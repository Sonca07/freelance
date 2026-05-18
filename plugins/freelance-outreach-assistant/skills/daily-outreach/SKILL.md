---
name: daily-outreach
description: Build a daily safe outreach queue for the freelance lead pipeline. Use when Codex needs to select today's leads, enforce wave limits, prepare follow-ups, or generate approved-send batches from the CRM.
---

# Daily Outreach

## Daily Run

Use this order:

```powershell
python plugins\freelance-outreach-assistant\scripts\crm_audit.py crm\leads.csv
python plugins\freelance-outreach-assistant\scripts\score_leads.py crm\leads.csv crm\leads_scored.csv
python plugins\freelance-outreach-assistant\scripts\next_actions.py crm\leads_scored.csv --limit 10 --output outputs\daily_actions.csv
python plugins\freelance-outreach-assistant\scripts\draft_emails.py crm\leads_scored.csv --limit 10 --output-dir outputs\drafts
```

## Limits

- Wave 1: 30 leads total, max 10/day.
- Wave 2: 70 leads total, max 15/day only if bounce/spam problems are absent.
- Lower limits when the Gmail account is new or warming up.

## Output

Return the selected leads, sequence type, and draft folder. Remind the user that messages still need manual approval and sending.

## Stop Conditions

If 30 sends produce fewer than 2 responses, stop scaling and revise niche, demo, subject, or offer before preparing wave 2.
