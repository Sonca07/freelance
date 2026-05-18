from __future__ import annotations

import datetime as dt
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "plugins" / "freelance-outreach-assistant" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from outreach_lib import apply_scores, due_actions, load_config, load_csv, write_drafts  # noqa: E402


class OutreachScriptsTest(unittest.TestCase):
    def setUp(self) -> None:
        self.sample = ROOT / "crm" / "leads_sample.csv"
        self.rows, _ = load_csv(self.sample)

    def test_scoring_blocks_baja(self) -> None:
        scored = apply_scores(self.rows)
        blocked = [row for row in scored if row["lead_id"] == "L-0005"][0]
        self.assertEqual(blocked["score"], "0")

    def test_due_actions_skip_baja(self) -> None:
        actions = due_actions(self.rows, dt.date(2026, 5, 18), limit=10)
        ids = {row["lead_id"] for row in actions}
        self.assertNotIn("L-0005", ids)
        self.assertIn("L-0001", ids)

    def test_drafts_are_files_only(self) -> None:
        actions = due_actions(self.rows, dt.date(2026, 5, 18), limit=2)
        config = load_config(ROOT / "crm" / "outreach_config.example.json")
        with tempfile.TemporaryDirectory() as temp_dir:
            index = write_drafts(actions, Path(temp_dir), config)
            self.assertTrue(index.exists())
            self.assertGreater(len(list(Path(temp_dir).glob("*.txt"))), 0)
            self.assertGreater(len(list(Path(temp_dir).glob("*.eml"))), 0)


if __name__ == "__main__":
    unittest.main()
