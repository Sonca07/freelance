from __future__ import annotations

import csv
import datetime as dt
import json
import re
import unicodedata
from email.message import EmailMessage
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple


REQUIRED_COLUMNS = [
    "lead_id",
    "negocio",
    "rubro",
    "barrio",
    "email",
    "fuente_publica",
    "web_redes",
    "score",
    "dolor_detectado",
    "estado",
    "ultimo_contacto",
    "proximo_followup",
    "baja",
    "respuesta",
    "notas",
]

VALID_STATES = [
    "Calificado",
    "Borrador creado",
    "Enviado",
    "Follow-up 1",
    "Follow-up 2",
    "Respondio",
    "Reunion",
    "Propuesta",
    "Ganado",
    "Perdido",
    "No contactar",
]

TERMINAL_STATES = {"Ganado", "Perdido", "No contactar"}
BLOCKING_BAJA_VALUES = {"1", "si", "yes", "true", "baja", "no contactar", "unsubscribe"}
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

DEFAULT_CONFIG = {
    "sender_name": "Nexora",
    "sender_email": "hola@nexora.example",
    "brand_name": "Nexora",
    "calendar_link": "",
    "default_demo_link": "https://sonca07.github.io/freelance/",
    "demo_links": {
        "estetica": "https://example.com/demo-estetica",
        "barberia": "https://sonca07.github.io/freelance/",
        "fitness": "https://example.com/demo-fitness",
        "consultorio": "https://example.com/demo-consultorio",
        "general": "https://sonca07.github.io/freelance/",
    },
    "signature": "Nexora\nSoftware simple para operar mejor\nEmail: hola@nexora.example",
    "unsubscribe_line": "Si no corresponde, decime y no vuelvo a contactarte.",
}


def strip_accents(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value or "")
    return "".join(ch for ch in normalized if not unicodedata.combining(ch))


def norm(value: str) -> str:
    return re.sub(r"\s+", " ", strip_accents(value).lower()).strip()


def normalize_state(value: str) -> str:
    key = norm(value)
    aliases = {
        "": "Calificado",
        "calificado": "Calificado",
        "borrador creado": "Borrador creado",
        "enviado": "Enviado",
        "follow up 1": "Follow-up 1",
        "follow-up 1": "Follow-up 1",
        "followup 1": "Follow-up 1",
        "follow up 2": "Follow-up 2",
        "follow-up 2": "Follow-up 2",
        "followup 2": "Follow-up 2",
        "respondio": "Respondio",
        "respondio ": "Respondio",
        "reunion": "Reunion",
        "propuesta": "Propuesta",
        "ganado": "Ganado",
        "perdido": "Perdido",
        "no contactar": "No contactar",
    }
    return aliases.get(key, value.strip() or "Calificado")


def is_truthy_baja(value: str) -> bool:
    return norm(value) in BLOCKING_BAJA_VALUES


def validate_email(value: str) -> bool:
    return bool(EMAIL_RE.match((value or "").strip()))


def today_iso() -> str:
    return dt.date.today().isoformat()


def parse_date(value: str) -> Optional[dt.date]:
    value = (value or "").strip()
    if not value:
        return None
    try:
        return dt.date.fromisoformat(value)
    except ValueError:
        return None


def business_days_after(start: dt.date, days: int) -> dt.date:
    current = start
    remaining = days
    while remaining:
        current += dt.timedelta(days=1)
        if current.weekday() < 5:
            remaining -= 1
    return current


def load_csv(path: Path) -> Tuple[List[Dict[str, str]], List[str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        existing = list(reader.fieldnames or [])
        fieldnames = list(dict.fromkeys(REQUIRED_COLUMNS + existing))
        rows = []
        for raw in reader:
            row = {key: (raw.get(key) or "").strip() for key in fieldnames}
            rows.append(row)
    return rows, fieldnames


def write_csv(path: Path, rows: Sequence[Dict[str, str]], fieldnames: Optional[Sequence[str]] = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    names = list(fieldnames or REQUIRED_COLUMNS)
    names = list(dict.fromkeys(REQUIRED_COLUMNS + names))
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=names)
        writer.writeheader()
        for row in rows:
            writer.writerow({name: row.get(name, "") for name in names})


def normalize_row(row: Dict[str, str], index: int) -> Dict[str, str]:
    cleaned = {key: (value or "").strip() for key, value in row.items()}
    for column in REQUIRED_COLUMNS:
        cleaned.setdefault(column, "")
    cleaned["lead_id"] = cleaned["lead_id"] or f"L-{index:04d}"
    cleaned["email"] = cleaned["email"].lower()
    cleaned["estado"] = normalize_state(cleaned.get("estado", ""))
    cleaned["baja"] = "si" if is_truthy_baja(cleaned.get("baja", "")) else cleaned.get("baja", "")
    return cleaned


def normalize_rows(rows: Sequence[Dict[str, str]]) -> List[Dict[str, str]]:
    return [normalize_row(row, index + 1) for index, row in enumerate(rows)]


def classify_rubro(row: Dict[str, str]) -> str:
    text = norm(" ".join([row.get("rubro", ""), row.get("negocio", ""), row.get("dolor_detectado", "")]))
    if any(word in text for word in ["barber", "barberia", "barbero"]):
        return "barberia"
    if any(word in text for word in ["estetica", "belleza", "spa", "unas", "manicura", "pestanas"]):
        return "estetica"
    if any(word in text for word in ["pilates", "yoga", "fitness", "gimnasio", "entrenamiento"]):
        return "fitness"
    if any(word in text for word in ["consultorio", "odont", "kinesio", "nutric", "psicolog", "medic"]):
        return "consultorio"
    return "general"


def row_is_blocked(row: Dict[str, str]) -> bool:
    return is_truthy_baja(row.get("baja", "")) or normalize_state(row.get("estado", "")) in TERMINAL_STATES


def score_row(row: Dict[str, str]) -> int:
    if row_is_blocked(row):
        return 0
    score = 20
    category = classify_rubro(row)
    category_points = {
        "estetica": 30,
        "barberia": 28,
        "fitness": 24,
        "consultorio": 22,
        "general": 10,
    }
    score += category_points.get(category, 10)
    if validate_email(row.get("email", "")):
        score += 18
    else:
        score -= 30
    if row.get("fuente_publica"):
        score += 10
    if row.get("barrio"):
        score += 5
    web = norm(row.get("web_redes", ""))
    if web:
        score += 5
    if "instagram" in web and not any(token in web for token in [".com.ar", ".com/"]):
        score += 4
    pain = norm(row.get("dolor_detectado", ""))
    if any(word in pain for word in ["whatsapp", "turno", "reserva", "agenda", "horario", "dm", "mensaje"]):
        score += 12
    return max(0, min(100, score))


def apply_scores(rows: Sequence[Dict[str, str]]) -> List[Dict[str, str]]:
    output = []
    for index, row in enumerate(rows, 1):
        cleaned = normalize_row(row, index)
        cleaned["score"] = str(score_row(cleaned))
        output.append(cleaned)
    return output


def recommended_sequence(row: Dict[str, str]) -> Optional[str]:
    state = normalize_state(row.get("estado", ""))
    if row_is_blocked(row):
        return None
    if state in {"Calificado", "Borrador creado"}:
        return "initial"
    if state == "Enviado":
        return "followup_1"
    if state == "Follow-up 1":
        return "followup_2"
    return None


def computed_followup_date(row: Dict[str, str], reference: Optional[dt.date] = None) -> Optional[dt.date]:
    reference = reference or dt.date.today()
    state = normalize_state(row.get("estado", ""))
    explicit = parse_date(row.get("proximo_followup", ""))
    if explicit:
        return explicit
    if state in {"Calificado", "Borrador creado"}:
        return reference
    last = parse_date(row.get("ultimo_contacto", "")) or reference
    if state == "Enviado":
        return business_days_after(last, 3)
    if state == "Follow-up 1":
        return business_days_after(last, 7)
    return None


def due_actions(rows: Sequence[Dict[str, str]], target_date: dt.date, limit: int) -> List[Dict[str, str]]:
    actions = []
    for index, row in enumerate(rows, 1):
        cleaned = normalize_row(row, index)
        if not validate_email(cleaned.get("email", "")):
            continue
        sequence = recommended_sequence(cleaned)
        due_date = computed_followup_date(cleaned, target_date)
        if not sequence or not due_date or due_date > target_date:
            continue
        cleaned["score"] = cleaned.get("score") or str(score_row(cleaned))
        cleaned["action_sequence"] = sequence
        cleaned["computed_followup"] = due_date.isoformat()
        actions.append(cleaned)
    actions.sort(key=lambda item: (-int(item.get("score") or 0), item.get("computed_followup", ""), item.get("negocio", "")))
    return actions[:limit]


def load_config(path: Optional[Path]) -> Dict:
    config = dict(DEFAULT_CONFIG)
    config["demo_links"] = dict(DEFAULT_CONFIG["demo_links"])
    if path and path.exists():
        with path.open("r", encoding="utf-8") as handle:
            loaded = json.load(handle)
        for key, value in loaded.items():
            if key == "demo_links":
                config["demo_links"].update(value or {})
            else:
                config[key] = value
    return config


def demo_link_for(row: Dict[str, str], config: Dict) -> str:
    category = classify_rubro(row)
    return config.get("demo_links", {}).get(category) or config.get("default_demo_link") or ""


def build_email(row: Dict[str, str], config: Dict) -> Tuple[str, str]:
    sequence = row.get("action_sequence") or recommended_sequence(row) or "initial"
    negocio = row.get("negocio") or "tu negocio"
    barrio = row.get("barrio", "")
    demo_link = demo_link_for(row, config)
    source = row.get("fuente_publica") or "su contacto publico"
    pain = row.get("dolor_detectado") or "la gestion de turnos por mensajes"
    signature = config.get("signature") or DEFAULT_CONFIG["signature"]
    opt_out = config.get("unsubscribe_line") or DEFAULT_CONFIG["unsubscribe_line"]
    calendar = config.get("calendar_link", "").strip()
    location = f" en {barrio}" if barrio else ""

    if sequence == "followup_1":
        subject = f"Te dejo la demo de reservas para {negocio}"
        body = (
            f"Hola, vuelvo breve sobre {negocio}{location}.\n\n"
            f"Te habia enviado una idea simple para ordenar reservas/turnos sin depender tanto del ida y vuelta por WhatsApp.\n\n"
            f"Demo: {demo_link}\n\n"
            "Si te interesa, puedo adaptar una primera version con tus servicios, horarios y contacto directo."
        )
    elif sequence == "followup_2":
        subject = f"Cierro por ahora - {negocio}"
        body = (
            "Hola, cierro este hilo para no insistir de mas.\n\n"
            f"Dejo la demo por si mas adelante queres ver una forma simple de mostrar servicios y recibir reservas para {negocio}:\n"
            f"{demo_link}\n\n"
            "Si en algun momento te sirve, respondes este correo y lo vemos."
        )
    else:
        subject = f"{negocio}: reservas online simples"
        body = (
            f"Hola, vi {source} de {negocio}{location} y me parecio que podria servirles una pagina simple para reservas.\n\n"
            f"Trabajo con negocios locales que toman turnos por WhatsApp o mensajes. La idea es resolver algo concreto: {pain}.\n\n"
            f"Arme una demo para mostrar el formato:\n{demo_link}\n\n"
            "Podria adaptarla con sus servicios, horarios, fotos y botones de contacto. Si te sirve, te mando una propuesta corta."
        )

    if calendar:
        body += f"\n\nTambien podemos verlo en 15 minutos aca: {calendar}"
    body += f"\n\n{signature}\n\n{opt_out}"
    return subject, body


def safe_filename(value: str) -> str:
    name = re.sub(r"[^a-zA-Z0-9._-]+", "-", strip_accents(value or "lead")).strip("-").lower()
    return name[:80] or "lead"


def make_eml(row: Dict[str, str], subject: str, body: str, config: Dict) -> EmailMessage:
    message = EmailMessage()
    sender_name = config.get("sender_name") or "Tu Nombre"
    sender_email = config.get("sender_email") or "tu.freelance@gmail.com"
    message["From"] = f"{sender_name} <{sender_email}>"
    message["To"] = row.get("email", "")
    message["Subject"] = subject
    message["X-Unsent"] = "1"
    message.set_content(body)
    return message


def write_drafts(actions: Sequence[Dict[str, str]], output_dir: Path, config: Dict) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    index_rows = []
    for row in actions:
        subject, body = build_email(row, config)
        base = f"{row.get('lead_id', 'lead')}-{safe_filename(row.get('negocio', 'lead'))}-{row.get('action_sequence', 'draft')}"
        txt_path = output_dir / f"{base}.txt"
        eml_path = output_dir / f"{base}.eml"
        txt_path.write_text(f"To: {row.get('email', '')}\nSubject: {subject}\n\n{body}\n", encoding="utf-8")
        eml_path.write_text(make_eml(row, subject, body, config).as_string(), encoding="utf-8")
        index_rows.append(
            {
                "lead_id": row.get("lead_id", ""),
                "negocio": row.get("negocio", ""),
                "email": row.get("email", ""),
                "sequence": row.get("action_sequence", ""),
                "subject": subject,
                "txt_path": str(txt_path),
                "eml_path": str(eml_path),
            }
        )
    index_path = output_dir / "drafts_index.csv"
    with index_path.open("w", encoding="utf-8", newline="") as handle:
        fieldnames = ["lead_id", "negocio", "email", "sequence", "subject", "txt_path", "eml_path"]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(index_rows)
    return index_path


def audit_rows(rows: Sequence[Dict[str, str]], target_date: Optional[dt.date] = None) -> Dict[str, List[str]]:
    target_date = target_date or dt.date.today()
    report = {"critical": [], "warnings": [], "info": []}
    seen_emails = {}
    for index, raw in enumerate(rows, 1):
        row = normalize_row(raw, index)
        label = row.get("lead_id") or f"row {index}"
        email = row.get("email", "")
        if not row.get("negocio"):
            report["warnings"].append(f"{label}: falta negocio")
        if not row.get("fuente_publica"):
            report["warnings"].append(f"{label}: falta fuente_publica")
        if email:
            if not validate_email(email):
                report["critical"].append(f"{label}: email invalido: {email}")
            if email in seen_emails:
                report["critical"].append(f"{label}: email duplicado con {seen_emails[email]}: {email}")
            seen_emails[email] = label
        else:
            report["warnings"].append(f"{label}: falta email")
        state = normalize_state(row.get("estado", ""))
        if state not in VALID_STATES:
            report["warnings"].append(f"{label}: estado no reconocido: {row.get('estado', '')}")
        if is_truthy_baja(row.get("baja", "")) and state not in {"No contactar", "Perdido"}:
            report["warnings"].append(f"{label}: tiene baja pero estado activo ({state})")
        due_date = computed_followup_date(row, target_date)
        if not row_is_blocked(row) and due_date and due_date <= target_date:
            report["info"].append(f"{label}: accion pendiente {recommended_sequence(row)} desde {due_date.isoformat()}")
    return report


def print_report(report: Dict[str, List[str]]) -> None:
    for section in ["critical", "warnings", "info"]:
        print(section.upper())
        items = report.get(section) or []
        if not items:
            print("- none")
        else:
            for item in items:
                print(f"- {item}")
