from __future__ import annotations

import argparse
import datetime as dt
from pathlib import Path

from outreach_lib import due_actions, load_config, load_csv, write_drafts


def main() -> int:
    parser = argparse.ArgumentParser(description="Create safe email draft files without sending anything.")
    parser.add_argument("crm", type=Path)
    parser.add_argument("--config", type=Path, default=Path("crm/outreach_config.example.json"))
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/drafts"))
    parser.add_argument("--date", default=dt.date.today().isoformat(), help="Target date in YYYY-MM-DD format.")
    parser.add_argument("--limit", type=int, default=10)
    args = parser.parse_args()

    target_date = dt.date.fromisoformat(args.date)
    rows, _ = load_csv(args.crm)
    actions = due_actions(rows, target_date, args.limit)
    config = load_config(args.config)
    index_path = write_drafts(actions, args.output_dir, config)
    print(f"Created {len(actions)} draft sets -> {args.output_dir}")
    print(f"Index -> {index_path}")
    print("No email was sent.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
