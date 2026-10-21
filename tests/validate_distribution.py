#!/usr/bin/env python3
"""Prebuilt/source equivalence and adversarial verification with an external stock fixture."""
import argparse
import binascii
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from unittest.mock import patch
import zipfile

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from verify import verify_pair
from z8precapture.patcher import prebuilt_code
from z8prores.package import Package
from tools.check_release import check_release


def need(ok, message):
    if not ok:
        raise RuntimeError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--stock', type=Path, help='Official firmware, required unless --archive-only')
    ap.add_argument('--compiler', default='clang')
    ap.add_argument('--report', required=True, type=Path)
    ap.add_argument('--archive', type=Path)
    ap.add_argument('--archive-only', action='store_true')
    args = ap.parse_args()
    need(not args.report.exists(), 'Report already exists')
    need(args.archive if args.archive_only else args.stock, 'Provide --stock, or --archive and --archive-only')
    rows = []

    def reject(name, fn, reason):
        try:
            fn()
        except ValueError as error:
            need(reason in str(error), name + ': unexpected rejection ' + str(error))
            rows.append(dict(test=name, result='REJECTED'))
        else:
            raise RuntimeError('Negative control accepted: ' + name)

    with tempfile.TemporaryDirectory(prefix='z8-distribution-tests-') as folder:
        temp = Path(folder)
        if not args.archive_only:
            original = args.stock.read_bytes()
            need(sha(original) == 'd67413c2ede6b9ce8887175f20700bd9fbad2a973a4820968c45503d15d80d96', 'Wrong official fixture')
            compiler = shutil.which(args.compiler)
            need(compiler, 'Compiler unavailable for source equivalence test')
            # An empty PATH makes an accidental compiler subprocess fail in default mode.
            no_compiler = dict(os.environ, PATH='')
            variants = [('04.04', 'p0'), ('17.42', 'x7')]
            for version, tag in variants:
                for features in (['prores'], ['precapture'], ['prores', 'precapture']):
                    outputs = []
                    for mode in ('prebuilt', 'source'):
                        output = temp / (version + '-' + '+'.join(features) + '-' + mode)
                        command = [sys.executable, '-B', str(ROOT / 'patch.py'), str(args.stock.resolve()),
                                   '--features', *features, '--version', version, '--tag', tag, '--output', str(output)]
                        # Default must be prebuilt, without an explicit flag.
                        if mode == 'source':
                            command += ['--code-source', 'source', '--compiler', compiler]
                        run = subprocess.run(command, capture_output=True, text=True,
                                             env=no_compiler if mode == 'prebuilt' else None)
                        need(run.returncode == 0, run.stderr)
                        candidate = (output / ('Z_8_' + version.replace('.', '') + '.bin')).read_bytes()
                        record = verify_pair(original, candidate, features, expected_version=version, expected_tag=tag)
                        need(record['requested_identity_checked'] and record['requested_features_checked'], 'Expected options not checked')
                        manifest = json.loads((output / 'manifest.json').read_text())
                        need(manifest['output_sha256'] == sha(candidate), 'Wrong manifest digest')
                        if 'precapture' in features:
                            need(manifest['details']['precapture']['code_source'] == mode, 'Wrong code-source provenance')
                        outputs.append(candidate)
                    need(outputs[0] == outputs[1], 'Prebuilt and source output differ')
                    rows.append(dict(test='prebuilt/source: ' + '+'.join(features) + ' ' + version + '.' + tag,
                                     result='PASS', output_sha256=sha(candidate)))
                    print(rows[-1]['test'] + ': PASS', flush=True)
            # Last output: both features with custom version/tag.
            features = ['prores', 'precapture']
            reject('wrong requested version', lambda: verify_pair(original, candidate, features, expected_version='17.43', expected_tag='x7'), 'requested version/tag')
            reject('wrong requested tag', lambda: verify_pair(original, candidate, features, expected_version='17.42', expected_tag='x6'), 'requested version/tag')
            reject('tag without version', lambda: verify_pair(original, candidate, features, expected_tag='x7'), 'requires an expected version')
            reject('wrong selected feature', lambda: verify_pair(original, candidate, ['prores']), 'reviewed feature patch bytes')
            detected = verify_pair(original, candidate)
            need(detected['features'] == ['precapture', 'prores'] and not detected['requested_features_checked']
                 and not detected['requested_identity_checked'], 'Auto-detection misreported as expected-option verification')
            rows.append(dict(test='inferred options reported separately from explicitly checked options', result='PASS'))
            package = Package(original)
            patched_eg = Package(candidate).eg

            def changed(at, raw, module='eg2070_1742x7.bi'):
                eg = bytearray(patched_eg)
                eg[at:at + len(raw)] = raw
                eg[-2:] = binascii.crc_hqx(eg[:-2], 0).to_bytes(2, 'big')
                return package.replace_eg(bytes(eg), module)[0]

            reject('changed hook with repaired checksums', lambda: verify_pair(original, changed(0xe0fe90, b'\0' * 4), features), 'reviewed feature patch bytes')
            reject('changed code with repaired checksums', lambda: verify_pair(original, changed(0x800010, b'\xff' * 4), features), 'reviewed feature patch bytes')
            capture_profile = json.loads((ROOT/'resources/precapture.json').read_text())
            old_sites = {0xe0fe90,0xd4915c,0xd43638,0xd4eb60,0xe0ff38,0xee8e1c,0xd49fac,0xd4eeec,0xd4ef10,0x4d2ffc0,0x4d2ffcc,0x800000,0x1024d8c}
            for edit in capture_profile['patches']:
                at = int(edit['offset'], 16)
                if at in old_sites:
                    continue
                damaged = bytes([patched_eg[at] ^ 1])
                reject('changed HE-star / UI / callback patch '+edit['offset']+' with repaired checksums',
                       lambda at=at, damaged=damaged: verify_pair(original, changed(at, damaged), features),
                       'reviewed feature patch bytes')
            reject('wrong shared loader with repaired checksums', lambda: verify_pair(original, changed(0x1024d8c, b'\0' * 8), features), 'reviewed feature patch bytes')
            reject('unlisted byte with repaired checksums', lambda: verify_pair(original, changed(0x2400000, b'\x13\x27\x42\x91'), features), 'outside declared')
            reject('version instruction opcode changed', lambda: verify_pair(original, changed(0xeb29fc, b'\0' * 4), features), 'Version instruction shape')
            reject('trailer identity changed', lambda: verify_pair(original, changed(len(patched_eg)-11, b'17.43.x7'), features), 'Internal identity mismatch')
            reject('module identity changed', lambda: verify_pair(original, changed(0x800000, patched_eg[0x800000:0x800004], 'eg2070_1743x7.bi'), features), 'directory EG name mismatch')
            modified = bytearray(package.eg)
            modified[0x2400000:0x2400004] = b'\x13\x27\x42\x91'
            modified[-2:] = binascii.crc_hqx(modified[:-2], 0).to_bytes(2, 'big')
            modified_input = package.replace_eg(bytes(modified), 'eg2070_0311b0.bi')[0]
            reject('modified input with valid envelope', lambda: verify_pair(modified_input, candidate, features), 'official Nikon Z8 C 3.11 SHA-256')
            wrong_input = temp / 'modified.bin'
            wrong_input.write_bytes(modified_input)
            rejected_dir = temp / 'rejected'
            run = subprocess.run([sys.executable, '-O', str(ROOT/'patch.py'), str(wrong_input), '--features', *features,
                                  '--version', '04.04', '--output', str(rejected_dir)], capture_output=True, text=True)
            need(run.returncode != 0 and 'official Nikon Z8 C 3.11 SHA-256' in run.stderr and not rejected_dir.exists(),
                 'Modified input passed the public CLI or left output')
            rows.append(dict(test='public CLI enforces exact original under python -O before output creation', result='PASS'))
            # Isolated resources exercise the loader without changing the release under test.
            resources = temp / 'resources'
            resources.mkdir()
            shutil.copyfile(ROOT/'resources/precapture.json', resources/'precapture.json')
            with patch('z8precapture.patcher.RESOURCES', resources):
                reject('missing prebuilt has no fallback', prebuilt_code, 'Prebuilt pre-capture code is missing')
                (resources/'precapture.bin').write_bytes(b'\0')
                reject('truncated prebuilt', prebuilt_code, 'wrong size')
                code = bytearray((ROOT/'resources/precapture.bin').read_bytes())
                code[16] ^= 1
                (resources/'precapture.bin').write_bytes(code)
                reject('corrupt prebuilt', prebuilt_code, 'reviewed SHA-256')
            # Missing asset must abort the full CLI too, rather than silently compile.
            isolated = temp / 'missing-asset-toolkit'
            shutil.copytree(ROOT, isolated, ignore=shutil.ignore_patterns('.git', 'build', '*.bin', '__pycache__'))
            run = subprocess.run([sys.executable, '-B', str(isolated/'patch.py'), str(args.stock.resolve()),
                                  '--features', 'precapture', '--version', '04.04', '--output', str(rejected_dir)],
                                 capture_output=True, text=True)
            need(run.returncode != 0 and 'Prebuilt pre-capture code is missing' in run.stderr and not rejected_dir.exists(),
                 'Missing prebuilt did not stop the CLI before output')
            rows.append(dict(test='missing Release asset aborts CLI without output or fallback', result='PASS'))
            # A source checkout remains usable with an explicit source request.
            run = subprocess.run([sys.executable, '-B', str(isolated/'patch.py'), str(args.stock.resolve()),
                                  '--features', 'precapture', '--version', '04.04', '--code-source', 'source',
                                  '--compiler', compiler, '--output', str(temp/'source-checkout')], capture_output=True, text=True)
            need(run.returncode == 0, 'Source checkout requires a prebuilt asset: ' + run.stderr)
            rows.append(dict(test='explicit source mode works without prebuilt asset', result='PASS'))
            need(args.stock.read_bytes() == original, 'Input firmware changed')

        if args.archive:
            rows.append(dict(test='Release archive matches source and contains only allowed members', **check_release(args.archive)))
            with zipfile.ZipFile(args.archive) as archive:
                members = [(e, archive.read(e)) for e in archive.infolist()]
            bad_archive = temp / 'bad-release.zip'
            with zipfile.ZipFile(bad_archive, 'w') as archive:
                for info, raw in members:
                    archive.writestr(info, raw)
                archive.writestr(members[0][0].filename.split('/')[0] + '/Z_8_0311.bin', b'excluded firmware member')
            reject('Release rejects extra firmware member', lambda: check_release(bad_archive), 'allowlist mismatch')
            with zipfile.ZipFile(bad_archive, 'w') as archive:
                for info, raw in members:
                    if info.filename.endswith('/resources/precapture.bin'):
                        raw = bytes([raw[0] ^ 1]) + raw[1:]
                    archive.writestr(info, raw)
            reject('Release rejects damaged code asset', lambda: check_release(bad_archive), 'digest mismatch')
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(dict(status='PASS', tests=rows), indent=2) + '\n')
    print('PASS: ' + str(len(rows)) + ' distribution checks')


if __name__ == '__main__':
    main()
