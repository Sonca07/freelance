# CRM Schema

Use this exact column order for CSV files that feed the outreach scripts:

`lead_id, negocio, rubro, barrio, email, fuente_publica, web_redes, score, dolor_detectado, estado, ultimo_contacto, proximo_followup, baja, respuesta, notas`

Allowed states:

- `Calificado`
- `Borrador creado`
- `Enviado`
- `Follow-up 1`
- `Follow-up 2`
- `Respondio`
- `Reunion`
- `Propuesta`
- `Ganado`
- `Perdido`
- `No contactar`

Rules:

- `baja` blocks all future drafts when it is `si`, `yes`, `true`, `1`, `baja`, or `no contactar`.
- `No contactar`, `Ganado`, and `Perdido` are terminal states for drafting.
- Store only public source references in `fuente_publica`.
- Keep Gmail sending separate from Readymind identity and files.
