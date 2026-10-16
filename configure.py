#!/usr/bin/env python3
"""Generate a pre-capture configuration locally, for manual copying to one card."""
import argparse
import json
from pathlib import Path
from z8precapture.config import CONFIG_NAME, build_config
from z8prores.package import require, sha


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', type=Path, required=True, help='New local output directory')
    ap.add_argument('--frames', type=int, default=30, help='Maximum historical frames, 1..30; default 30')
    ap.add_argument('--c15-only', action='store_true', help='Do not enable C30')
    ap.add_argument('--diagnostic-footer', action='store_true', help='Append optional timing data to each NEF')
    a = ap.parse_args()
    raw = build_config(a.frames, not a.c15_only, a.diagnostic_footer)
    require(not a.output.exists(), 'Output directory already exists')
    a.output.mkdir(parents=True, exist_ok=False)
    with (a.output / CONFIG_NAME).open('xb') as f:
        f.write(raw)
    print(json.dumps(dict(file=str(a.output / CONFIG_NAME), sha256=sha(raw), frames=a.frames,
                          c30=not a.c15_only, diagnostic_footer=a.diagnostic_footer), indent=2))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError) as exc:
        raise SystemExit('ERROR: ' + str(exc))
