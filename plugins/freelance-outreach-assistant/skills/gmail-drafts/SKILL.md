---
name: gmail-drafts
description: Prepare Gmail-ready draft artifacts for a separate freelance Gmail account without sending email. Use when Codex needs to stage outreach messages as copyable text, .eml files, or Gmail drafts when an authenticated Gmail connector is explicitly available.
---

# Gmail Drafts

## Principle

Separate the freelance operation from Readymind. Use the configured freelance Gmail identity from `crm/outreach_config.example.json`, then generate draft files or connector drafts only after the user approves the account.

## Without Gmail Connector

Generate local draft artifacts:

```powershell
python plugins\freelance-outreach-assistant\scripts\draft_emails.py crm\leads_scored.csv --output-dir outputs\drafts --limit 10
```

Use `.txt` files for copy/paste into Gmail. `.eml` files are local draft artifacts, not proof of Gmail delivery.

## With Gmail Connector

If a Gmail tool is installed and the user explicitly asks to create Gmail drafts, create drafts only. Never send automatically. Respect `baja`, `No contactar`, daily limits, and the opt-out line.

## Account Setup Checklist

Create the Gmail account manually, update `sender_name`, `sender_email`, `signature`, demo links, and optional `calendar_link` in the config before real outreach.
