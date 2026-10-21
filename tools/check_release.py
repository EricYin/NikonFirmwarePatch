#!/usr/bin/env python3
"""Independently check a toolkit ZIP against this source checkout, without compiling."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import zipfile

ROOT = Path(__file__).resolve().parents[1]
# Deliberate distribution allowlist. Full firmware, photos and runtimes have no entry.
SOURCE_FILES = (
    '.gitattributes', '.githooks/pre-commit', '.gitignore', 'LICENSE', 'NOTICE.md', 'README.md',
    'features.py', 'patch.py', 'verify.py', 'requirements.txt',
    'docs/images/prores-quality-options.png', 'docs/images/prores-quality-value.png',
    'docs/raw-precapture.md', 'docs/validation.md', 'docs/validation-summary.json', 'docs/validation-implementation-v3.json',
    'docs/validation-v0.1.0.json',
    'docs/releases.md', 'resources/input.json', 'resources/precapture.json', 'resources/profile.json',
    'tests/validate.py', 'tests/validate_features.py', 'tests/validate_distribution.py',
    'tools/check_repository.py', 'tools/build_release.py', 'tools/check_release.py',
    'z8precapture/__init__.py', 'z8precapture/crc32_table.inc',
    'z8precapture/firmware.c', 'z8precapture/linker.py', 'z8precapture/patcher.py',
    'z8prores/__init__.py', 'z8prores/a64.py', 'z8prores/back_half.py', 'z8prores/layout.py',
    'z8prores/menu.py', 'z8prores/package.py', 'z8prores/patcher.py',
)
CODE_FILE = 'resources/precapture.bin'
MANIFEST = 'release-manifest.json'


def need(ok, message):
    if not ok:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def check_release(path, expected_commit=None):
    need(path.stat().st_size <= 4 * 1024 * 1024, 'Toolkit archive exceeds the size limit')
    with zipfile.ZipFile(path) as archive:
        entries = archive.infolist()
        names = [e.filename for e in entries]
        need(names and len(names) == len(set(names)), 'Duplicate or missing ZIP members')
        prefix = names[0].split('/')[0]
        need(re.fullmatch(r'NikonFirmwarePatch-v[0-9]+\.[0-9]+\.[0-9]+', prefix), 'Unexpected toolkit folder')
        wanted = {prefix + '/' + n for n in (*SOURCE_FILES, CODE_FILE, MANIFEST)}
        need(set(names) == wanted, 'Release member allowlist mismatch')
        need(sum(e.file_size for e in entries) <= 4 * 1024 * 1024, 'Expanded toolkit exceeds the size limit')
        need(all((e.external_attr >> 16) & 0o170000 == 0o100000 for e in entries), 'Non-regular ZIP member')
        files = {n: archive.read(prefix + '/' + n) for n in (*SOURCE_FILES, CODE_FILE)}
        record = json.loads(archive.read(prefix + '/' + MANIFEST))
    need(record['schema'] == 1 and record['tag'] == prefix.removeprefix('NikonFirmwarePatch-'), 'Release identity mismatch')
    need(re.fullmatch(r'[0-9a-f]{40}', record['source_commit']), 'Invalid source commit')
    need(expected_commit is None or record['source_commit'] == expected_commit, 'Unexpected source commit')
    need(set(record['files']) == set(files), 'Manifest member mismatch')
    for name, raw in files.items():
        need(record['files'][name] == {'bytes': len(raw), 'sha256': digest(raw)}, 'Member digest mismatch: ' + name)
    for name in SOURCE_FILES:
        need(files[name] == (ROOT / name).read_bytes(), 'Source differs from this checkout: ' + name)
    profile = json.loads((ROOT / 'resources/precapture.json').read_text())
    code = files[CODE_FILE]
    need(len(code) == profile['code_bytes'] and digest(code) == profile['code_sha256'], 'Unreviewed machine code')
    need(record['precapture_profile'] == profile['id'], 'Profile identity mismatch')
    need(record['compiler'] == profile['compiler'] and record['compiler_flags'] == profile['compiler_flags'],
         'Compiler provenance differs from the reviewed release recipe')
    return dict(status='PASS', tag=record['tag'], source_commit=record['source_commit'],
                source_files=len(SOURCE_FILES), binary_files=[CODE_FILE], code_bytes=len(code),
                code_sha256=digest(code), archive_sha256=digest(path.read_bytes()),
                firmware_included=False, scope='Archive contents, source identity and pinned patch bytes')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('archive', type=Path)
    ap.add_argument('--commit', help='Expected full source commit SHA')
    args = ap.parse_args()
    print(json.dumps(check_release(args.archive, args.commit), indent=2))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, KeyError, zipfile.BadZipFile) as error:
        raise SystemExit('ERROR: ' + str(error))
