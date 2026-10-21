#!/usr/bin/env python3
"""Feature-composition regression and rejection tests with an external stock fixture."""
import argparse
import binascii
import json
from pathlib import Path
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from features import compatibility, selected_features
from z8prores.package import Package, sha
from verify import verify_pair


def check(ok, message):
    if not ok:
        raise RuntimeError(message)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--stock', required=True, type=Path)
    ap.add_argument('--report', type=Path, required=True)
    ap.add_argument('--compiler', default='clang')
    ap.add_argument('--code-source', choices=['prebuilt', 'source'], default='prebuilt')
    a = ap.parse_args()
    check(not a.report.exists(), 'Report already exists')
    data = a.stock.read_bytes()
    check(sha(data) == 'd67413c2ede6b9ce8887175f20700bd9fbad2a973a4820968c45503d15d80d96', 'Expected original 3.11 fixture')
    package = Package(data)
    rows = []

    def reject(name, fn, reason):
        try:
            fn()
        except ValueError as exc:
            check(reason in str(exc), name + ': unexpected error ' + str(exc))
            rows.append(dict(test=name, result='REJECTED'))
        else:
            raise RuntimeError('Negative control accepted: ' + name)

    with tempfile.TemporaryDirectory(prefix='z8-feature-tests-') as temporary:
        temp = Path(temporary)
        for names in [['prores'], ['precapture'], ['prores', 'precapture']]:
            name = '+'.join(names)
            out = temp/name
            cmd = [sys.executable, '-B', str(ROOT/'patch.py'), str(a.stock.resolve()), '--features', *names,
                   '--version', '04.04', '--output', str(out), '--code-source', a.code_source]
            if a.code_source == 'source':
                cmd += ['--compiler', a.compiler]
            pr = subprocess.run(cmd, capture_output=True, text=True)
            check(pr.returncode == 0, pr.stderr)
            candidate = (out/'Z_8_0404.bin').read_bytes()
            verified = verify_pair(data, candidate, names)
            auto = verify_pair(data, candidate)
            check(set(auto['features']) == set(names), 'Feature detection differs')
            manifest = json.loads((out/'manifest.json').read_text())
            check(manifest['features'] == names and manifest['output_sha256'] == sha(candidate), 'Manifest mismatch')
            check({x.name for x in out.iterdir()} == {'Z_8_0404.bin', 'manifest.json', 'SHA256SUMS.txt'},
                  'Build left an unexpected file, including a legacy card configuration')
            if 'precapture' in names:
                check(manifest['capture_control']['configuration_required'] is False and
                      manifest['capture_control']['diagnostic_footer'] is False and
                      manifest['capture_control']['raw_compression'] == ['HE', 'HE-star'], 'Capture control description')
            rows.append(dict(test=name, result='PASS', output_sha256=sha(candidate), independently_verified=verified['status']))
            print(name + ': PASS', flush=True)
            reject(name+' repeated patch', lambda names=names: compatibility(Package(candidate).eg, names), 'Incompatible')
            wrong = ['precapture'] if names == ['prores'] else ['prores']
            reject(name+' wrong feature claim', lambda: verify_pair(data, candidate, wrong), 'Output differs')
            repeated = subprocess.run(cmd, capture_output=True, text=True)
            check(repeated.returncode != 0 and 'already exists' in repeated.stderr and
                  (out/'Z_8_0404.bin').read_bytes() == candidate, 'Existing output changed')
        # Reject validly checksummed changes to required code and occupied patch space.
        capture_profile = json.loads((ROOT/'resources/precapture.json').read_text())
        for offset in sorted({int(e['offset'], 16) for e in capture_profile['patches']} |
                             {0x47add4,0x3ec44c8,0xd4367c,0x56c134,0x7002cc,0x7148a8,0x715834,0x4cf4fd0,0x17aa4c,0x55a3e0,0x710284}):
            bad = bytearray(package.eg); bad[offset] ^= 1
            bad[-2:] = binascii.crc_hqx(bad[:-2],0).to_bytes(2,'big')
            reason = 'Pre-capture patch input conflicts' if offset == 0x1024d8c else 'Incompatible'
            reject(f'conflicting input {offset:#x}', lambda bad=bad: compatibility(bytes(bad),['precapture']), reason)
        bad = bytearray(Package(candidate).eg); bad[0x2400000] ^= 1
        bad[-2:] = binascii.crc_hqx(bad[:-2],0).to_bytes(2,'big')
        packet,_ = package.replace_eg(bytes(bad),'eg2070_0404p0.bi')
        reject('repaired checksums do not hide unrelated edits',lambda:verify_pair(data,packet,['prores','precapture']), 'outside declared')
        # Build from a layout-compatible input with an unrelated sentinel; preserve it exactly.
        source = bytearray(package.eg); source[0x2400000:0x2400004] = b'\x13\x27\x42\x91'
        source[-2:] = binascii.crc_hqx(source[:-2],0).to_bytes(2,'big')
        from features import build
        output,_ = build(bytes(source),'04.05','p0',['prores','precapture'],a.compiler,a.code_source)
        check(output[0x2400000:0x2400004] == source[0x2400000:0x2400004], 'Unselected bytes changed')
        rows.append(dict(test='unselected input bytes preserved',result='PASS'))
        # Optimized Python must not disable the input guards.
        bad = bytearray(package.eg); bad[0x800000] ^= 1
        bad[-2:] = binascii.crc_hqx(bad[:-2],0).to_bytes(2,'big')
        packet,_ = package.replace_eg(bytes(bad),'eg2070_0311b0.bi')
        input_path = temp/'bad.bin'; input_path.write_bytes(packet)
        out = temp/'optimized-rejected'
        pr = subprocess.run([sys.executable,'-O',str(ROOT/'patch.py'),str(input_path),'--features','precapture',
                             '--version','04.04','--output',str(out)],capture_output=True,text=True)
        check(pr.returncode != 0 and not out.exists(), 'python -O disabled the compatibility guard')
        rows.append(dict(test='optimized Python rejects incompatible input without output',result='PASS'))
    # The menu-driven build has no CFG-generation step. Reject old configuration switches explicitly.
    with tempfile.TemporaryDirectory(prefix='z8-obsolete-options-') as temporary:
        rejected = Path(temporary)/'rejected'
        for options in (['--capture-mode','raw-jpeg'],['--capture-mode','raw-only'],['--frames','5'],['--c15-only'],['--diagnostic-footer']):
            pr = subprocess.run([sys.executable,'-B',str(ROOT/'patch.py'),str(a.stock.resolve()),
                                 '--features','precapture','--version','04.04','--output',str(rejected),*options],
                                capture_output=True,text=True)
            check(pr.returncode != 0 and not rejected.exists(), 'Obsolete configuration option accepted')
            rows.append(dict(test='obsolete configuration option rejected: '+' '.join(options), result='PASS'))
    for selection in [[],['unknown'],['prores','prores']]:
        reject('invalid feature selection '+str(selection),lambda selection=selection:selected_features(selection),'Select')
    check(a.stock.read_bytes() == data, 'Input firmware modified')
    a.report.parent.mkdir(parents=True,exist_ok=True)
    a.report.write_text(json.dumps(dict(status='PASS',tests=rows),indent=2)+'\n')
    print('PASS: ' + str(len(rows)) + ' feature and rejection checks')


if __name__ == '__main__':
    main()
