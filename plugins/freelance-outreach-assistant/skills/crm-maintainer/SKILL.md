---
name: crm-maintainer
description: Maintain and audit the freelance outreach CRM CSV or Excel-exported CSV. Use when Codex needs to inspect lead statuses, detect duplicates, enforce opt-outs, find missing fields, or prepare safe updates for outreach follow-up workflows.
---

# CRM Maintainer

## Audit

Run:

```powershell
python plugins\freelance-outreach-assistant\scripts\crm_audit.py crm\leads.csv
```

Use `--strict` when a CI/test-style failure should happen on duplicate or invalid emails.

## Maintenance Rules

- Keep columns aligned with `../../references/crm-schema.md`.
- Mark opt-outs as `baja=si` and `estado=No contactar`.
- Do not remove rows when a lead opts out; keep them to prevent future contact.
- Use ISO dates (`YYYY-MM-DD`) for `ultimo_contacto` and `proximo_followup`.
- Keep manual notes in `notas`, not in state fields.

## Status Updates

After the user sends a message manually, update `estado=Enviado` and `ultimo_contacto=<today>`. After follow-ups, move to `Follow-up 1` or `Follow-up 2`.

If a lead replies, move to `Respondio`, `Reunion`, or `Propuesta` and stop automated follow-up suggestions.

When editing CRM files, preserve user-entered columns and do not overwrite unrelated notes.
