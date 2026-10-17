#!/usr/bin/env python3
"""Package committed source and reviewed original patch code; never reads a firmware file."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.check_release import SOURCE_FILES, CODE_FILE, MANIFEST, check_release
from z8precapture.patcher import compile_code


def need(ok, message):
    if not ok:
        raise ValueError(message)


def git(*args):
    return subprocess.check_output(['git', '-C', str(ROOT), *args])


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--tag', required=True, help='Toolkit release vMAJOR.MINOR.PATCH, unrelated to camera version')
    ap.add_argument('--compiler', default='clang')
    ap.add_argument('--output', required=True, type=Path, help='New release asset directory')
    args = ap.parse_args()
    need(re.fullmatch(r'v[0-9]+\.[0-9]+\.[0-9]+', args.tag), 'Invalid release tag')
    need(not args.output.exists(), 'Output directory already exists')
    need(not git('status', '--porcelain', '--untracked-files=normal').strip(), 'Commit source changes before packaging')
    commit = git('rev-parse', 'HEAD').decode().strip()
    names = set(git('ls-tree', '-r', '--name-only', 'HEAD').decode().splitlines())
    need(names == set(SOURCE_FILES), 'Tracked source differs from the release allowlist')
    subprocess.run([sys.executable, '-B', str(ROOT / 'tools/check_repository.py'), '--all'], cwd=ROOT, check=True)
    files = {name: git('show', f'HEAD:{name}') for name in SOURCE_FILES}
    need(all(raw == (ROOT / name).read_bytes() for name, raw in files.items()), 'Working tree differs from committed source')
    code, detail = compile_code(args.compiler)
    profile = json.loads(files['resources/precapture.json'])
    need(detail['compiler'] == profile['compiler'], 'Release must use the recorded compiler version')
    files[CODE_FILE] = code
    record = dict(schema=1, tag=args.tag, source_commit=commit, precapture_profile=profile['id'],
                  compiler=detail['compiler'], compiler_flags=profile['compiler_flags'],
                  files={name: dict(bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest()) for name, raw in sorted(files.items())})
    files[MANIFEST] = (json.dumps(record, indent=2) + '\n').encode()
    args.output.mkdir(parents=True, exist_ok=False)
    prefix = 'NikonFirmwarePatch-' + args.tag
    archive_path = args.output / (prefix + '-toolkit.zip')
    # Fixed timestamps and modes make repeated packaging reproducible.
    with zipfile.ZipFile(archive_path, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, raw in sorted(files.items()):
            entry = zipfile.ZipInfo(prefix + '/' + name, date_time=(2026, 1, 1, 0, 0, 0))
            entry.create_system = 3
            entry.external_attr = 0o100644 << 16
            entry.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(entry, raw)
    verified = check_release(archive_path, commit)
    with (args.output / 'SHA256SUMS.txt').open('x') as stream:
        stream.write(verified['archive_sha256'] + '  ' + archive_path.name + '\n')
    print(json.dumps(verified, indent=2))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        raise SystemExit('ERROR: ' + str(error))
