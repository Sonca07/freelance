---
name: lead-scoring
description: Score and prioritize freelance outreach leads from a CRM CSV. Use when Codex needs to rank businesses by fit for booking/reservation SPAs, normalize states, block opt-outs, or prepare leads for daily outreach.
---

# Lead Scoring

## Quick Start

Run the scoring script against a CRM CSV:

```powershell
python plugins\freelance-outreach-assistant\scripts\score_leads.py crm\leads.csv crm\leads_scored.csv
```

The script keeps the CRM schema from `../../references/crm-schema.md`, fills `score`, normalizes known states, and assigns `0` to blocked leads.

## Scoring Intent

Prioritize appointment-heavy businesses with public email, public source, identifiable booking pain, and local context. Strong initial rubros are estetica, barberia, fitness/pilates/yoga, and consultorios chicos.

Never override `baja=si`, `No contactar`, `Ganado`, or `Perdido` to make a lead eligible.

## Review

After scoring, inspect the top leads and explain why they rank highly before drafting emails.
