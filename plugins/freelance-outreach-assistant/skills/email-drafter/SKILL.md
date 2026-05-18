---
name: email-drafter
description: Draft safe first-contact and follow-up emails for freelance outreach leads. Use when Codex needs to create personalized email copy, subject lines, follow-up sequences, or review outreach messages for booking/reservation SPA offers.
---

# Email Drafter

## Guardrails

- Draft only. Do not send.
- Use honest subject lines; never imply prior conversation unless `estado` confirms one.
- Include one concrete reference to the business or public source.
- Link to a demo; do not attach files.
- Include the configured opt-out line.
- Never draft for `baja=si`, `No contactar`, `Ganado`, or `Perdido`.

## Generate Drafts

Use:

```powershell
python plugins\freelance-outreach-assistant\scripts\draft_emails.py crm\leads_scored.csv --config crm\outreach_config.example.json --output-dir outputs\drafts --limit 10
```

Outputs are `.txt`, `.eml`, and `drafts_index.csv`. The script prints `No email was sent.`

## Sequence Mapping

- `Calificado` or `Borrador creado`: first-contact email.
- `Enviado`: first follow-up after 3 business days.
- `Follow-up 1`: final follow-up after 7 business days.

## Review

Before presenting drafts, summarize count, sequence type, and any blocked leads skipped.
