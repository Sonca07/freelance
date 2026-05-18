from __future__ import annotations

import argparse
from pathlib import Path

from outreach_lib import apply_scores, load_csv, write_csv


def main() -> int:
    parser = argparse.ArgumentParser(description="Score freelance outreach CRM leads.")
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    rows, fieldnames = load_csv(args.input)
    scored = apply_scores(rows)
    write_csv(args.output, scored, fieldnames)
    print(f"Scored {len(scored)} leads -> {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
