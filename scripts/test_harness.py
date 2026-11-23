"""
Test Harness Determinista para Podcast Radar
Valida:
1. Esquema de datos obligatorio (id, title, channel, theme, duration, summary, url, thumbnail, published_at).
2. Linter de calidad:
   - Duración >= 15 minutos (mínimo 900 segundos).
   - Resumen <= 70 palabras y no vacío.
   - Formato de duración estándar (e.g., "1h 45m" o "48 min").
3. Validador de enlaces HTTP 200 en YouTube y miniaturas.
"""

import sys
import json
import re
import urllib.request
from typing import List, Dict, Any, Tuple

REQUIRED_FIELDS = [
    "id",
    "title",
    "channel",
    "theme",
    "duration",
    "duration_seconds",
    "summary",
    "url",
    "thumbnail",
    "published_at"
]

ALLOWED_THEMES = [
    "Inteligencia Artificial",
    "Negocios & Startups",
    "Ciencia & Salud",
    "Filosofía & Modelos Mentales",
    "Tecnología"
]

def parse_duration_to_seconds(duration_str: str) -> int:
    """Parsea formatos como '1h 45m', '2h 10m', '48 min', '15 min' a segundos."""
    duration_str = duration_str.strip()
    hours_match = re.search(r'(\d+)\s*h(?:ora)?s?', duration_str)
    mins_match = re.search(r'(\d+)\s*m(?:in)?s?', duration_str)
    
    total_seconds = 0
    if hours_match:
        total_seconds += int(hours_match.group(1)) * 3600
    if mins_match:
        total_seconds += int(mins_match.group(1)) * 60
        
    return total_seconds

def check_http_200(url: str, timeout: int = 6) -> bool:
    try:
        req = urllib.request.Request(
            url, 
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        )
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return response.status == 200
    except Exception as e:
        return False

def validate_podcast(podcast: Dict[str, Any], verify_urls: bool = True) -> Tuple[bool, List[str]]:
    errors = []
    pid = podcast.get("id", "DESCONOCIDO")

    # 1. Esquema de campos requeridos
    for field in REQUIRED_FIELDS:
        if field not in podcast or podcast[field] is None or str(podcast[field]).strip() == "":
            errors.append(f"[{pid}] Campo obligatorio faltante o vacío: '{field}'")

    if errors:
        return False, errors

    # 2. Temática válida
    if podcast["theme"] not in ALLOWED_THEMES:
        errors.append(f"[{pid}] Temática inválida '{podcast['theme']}'. Permitidas: {ALLOWED_THEMES}")

    # 3. Duración mínima de 15 minutos (900 seg)
    dur_sec = podcast.get("duration_seconds")
    if not isinstance(dur_sec, (int, float)):
        dur_sec = parse_duration_to_seconds(podcast.get("duration", ""))
    
    if dur_sec < 900:
        errors.append(f"[{pid}] Fallo filtro duración: {dur_sec}s ({dur_sec//60} min). Mínimo exigido: 15 min (900s).")

    # 4. Linter de resumen: conciso (1 párrafo, <= 70 palabras)
    summary = podcast.get("summary", "").strip()
    word_count = len(summary.split())
    if word_count > 70:
        errors.append(f"[{pid}] Fallo linter de resumen: {word_count} palabras. Máximo permitido: 70 palabras.")
    if "\n\n" in summary:
        errors.append(f"[{pid}] El resumen debe ser un único párrafo sin saltos dobles de línea.")

    # 5. Validador de enlaces HTTP 200 (si está habilitado)
    if verify_urls:
        if not check_http_200(podcast["url"]):
            errors.append(f"[{pid}] Enlace no accesible (HTTP != 200): {podcast['url']}")
        if not check_http_200(podcast["thumbnail"]):
            errors.append(f"[{pid}] Miniatura no accesible (HTTP != 200): {podcast['thumbnail']}")

    return len(errors) == 0, errors

def run_harness(file_path: str, verify_urls: bool = True) -> bool:
    print("=" * 60)
    print("INICIANDO ARNÉS DE PRUEBAS DETERMINISTA - PODCAST RADAR")
    print("=" * 60)
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"[ERROR CRÍTICO] No se pudo leer el archivo JSON '{file_path}': {e}")
        return False

    if not isinstance(data, list):
        print(f"[ERROR CRÍTICO] El JSON raíz debe ser un array de podcasts.")
        return False

    all_passed = True
    total = len(data)
    print(f"Total de episodios a validar: {total}")
    print(f"Verificación de URLs en vivo: {'ACTIVADA' if verify_urls else 'DESACTIVADA'}")
    print("-" * 60)

    for idx, podcast in enumerate(data, start=1):
        passed, errors = validate_podcast(podcast, verify_urls=verify_urls)
        pid = podcast.get("id", f"Item #{idx}")
        title = podcast.get("title", "Sin título")[:40]
        
        if passed:
            print(f"[OK] ({idx}/{total}) {pid} - {title}... -> PASÓ TODAS LAS PRUEBAS")
        else:
            all_passed = False
            print(f"[RECHAZADO] ({idx}/{total}) {pid} - {title}...")
            for err in errors:
                print(f"    ❌ {err}")

    print("=" * 60)
    if all_passed:
        print("RESULTADO: TODOS LOS ELEMENTOS SUPERARON EL ARNÉS CON ÉXITO.")
        return True
    else:
        print("RESULTADO: EL ARNÉS DETECTÓ VIOLACIONES DE CALIDAD / REGLAS.")
        return False

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "data/podcasts.json"
    verify_links = "--skip-network" not in sys.argv
    success = run_harness(target, verify_urls=verify_links)
    sys.exit(0 if success else 1)
