# Runbook Diario - Outreach Barberias

## Objetivo

Preparar una tanda diaria chica de leads revisables, sin envio automatico. El sistema crea acciones y borradores locales; la aprobacion y el envio quedan manuales.

## Ola 0 ficticia

Usar la Ola 0 para validar el flujo antes de cargar barberias reales.

```powershell
python plugins/freelance-outreach-assistant/scripts/score_leads.py crm/barberias_ola0_ficticio.csv outputs/barberias_ola0_scored.csv
python plugins/freelance-outreach-assistant/scripts/crm_audit.py outputs/barberias_ola0_scored.csv --date 2026-05-18 --strict
python plugins/freelance-outreach-assistant/scripts/next_actions.py outputs/barberias_ola0_scored.csv --date 2026-05-18 --limit 5 --output outputs/barberias_ola0_actions.csv
python plugins/freelance-outreach-assistant/scripts/draft_emails.py outputs/barberias_ola0_scored.csv --config crm/outreach_config.example.json --date 2026-05-18 --limit 5 --output-dir outputs/drafts/barberias_ola0
```

Resultado esperado:

- B-0005 no aparece porque tiene `baja=si` y estado `No contactar`.
- Se generan borradores `.txt` y `.eml` en `outputs/drafts/barberias_ola0`.
- No se envia ningun correo.

## Rutina con leads reales

1. Buscar 10 a 15 barberias por dia.
2. Usar solo email publicado por el negocio, web oficial, Google Business, Instagram o formulario publico.
3. Completar `crm/leads.csv`.
4. Ejecutar scoring y auditoria.
5. Generar maximo 10 borradores diarios.
6. Revisar manualmente asunto, fuente publica, dolor detectado y link a demo.
7. Enviar manualmente desde Gmail.
8. Registrar `estado`, `ultimo_contacto` y `proximo_followup`.
9. Si piden baja, marcar `baja=si` y `estado=No contactar`.

## Metricas de ola

Medir cada 30 contactos:

- respuestas;
- rebotes;
- interesados;
- reuniones;
- objeciones;
- rubro/barrio con mejor respuesta.

Si 30 envios generan menos de 2 respuestas, ajustar nicho, demo o copy antes de escalar.
