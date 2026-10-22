"""Adaptador experimental SENTINELA R22 -> resumen de investigación TradingAgents.

SOLO LECTURA. No importa ni llama API de broker, no autoriza órdenes.
Consume el JSON generado por AUDITAR_SENTINELA_MULTIAGENTE_R22.bat.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping

SOURCE_NAME = "SENTINELA_MULTIAGENTE_MCP_LAB"
REQUIRED_ROLES = (
    "ANALISTA_PATRON",
    "ANALISTA_LATENCIA",
    "ANALISTA_ADN",
    "AUDITOR_RESULTADOS",
    "DIRECTOR_MCP",
)


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _nonnegative(value: Any, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{label} debe ser entero no negativo")
    return value


def summarize_sentinela_report(report: Mapping[str, Any]) -> dict[str, Any]:
    """Devuelve evidencia compacta sin atribuir WIN a señales sin liquidación."""
    if report.get("name") != SOURCE_NAME or report.get("offline_only") is not True:
        raise ValueError("Se requiere reporte oficial offline del auditor SENTINELA R22")
    roles = _mapping(report.get("roles"))
    missing = [name for name in REQUIRED_ROLES if name not in roles]
    if missing:
        raise ValueError("Faltan roles del reporte: " + ", ".join(missing))

    pattern = _mapping(roles["ANALISTA_PATRON"])
    latency = _mapping(roles["ANALISTA_LATENCIA"])
    dna = _mapping(roles["ANALISTA_ADN"])
    audit = _mapping(roles["AUDITOR_RESULTADOS"])
    director = _mapping(roles["DIRECTOR_MCP"])

    if audit.get("authority") != "SOLO_LECTURA" or director.get("authority") != "NINGUNA_COMPRA":
        raise ValueError("Reporte con autoridad de ejecución inesperada")

    outcomes = _mapping(audit.get("verified_outcomes"))
    win = _nonnegative(outcomes.get("WIN", 0), "WIN")
    loss = _nonnegative(outcomes.get("LOSS", 0), "LOSS")
    draw = _nonnegative(outcomes.get("DRAW", 0), "DRAW")
    total = _nonnegative(audit.get("verified_trades", 0), "verified_trades")
    if total != win + loss + draw:
        raise ValueError("Resultados verificados inconsistentes")

    rate = round(100 * win / (win + loss), 2) if win + loss else None
    return {
        "schema": "sentinela.mcp.research_snapshot.v1",
        "source": SOURCE_NAME,
        "generated_utc": report.get("generated_utc"),
        "strategy": "FRESH_NEW_IMPULSE_VISUAL",
        "entry_contract": "EMA cruce confirmado en C; estocástico 13,3,3; entrada en C+1",
        "execution_authority": False,
        "broker_connected": False,
        "verified": {"WIN": win, "LOSS": loss, "DRAW": draw, "total": total,
                     "winrate_excluding_draw_pct": rate},
        "read_evaluations": _nonnegative(pattern.get("read_evaluations", 0), "read_evaluations"),
        "late_decisions": _nonnegative(latency.get("late_decisions", 0), "late_decisions"),
        "provider_tick_timestamp_verified": latency.get("provider_tick_timestamp_verified") is True,
        "context_hypotheses_only": dict(_mapping(dna.get("context_hypothesis_counts"))),
        "alerts": list(director.get("alerts", [])),
        "notes": "Solo para análisis diferido; nunca introducir esta salida en el gatillo BUY.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Exportar resumen forense SENTINELA R22 sin órdenes")
    parser.add_argument("--input", type=Path, required=True, help="SENTINELA_MULTIAGENTE_REPORTE.json")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = json.loads(args.input.read_text(encoding="utf-8"))
    output = summarize_sentinela_report(report)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Resumen offline guardado en {args.output}")


if __name__ == "__main__":
    main()
