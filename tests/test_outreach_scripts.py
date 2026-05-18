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
from research_urls import build_lead, is_blocked_platform  # noqa: E402


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

    def test_barber_ola0_blocks_no_contact(self) -> None:
        rows, _ = load_csv(ROOT / "crm" / "barberias_ola0_ficticio.csv")
        actions = due_actions(rows, dt.date(2026, 5, 18), limit=10)
        ids = {row["lead_id"] for row in actions}
        self.assertEqual(len(actions), 4)
        self.assertNotIn("B-0005", ids)
        self.assertIn("B-0001", ids)

    def test_drafts_are_files_only(self) -> None:
        actions = due_actions(self.rows, dt.date(2026, 5, 18), limit=2)
        config = load_config(ROOT / "crm" / "outreach_config.example.json")
        with tempfile.TemporaryDirectory() as temp_dir:
            index = write_drafts(actions, Path(temp_dir), config)
            self.assertTrue(index.exists())
            self.assertGreater(len(list(Path(temp_dir).glob("*.txt"))), 0)
            self.assertGreater(len(list(Path(temp_dir).glob("*.eml"))), 0)

    def test_research_blocks_sensitive_platforms(self) -> None:
        self.assertTrue(is_blocked_platform("https://www.instagram.com/barberia-demo"))
        self.assertTrue(is_blocked_platform("https://www.google.com/maps/place/barberia-demo"))
        self.assertFalse(is_blocked_platform("https://barberia-demo.example/contacto"))

    def test_research_extracts_public_email_from_html(self) -> None:
        html = """
        <html>
          <head><title>Corte Norte Barber | Turnos</title></head>
          <body>
            <p>Barberia en Belgrano. Turnos por WhatsApp.</p>
            <a href="mailto:hola@cortenorte.example">Contacto</a>
          </body>
        </html>
        """
        lead, reason = build_lead(
            {
                "seed_id": "T-0001",
                "url": "https://cortenorte.example",
                "rubro": "barberia",
            },
            html,
            "https://cortenorte.example",
        )
        self.assertIsNone(reason)
        self.assertIsNotNone(lead)
        self.assertEqual(lead["email"], "hola@cortenorte.example")
        self.assertEqual(lead["negocio"], "Corte Norte Barber")
        self.assertEqual(lead["barrio"], "Belgrano")
        self.assertIn("WhatsApp", lead["dolor_detectado"])


if __name__ == "__main__":
    unittest.main()
