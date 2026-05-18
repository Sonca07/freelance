from __future__ import annotations

import argparse
import csv
import datetime as dt
import sys
from pathlib import Path

from outreach_lib import due_actions, load_csv


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare a daily outreach action list.")
    parser.add_argument("crm", type=Path)
    parser.add_argument("--date", default=dt.date.today().isoformat(), help="Target date in YYYY-MM-DD format.")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--output", type=Path, help="Optional CSV output path.")
    args = parser.parse_args()

    target_date = dt.date.fromisoformat(args.date)
    rows, _ = load_csv(args.crm)
    actions = due_actions(rows, target_date, args.limit)
    fields = ["lead_id", "negocio", "rubro", "barrio", "email", "score", "estado", "action_sequence", "computed_followup"]

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            writer.writerows({field: row.get(field, "") for field in fields} for row in actions)
        print(f"Wrote {len(actions)} actions -> {args.output}")
        return 0

    writer = csv.DictWriter(sys.stdout, fieldnames=fields)
    writer.writeheader()
    writer.writerows({field: row.get(field, "") for field in fields} for row in actions)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
