#!/usr/bin/env python3
"""Patch a compatible Z8 3.11-derived update package with a ProRes quality menu."""
import argparse
import json
import os
from pathlib import Path
import sys

sys.dont_write_bytecode = True
from z8prores.package import Package, PACKAGE_BYTES, RESOURCES, require, sha
from z8prores.patcher import build, compatibility


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('firmware', type=Path, help='User-supplied complete Z8 firmware .bin')
    ap.add_argument('--check', action='store_true', help='Read-only input compatibility and integrity check')
    ap.add_argument('--version', help='Custom output public version NN.NN, e.g. 03.23 (choose higher than the installed camera)')
    ap.add_argument('--tag', default='u0', help='Internal revision suffix: lowercase letter plus digit; default u0')
    ap.add_argument('--output', type=Path, help='New output directory; must not already exist')
    a = ap.parse_args()
    if not a.check and (not a.version or not a.output):
        ap.error('Building requires --version and --output; use --check for read-only inspection')
    if a.check and (a.output or a.version or a.tag != 'u0'):
        ap.error('--check cannot be combined with output options')
    require(a.firmware.is_file(), 'Input must be a regular firmware file')
    require(a.firmware.stat().st_size == PACKAGE_BYTES, 'Unsupported firmware length')
    if not a.check:
        require(not a.output.exists(), 'Output directory already exists; use a new directory')
    data = a.firmware.read_bytes()
    package = Package(data)
    profile, identity = compatibility(package.eg)
    if a.check:
        print(json.dumps(dict(status='COMPATIBLE', input_sha256=package.sha256,
                              identity=identity, profile=profile['id'], modules=package.modules), indent=2))
        return
    eg, report = build(package.eg, a.version, a.tag)
    module_name = 'eg2070_' + a.version.replace('.', '') + a.tag + '.bi'
    packet, checked = package.replace_eg(eg, module_name)
    name = 'Z_8_' + a.version.replace('.', '') + '.bin'
    report.update(status='BUILT_AND_LOCALLY_VERIFIED', input_sha256=package.sha256,
                  input_filename=a.firmware.name, input_bytes=len(data), output_sha256=sha(packet),
                  output_bytes=len(packet), output_filename=name, output_eg_sha256=sha(eg),
                  input_modules=package.modules, output_modules=checked.modules,
                  source_hashes={str(p.relative_to(Path(__file__).resolve().parent)): sha(p.read_bytes())
                                 for p in [Path(__file__).resolve(), *sorted(Path(__file__).resolve().parent.glob('z8prores/*.py')),
                                           *sorted(RESOURCES.glob('*.json'))]},
                  scope='ProRes patch bytes verified; all other input EG bytes and all non-EG modules preserved; no camera install or recording test of this output')
    # Create only after validation. Exclusive creation never replaces input or an earlier build.
    # On I/O failure the directory is kept, without a successful manifest, for inspection.
    a.output.mkdir(parents=True, exist_ok=False)
    with (a.output / name).open('xb') as f:
        f.write(packet)
        f.flush()
        os.fsync(f.fileno())
    require(sha((a.output / name).read_bytes()) == report['output_sha256'], 'Output readback mismatch')
    require(sha(a.firmware.read_bytes()) == package.sha256, 'Input changed during build')
    with (a.output / 'SHA256SUMS.txt').open('x') as f:
        f.write(report['output_sha256'] + '  ' + name + '\n')
    with (a.output / 'manifest.json').open('x') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
        f.write('\n')
    print(json.dumps(dict(status=report['status'], output=str(a.output / name), sha256=report['output_sha256'],
                          input_identity=identity, output_identity=report['output_identity']), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, ImportError) as e:
        raise SystemExit('ERROR: ' + str(e))
