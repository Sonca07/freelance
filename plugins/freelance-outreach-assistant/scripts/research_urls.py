from __future__ import annotations

import argparse
import csv
import html
import re
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

from outreach_lib import REQUIRED_COLUMNS, score_row, validate_email, write_csv


SEED_COLUMNS = [
    "seed_id",
    "url",
    "negocio",
    "rubro",
    "barrio",
    "email",
    "fuente_publica",
    "dolor_detectado",
    "notas",
]

REVIEW_COLUMNS = SEED_COLUMNS + ["reason"]

BLOCKED_HOST_PARTS = (
    "instagram.com",
    "facebook.com",
    "fb.com",
    "google.com",
    "google.com.ar",
    "maps.app.goo.gl",
    "goo.gl",
    "tiktok.com",
    "linkedin.com",
)

BARRIOS_AMBA = [
    "Agronomia",
    "Almagro",
    "Avellaneda",
    "Balvanera",
    "Barracas",
    "Belgrano",
    "Boedo",
    "Caballito",
    "Chacarita",
    "Colegiales",
    "Flores",
    "Lanus",
    "Liniers",
    "Lomas de Zamora",
    "Moron",
    "Nuñez",
    "Palermo",
    "Recoleta",
    "Saavedra",
    "San Telmo",
    "Villa Crespo",
    "Villa Urquiza",
]

EMAIL_RE = re.compile(r"(?<![\w.+-])[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}(?![\w.-])")
TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.IGNORECASE | re.DOTALL)
META_RE_TEMPLATE = r'<meta[^>]+(?:property|name)=["\']{name}["\'][^>]+content=["\']([^"\']+)["\'][^>]*>'


def read_seed_csv(path: Path) -> List[Dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = []
        for row in reader:
            rows.append({column: (row.get(column) or "").strip() for column in SEED_COLUMNS})
    return rows


def write_review(path: Path, rows: Sequence[Dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=REVIEW_COLUMNS)
        writer.writeheader()
        writer.writerows({column: row.get(column, "") for column in REVIEW_COLUMNS} for row in rows)


def host_for(url: str) -> str:
    parsed = urllib.parse.urlparse(url if "://" in url else f"https://{url}")
    return (parsed.netloc or "").lower().removeprefix("www.")


def is_blocked_platform(url: str) -> bool:
    host = host_for(url)
    return any(part == host or host.endswith(f".{part}") for part in BLOCKED_HOST_PARTS)


def fetch_public_page(url: str, timeout: int = 12) -> Tuple[str, str]:
    target = url if "://" in url else f"https://{url}"
    request = urllib.request.Request(
        target,
        headers={
            "User-Agent": "NexoraLeadResearch/1.0 (+manual public business research)",
            "Accept": "text/html,application/xhtml+xml",
        },
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        content_type = response.headers.get("content-type", "")
        if "text/html" not in content_type and "application/xhtml+xml" not in content_type:
            raise ValueError(f"unsupported content type: {content_type or 'unknown'}")
        charset = response.headers.get_content_charset() or "utf-8"
        body = response.read(1_500_000).decode(charset, errors="replace")
        return body, response.geturl()


def clean_text(value: str) -> str:
    text = re.sub(r"<script[\s\S]*?</script>", " ", value, flags=re.IGNORECASE)
    text = re.sub(r"<style[\s\S]*?</style>", " ", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def meta_content(document: str, name: str) -> str:
    pattern = re.compile(META_RE_TEMPLATE.format(name=re.escape(name)), re.IGNORECASE | re.DOTALL)
    match = pattern.search(document)
    return html.unescape(match.group(1)).strip() if match else ""


def extract_title(document: str) -> str:
    for meta_name in ["og:site_name", "og:title", "twitter:title"]:
        value = meta_content(document, meta_name)
        if value:
            return value
    match = TITLE_RE.search(document)
    if not match:
        return ""
    title = clean_text(match.group(1))
    return re.split(r"\s+[|-]\s+", title)[0].strip()


def extract_emails(document: str) -> List[str]:
    decoded = html.unescape(document)
    decoded = decoded.replace("%40", "@")
    emails = []
    for match in EMAIL_RE.findall(decoded):
        email = match.strip(".,;:()[]{}<>").lower()
        if validate_email(email) and email not in emails:
            emails.append(email)
    return emails


def infer_barrio(text: str) -> str:
    normalized = text.lower()
    for barrio in BARRIOS_AMBA:
        if barrio.lower() in normalized:
            return barrio
    return ""


def detect_pain(text: str, url: str = "") -> str:
    lower = f"{text} {url}".lower()
    has_booking = any(token in lower for token in ["reserv", "booking", "calendly", "turno online"])
    has_whatsapp = any(token in lower for token in ["whatsapp", "wa.me", "api.whatsapp"])
    has_turnos = any(token in lower for token in ["turno", "agenda", "horario"])
    if has_whatsapp and not has_booking:
        return "turnos por WhatsApp sin agenda visible"
    if has_turnos and not has_booking:
        return "muestra turnos u horarios sin reserva online clara"
    if not has_booking:
        return "no muestra reserva online clara"
    return "servicios visibles con oportunidad de mejorar conversion"


def build_lead(seed: Dict[str, str], document: str = "", fetched_url: str = "") -> Tuple[Optional[Dict[str, str]], Optional[str]]:
    text = clean_text(document) if document else ""
    emails = extract_emails(document) if document else []
    manual_email = (seed.get("email") or "").strip().lower()
    email = manual_email or (emails[0] if emails else "")
    if email and not validate_email(email):
        return None, "invalid_email"
    if not email:
        return None, "missing_public_email"

    source_url = fetched_url or seed.get("url", "")
    negocio = seed.get("negocio") or extract_title(document) or host_for(source_url) or "Negocio sin nombre"
    barrio = seed.get("barrio") or infer_barrio(text)
    dolor = seed.get("dolor_detectado") or detect_pain(text, source_url)
    fuente = seed.get("fuente_publica") or f"Sitio web publico: {source_url}"
    lead = {
        "lead_id": seed.get("seed_id", ""),
        "negocio": negocio,
        "rubro": seed.get("rubro") or "barberia",
        "barrio": barrio,
        "email": email,
        "fuente_publica": fuente,
        "web_redes": source_url,
        "score": "",
        "dolor_detectado": dolor,
        "estado": "Calificado",
        "ultimo_contacto": "",
        "proximo_followup": "",
        "baja": "",
        "respuesta": "",
        "notas": seed.get("notas", ""),
    }
    lead["score"] = str(score_row(lead))
    return lead, None


def research_seed(seed: Dict[str, str], timeout: int = 12) -> Tuple[Optional[Dict[str, str]], Optional[Dict[str, str]]]:
    url = seed.get("url", "")
    if seed.get("email"):
        lead, reason = build_lead(seed)
        return lead, ({**seed, "reason": reason} if reason else None)
    if not url:
        return None, {**seed, "reason": "missing_url"}
    if is_blocked_platform(url):
        return None, {**seed, "reason": "blocked_platform_manual_review"}
    try:
        document, fetched_url = fetch_public_page(url, timeout=timeout)
        lead, reason = build_lead(seed, document, fetched_url)
        return lead, ({**seed, "reason": reason} if reason else None)
    except (urllib.error.URLError, TimeoutError, ValueError, UnicodeError) as exc:
        return None, {**seed, "reason": f"fetch_failed: {exc}"}


def main() -> int:
    parser = argparse.ArgumentParser(description="Turn reviewed public seed URLs into CRM-ready outreach leads.")
    parser.add_argument("seeds", type=Path, help="CSV with seed URLs and optional manually verified fields.")
    parser.add_argument("--output", type=Path, default=Path("outputs/researched_leads.csv"))
    parser.add_argument("--review-output", type=Path, default=Path("outputs/research_review.csv"))
    parser.add_argument("--timeout", type=int, default=12)
    args = parser.parse_args()

    leads: List[Dict[str, str]] = []
    review: List[Dict[str, str]] = []
    for seed in read_seed_csv(args.seeds):
        lead, review_row = research_seed(seed, timeout=args.timeout)
        if lead:
            leads.append(lead)
        if review_row:
            review.append(review_row)

    write_csv(args.output, leads, REQUIRED_COLUMNS)
    write_review(args.review_output, review)
    print(f"Created {len(leads)} CRM-ready leads -> {args.output}")
    print(f"Queued {len(review)} seeds for manual review -> {args.review_output}")
    print("Blocked platforms are not fetched automatically.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
