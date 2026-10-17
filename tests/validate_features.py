#!/usr/bin/env python3
"""Feature-composition regression and rejection tests with an external stock fixture."""
import argparse
import binascii
import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import zlib

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from features import compatibility, selected_features
from z8prores.package import Package, sha
from z8precapture.config import build_config
from verify import verify_pair


def check(ok, message):
    if not ok:
        raise RuntimeError(message)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--stock', required=True, type=Path)
    ap.add_argument('--report', type=Path, required=True)
    ap.add_argument('--compiler', default='clang')
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
                   '--version', '04.01', '--output', str(out), '--compiler', a.compiler]
            pr = subprocess.run(cmd, capture_output=True, text=True)
            check(pr.returncode == 0, pr.stderr)
            candidate = (out/'Z_8_0401.bin').read_bytes()
            verified = verify_pair(data, candidate, names)
            auto = verify_pair(data, candidate)
            check(set(auto['features']) == set(names), 'Feature detection differs')
            manifest = json.loads((out/'manifest.json').read_text())
            check(manifest['features'] == names and manifest['output_sha256'] == sha(candidate), 'Manifest mismatch')
            cpath = out/'Z8PRE.CFG'
            check(cpath.exists() == ('precapture' in names), 'Unexpected card configuration')
            if cpath.exists():
                c = cpath.read_bytes()
                check(len(c) == 64 and c[:16] == b'Z8PRECFGv2'.ljust(16, b'\0'), 'Configuration format')
                check(struct.unpack_from('<4I', c, 16) == (0x13,30,1500000,0), 'Default configuration values')
                check(zlib.crc32(c[:60]) == struct.unpack_from('<I', c, 60)[0], 'Configuration CRC')
            rows.append(dict(test=name, result='PASS', output_sha256=sha(candidate), independently_verified=verified['status']))
            print(name + ': PASS', flush=True)
            reject(name+' repeated patch', lambda names=names: compatibility(Package(candidate).eg, names), 'Incompatible')
            wrong = ['precapture'] if names == ['prores'] else ['prores']
            reject(name+' wrong feature claim', lambda: verify_pair(data, candidate, wrong), 'Output differs')
            repeated = subprocess.run(cmd, capture_output=True, text=True)
            check(repeated.returncode != 0 and 'already exists' in repeated.stderr and
                  (out/'Z_8_0401.bin').read_bytes() == candidate, 'Existing output changed')
        # Reject validly checksummed changes to required code and occupied patch space.
        for offset in [0xe0fe90,0xd4915c,0xd43638,0xd4367c,0xd4eb60,0x56c134,0x7002cc,0x7148a8,0x715834,0x4cf4fd0,0x800000,0x4d2ffc0,0x17aa4c]:
            bad = bytearray(package.eg); bad[offset] ^= 1
            bad[-2:] = binascii.crc_hqx(bad[:-2],0).to_bytes(2,'big')
            reject(f'conflicting input {offset:#x}', lambda bad=bad: compatibility(bytes(bad),['precapture']), 'Incompatible')
        bad = bytearray(Package(candidate).eg); bad[0x2400000] ^= 1
        bad[-2:] = binascii.crc_hqx(bad[:-2],0).to_bytes(2,'big')
        packet,_ = package.replace_eg(bytes(bad),'eg2070_0401p0.bi')
        reject('repaired checksums do not hide unrelated edits',lambda:verify_pair(data,packet,['prores','precapture']), 'outside declared')
        # Build from a layout-compatible input with an unrelated sentinel; preserve it exactly.
        source = bytearray(package.eg); source[0x2400000:0x2400004] = b'\x13\x27\x42\x91'
        source[-2:] = binascii.crc_hqx(source[:-2],0).to_bytes(2,'big')
        from features import build
        output,_ = build(bytes(source),'04.02','p0',['prores','precapture'],a.compiler)
        check(output[0x2400000:0x2400004] == source[0x2400000:0x2400004], 'Unselected bytes changed')
        rows.append(dict(test='unselected input bytes preserved',result='PASS'))
        # Optimized Python must not disable the input guards.
        bad = bytearray(package.eg); bad[0x800000] ^= 1
        bad[-2:] = binascii.crc_hqx(bad[:-2],0).to_bytes(2,'big')
        packet,_ = package.replace_eg(bytes(bad),'eg2070_0311b0.bi')
        input_path = temp/'bad.bin'; input_path.write_bytes(packet)
        out = temp/'optimized-rejected'
        pr = subprocess.run([sys.executable,'-O',str(ROOT/'patch.py'),str(input_path),'--features','precapture',
                             '--version','04.01','--output',str(out)],capture_output=True,text=True)
        check(pr.returncode != 0 and not out.exists(), 'python -O disabled the compatibility guard')
        rows.append(dict(test='optimized Python rejects incompatible input without output',result='PASS'))
    # Exercise the user-facing configuration command and reject options that cannot apply.
    with tempfile.TemporaryDirectory(prefix='z8-config-tests-') as temporary:
        temp = Path(temporary)
        for mode in ('raw-jpeg', 'raw-only'):
            out = temp/mode
            cmd = [sys.executable, '-B', str(ROOT/'configure.py'), '--capture-mode', mode,
                   '--frames', '5', '--c15-only', '--diagnostic-footer', '--output', str(out)]
            pr = subprocess.run(cmd, capture_output=True, text=True)
            check(pr.returncode == 0, pr.stderr)
            expected = build_config(5, False, True, mode)
            check((out/'Z8PRE.CFG').read_bytes() == expected, 'Configuration CLI differs')
            pr = subprocess.run(cmd, capture_output=True, text=True)
            check(pr.returncode != 0 and (out/'Z8PRE.CFG').read_bytes() == expected, 'Existing configuration overwritten')
            rows.append(dict(test=mode+' configuration CLI and overwrite refusal', result='PASS'))
        for opts in (['--features','prores','--capture-mode','raw-only','--version','04.02'],
                     ['--features','precapture','--capture-mode','raw-only','--check']):
            cmd = [sys.executable, '-B', str(ROOT/'patch.py'), str(a.stock.resolve()), *opts]
            if '--check' not in opts: cmd += ['--output', str(temp/'rejected')]
            pr = subprocess.run(cmd,capture_output=True,text=True)
            check(pr.returncode != 0 and not (temp/'rejected').exists(), 'Inapplicable configuration option accepted')
        rows.append(dict(test='capture mode requires a pre-capture build', result='PASS'))
    for mode, flags in [('raw-jpeg', 0x13), ('raw-only', 0x77)]:
        c = build_config(capture_mode=mode)
        check(struct.unpack_from('<I', c, 16)[0] == flags, 'Mode flags differ')
        check(zlib.crc32(c[:60]) == struct.unpack_from('<I', c, 60)[0], 'Mode CRC differs')
        c = build_config(5, False, True, mode)
        check(struct.unpack_from('<I', c, 16)[0] == (flags & ~2) | 8, 'C15 diagnostic flags differ')
        rows.append(dict(test=mode+' configuration', result='PASS'))
    reject('unsupported capture mode', lambda:build_config(capture_mode='unknown'), 'Capture mode')
    for selection in [[],['unknown'],['prores','prores']]:
        reject('invalid feature selection '+str(selection),lambda selection=selection:selected_features(selection),'Select')
    for frames in [0,31]:
        reject('invalid frame limit '+str(frames),lambda frames=frames:build_config(frames),'Frames')
    check(a.stock.read_bytes() == data, 'Input firmware modified')
    a.report.parent.mkdir(parents=True,exist_ok=True)
    a.report.write_text(json.dumps(dict(status='PASS',tests=rows),indent=2)+'\n')
    print('PASS: ' + str(len(rows)) + ' feature and rejection checks')


if __name__ == '__main__':
    main()
