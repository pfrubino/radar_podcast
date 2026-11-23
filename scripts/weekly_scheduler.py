#!/usr/bin/env python3
"""
Módulo de Automatización Semanal - Podcast Radar
Ejecuta la rutina completa de forma periódica o bajo demanda:
1. Rastrea canales y temas de afinidad (Discovery).
2. Curaduría y Auditoría de nuevos candidatos.
3. Validación estricta con el Arnés Determinista.
4. Sincronización de base de datos de la web.
5. Registro de auditoría (logs de ejecución).
"""

import os
import sys
import json
import time
from datetime import datetime, timezone

from discovery import run_discovery
from curator_auditor import run_curation_pipeline
from test_harness import run_harness

LOG_FILE = "data/automation_log.json"

def log_event(event_type: str, details: dict):
    os.makedirs("data", exist_ok=True)
    history = []
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                history = json.load(f)
        except Exception:
            history = []

    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event": event_type,
        "details": details
    }
    history.append(record)
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def execute_weekly_cycle() -> bool:
    start_time = time.time()
    print("\n" + "=" * 65)
    print(f"🚀 INICIANDO CICLO SEMANAL AUTOMÁTICO DE PODCAST RADAR")
    print(f"   Fecha: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print("=" * 65)

    # Paso 1: Discovery
    print("\n[FASE 1/3] RASTREO Y DESCUBRIMIENTO (DISCOVERY AGENT)...")
    candidates = run_discovery()
    raw_path = "data/raw_candidates.json"
    with open(raw_path, "w", encoding="utf-8") as f:
        json.dump(candidates, f, ensure_ascii=False, indent=2)

    # Paso 2: Curaduría y Auditoría
    print("\n[FASE 2/3] BUCLE CURADOR-AUDITOR (AUTO-CORRECCIÓN)...")
    added = run_curation_pipeline(raw_path, "data/podcasts.json")

    # Paso 3: Validación del Arnés
    print("\n[FASE 3/3] EJECUCIÓN DEL ARNÉS DETERMINISTA...")
    harness_passed = run_harness("data/podcasts.json", verify_urls=True)

    elapsed = round(time.time() - start_time, 2)
    status = "ÉXITO" if harness_passed else "FALLO_ARNES"

    log_event("CICLO_SEMANAL", {
        "status": status,
        "candidates_discovered": len(candidates),
        "episodes_added": added,
        "duration_seconds": elapsed,
        "harness_verified": harness_passed
    })

    print("\n" + "=" * 65)
    print(f"🏁 CICLO SEMANAL FINALIZADO EN {elapsed}s | ESTADO: {status}")
    print("=" * 65 + "\n")
    return harness_passed

def run_loop():
    """Bucle continuo que corre una vez por semana (cada 7 días)."""
    WEEK_SECONDS = 7 * 24 * 3600
    print("Iniciando servicio de automatización semanal en segundo plano...")
    while True:
        execute_weekly_cycle()
        print(f"Durmiendo hasta el próximo ciclo semanal ({WEEK_SECONDS} segundos)...")
        time.sleep(WEEK_SECONDS)

if __name__ == "__main__":
    if "--daemon" in sys.argv:
        run_loop()
    else:
        execute_weekly_cycle()
