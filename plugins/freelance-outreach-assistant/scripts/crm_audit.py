from __future__ import annotations

import argparse
import datetime as dt
from pathlib import Path

from outreach_lib import audit_rows, load_csv, print_report


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit a freelance outreach CRM CSV.")
    parser.add_argument("crm", type=Path)
    parser.add_argument("--date", default=dt.date.today().isoformat(), help="Target date in YYYY-MM-DD format.")
    parser.add_argument("--strict", action="store_true", help="Exit 1 when critical issues are found.")
    args = parser.parse_args()

    target_date = dt.date.fromisoformat(args.date)
    rows, _ = load_csv(args.crm)
    report = audit_rows(rows, target_date)
    print_report(report)
    if args.strict and report["critical"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
