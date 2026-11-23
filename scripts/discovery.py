#!/usr/bin/env python3
"""
Agente Rastreador / Discovery para Podcast Radar
Rastrea canales semilla y realiza búsquedas por similitud semántica.
Extrae metadatos crudos: video_id, título, canal, duración exacta, thumbnail y enlace.
"""

import urllib.request
import urllib.parse
import json
import re
import html
import os
import sys
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "es-ES,es;q=0.9,en;q=0.8"
}

def fetch_page(url: str, timeout: int = 10) -> str:
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="ignore")

def extract_video_details(video_id: str) -> Optional[Dict[str, Any]]:
    """Extrae metadatos de un video de YouTube a partir de su ID."""
    url = f"https://www.youtube.com/watch?v={video_id}"
    try:
        content = fetch_page(url)
    except Exception as e:
        print(f"  [WARN] No se pudo acceder al video {video_id}: {e}")
        return None

    # Título
    title_m = re.search(r'<meta\s+name="title"\s+content="([^"]+)"', content)
    if not title_m:
        title_m = re.search(r"<title>(.*?)</title>", content)
    raw_title = html.unescape(title_m.group(1)) if title_m else ""
    # Limpiar sufijo " - YouTube"
    cleaned_title = re.sub(r"\s*-\s*YouTube$", "", raw_title).strip()

    # Canal
    channel_m = re.search(r'<link\s+itemprop="name"\s+content="([^"]+)"', content)
    if not channel_m:
        channel_m = re.search(r'"ownerChannelName":"([^"]+)"', content)
    channel = html.unescape(channel_m.group(1)) if channel_m else "Canal de YouTube"

    # Duración en segundos
    dur_m = re.search(r'"approxDurationMs":"(\d+)"', content)
    dur_seconds = int(dur_m.group(1)) // 1000 if dur_m else 0

    if dur_seconds == 0:
        # Fallback a microformat duration
        iso_dur = re.search(r'<meta\s+itemprop="duration"\s+content="PT([^"]+)"', content)
        if iso_dur:
            raw_iso = iso_dur.group(1)
            h = re.search(r'(\d+)H', raw_iso)
            m = re.search(r'(\d+)M', raw_iso)
            s = re.search(r'(\d+)S', raw_iso)
            dur_seconds = (int(h.group(1)) * 3600 if h else 0) + \
                          (int(m.group(1)) * 60 if m else 0) + \
                          (int(s.group(1)) if s else 0)

    # Formato legible (ej: '1h 24m' o '38 min')
    hours = dur_seconds // 3600
    minutes = (dur_seconds % 3600) // 60
    if hours > 0:
        duration_str = f"{hours}h {minutes}m"
    else:
        duration_str = f"{minutes} min"

    # Miniatura
    thumbnail = f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg"

    # Fecha estimada
    date_m = re.search(r'<meta\s+itemprop="datePublished"\s+content="([^"]+)"', content)
    published_at = date_m.group(1)[:10] if date_m else datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # Descripción corta (para extraer el valor)
    desc_m = re.search(r'<meta\s+name="description"\s+content="([^"]+)"', content)
    description = html.unescape(desc_m.group(1)) if desc_m else ""

    return {
        "video_id": video_id,
        "title": cleaned_title,
        "channel": channel,
        "duration": duration_str,
        "duration_seconds": dur_seconds,
        "url": url,
        "thumbnail": thumbnail,
        "published_at": published_at,
        "raw_description": description[:300]
    }

def search_youtube_videos(query: str, max_results: int = 4) -> List[str]:
    """Busca videos en YouTube y devuelve lista de IDs de videos únicos."""
    search_url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}"
    try:
        html_content = fetch_page(search_url)
        found_ids = re.findall(r'watch\?v=([a-zA-Z0-9_-]{11})', html_content)
        unique_ids = []
        for vid in found_ids:
            if vid not in unique_ids:
                unique_ids.append(vid)
            if len(unique_ids) >= max_results:
                break
        return unique_ids
    except Exception as e:
        print(f"[ERROR] Error buscando '{query}': {e}")
        return []

def run_discovery(config_path: str = "config/preferences.json", existing_file: str = "data/podcasts.json") -> List[Dict[str, Any]]:
    print("=" * 60)
    print("🛰️  AGENTE RASTREADOR (DISCOVERY) - INICIANDO EXPLORACIÓN")
    print("=" * 60)

    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    # Cargar IDs existentes para evitar duplicados
    existing_ids = set()
    if os.path.exists(existing_file):
        with open(existing_file, "r", encoding="utf-8") as f:
            for p in json.load(f):
                existing_ids.add(p.get("url", "").split("v=")[-1])
                existing_ids.add(p.get("id"))

    candidates = []
    seen_vids = set(existing_ids)

    # 1. Rastrear Canales Semilla Favoritos
    print("\n[Paso 1] Rastreando canales semilla configurados...")
    for seed in config.get("seed_channels", []):
        name = seed["name"]
        query = seed["search_query"]
        print(f" -> Consultando: {name} ('{query}')")
        vids = search_youtube_videos(query, max_results=2)
        for vid in vids:
            if vid not in seen_vids:
                seen_vids.add(vid)
                details = extract_video_details(vid)
                if details:
                    details["candidate_theme"] = seed.get("default_theme", "Tecnología")
                    details["source_type"] = "canal_semilla"
                    candidates.append(details)
                    print(f"    ✔ Descubierto: {details['title'][:45]}... ({details['duration']})")

    # 2. Rastrear por Similitud Semántica y Afinidad
    print("\n[Paso 2] Explorando afinidad y temas emergentes...")
    for sim in config.get("similarity_queries", []):
        theme = sim["theme"]
        query = sim["query"]
        print(f" -> Explorando tema: {theme} ('{query}')")
        vids = search_youtube_videos(query, max_results=2)
        for vid in vids:
            if vid not in seen_vids:
                seen_vids.add(vid)
                details = extract_video_details(vid)
                if details:
                    details["candidate_theme"] = theme
                    details["source_type"] = "afinidad_tematica"
                    candidates.append(details)
                    print(f"    ✔ Descubierto: {details['title'][:45]}... ({details['duration']})")

    print("\n" + "=" * 60)
    print(f"TOTAL CANDIDATOS CRUDOS DESCUBIERTOS: {len(candidates)}")
    print("=" * 60)
    return candidates

if __name__ == "__main__":
    results = run_discovery()
    output_path = "data/raw_candidates.json"
    os.makedirs("data", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\nResultados crudos guardados en: {output_path}")
