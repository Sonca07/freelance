from __future__ import annotations

import argparse
from pathlib import Path

from outreach_lib import REQUIRED_COLUMNS, write_csv


SAMPLE_ROWS = [
    {
        "lead_id": "L-0001",
        "negocio": "Aura Belleza",
        "rubro": "estetica",
        "barrio": "Palermo",
        "email": "contacto@aurabelleza.example",
        "fuente_publica": "Perfil publico ficticio",
        "web_redes": "https://instagram.com/aura-belleza",
        "dolor_detectado": "turnos por WhatsApp sin agenda visible",
        "estado": "Calificado",
        "notas": "FICTICIO - reemplazar por lead real",
    }
]


def main() -> int:
    parser = argparse.ArgumentParser(description="Create an empty outreach CRM CSV.")
    parser.add_argument("output", type=Path)
    parser.add_argument("--sample", action="store_true")
    args = parser.parse_args()

    rows = SAMPLE_ROWS if args.sample else []
    write_csv(args.output, rows, REQUIRED_COLUMNS)
    print(f"Created CRM CSV -> {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
