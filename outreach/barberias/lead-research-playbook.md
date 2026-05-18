# Playbook De Investigacion - Barberias AMBA

## Perfil ideal

Priorizar barberias con:

- agenda o turnos por WhatsApp;
- servicios publicados pero sin reserva clara;
- Instagram activo;
- Google Business con comentarios recientes;
- varios barberos o servicios diferenciados;
- barrio con movimiento comercial.

## Senales de oportunidad

Alta prioridad:

- "Turnos por WhatsApp";
- horarios escritos en posts o historias;
- clientes preguntando precios/turnos en comentarios;
- sin link de reservas;
- carta de servicios poco clara;
- muchas sucursales o varios profesionales.

Baja prioridad:

- ya usan sistema de reservas completo;
- no hay email ni formulario publico;
- negocio sin actividad reciente;
- cuenta privada;
- solo atienden por referido.

## Fuentes permitidas

- sitio web oficial;
- Google Business;
- Instagram publico;
- Facebook publico;
- directorios publicos del negocio;
- formulario de contacto del propio negocio.

No usar bases compradas, scraping agresivo ni emails personales no publicados.

## Como cargar un lead

Completar:

- `negocio`: nombre comercial;
- `rubro`: `barberia`;
- `barrio`: zona o localidad;
- `email`: email publicado;
- `fuente_publica`: donde se vio el contacto;
- `web_redes`: link;
- `dolor_detectado`: senal concreta;
- `estado`: `Calificado`;
- `baja`: vacio.

Ejemplo de dolor:

`turnos por WhatsApp sin agenda visible`

## Semillas revisadas

Para acelerar sin scrapear plataformas sensibles, cargar URLs o datos revisados en:

`crm/lead_research_seeds_sample.csv`

Columnas:

- `seed_id`;
- `url`;
- `negocio`;
- `rubro`;
- `barrio`;
- `email`;
- `fuente_publica`;
- `dolor_detectado`;
- `notas`.

Si la URL es Instagram, Facebook, Google Maps, TikTok o LinkedIn, el sistema la manda a revision manual y no la descarga. Si el email fue copiado manualmente desde una fuente publica, se puede completar `email` y `fuente_publica`.

Comando:

```powershell
python plugins/freelance-outreach-assistant/scripts/research_urls.py crm/lead_research_seeds_sample.csv --output outputs/researched_leads.csv --review-output outputs/research_review.csv
```

## Criterio para contactar

Contactar solo si se puede escribir una primera linea honesta:

`Vi el Instagram publico de {{negocio}} y note que toman turnos por WhatsApp.`
