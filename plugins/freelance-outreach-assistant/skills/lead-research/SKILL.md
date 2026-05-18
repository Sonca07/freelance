---
name: lead-research
description: Research and qualify public business leads for a local freelance outreach pipeline. Use when Codex needs to find AMBA or local businesses, collect public emails, identify reservation or turn-taking pain signals, and produce CRM-ready lead rows for SPAs, landing pages, booking systems, or similar freelance offers.
---

# Lead Research

## Workflow

Research only public business information and produce rows that match `../../references/crm-schema.md`. Use web search when current market facts, business listings, or public contact details are needed.

1. Define the rubro and geography before collecting leads. Default to AMBA and appointment-heavy businesses: estetica, barberia, fitness/pilates/yoga, consultorios chicos.
2. Collect only public business contact data: official website, Google profile, public directory, or public social profile.
3. Record the exact public source in `fuente_publica`; do not use purchased databases or private contact data.
4. Identify one concrete `dolor_detectado`, such as WhatsApp-only booking, no visible horarios, no online reservation, or unclear contact flow.
5. Write rows to a CRM CSV, then run:

```powershell
python plugins\freelance-outreach-assistant\scripts\research_urls.py crm\lead_research_seeds_sample.csv --output outputs\researched_leads.csv --review-output outputs\research_review.csv
python plugins\freelance-outreach-assistant\scripts\normalize_leads.py crm\leads.csv crm\leads_normalized.csv
python plugins\freelance-outreach-assistant\scripts\score_leads.py crm\leads_normalized.csv crm\leads_scored.csv
```

`research_urls.py` must not fetch Instagram, Facebook, Google Maps, TikTok, or LinkedIn URLs automatically. It should queue those rows for manual review unless the user has already copied a public business email into the seed CSV.

## Lead Quality Rules

- Prefer businesses where bookings are visibly handled by WhatsApp, DM, phone, or unclear forms.
- Prefer businesses with active social/web presence but weak conversion flow.
- Skip leads with no public email unless the user explicitly wants a separate form/contact workflow.
- If a business asks not to be contacted, set `baja=si` and `estado=No contactar`.

## Output

Return a compact summary plus CRM-ready CSV rows. Keep any uncertainty in `notas`; do not invent contact details.
