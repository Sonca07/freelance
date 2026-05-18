from __future__ import annotations

import argparse
from pathlib import Path

from outreach_lib import load_csv, normalize_rows, write_csv


def main() -> int:
    parser = argparse.ArgumentParser(description="Normalize freelance outreach CRM leads.")
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    rows, fieldnames = load_csv(args.input)
    normalized = normalize_rows(rows)
    write_csv(args.output, normalized, fieldnames)
    print(f"Normalized {len(normalized)} leads -> {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
