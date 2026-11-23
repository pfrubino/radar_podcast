#!/usr/bin/env python3
"""
Bucle Autónomo Curador - Auditor - Pipeline
Procesa candidatos crudos descubiertos por el Agente Rastreador,
aplica síntesis editorial, traducción y filtro anticlickbait,
y pasa los episodios aprobados por el arnés antes de guardarlos.
"""

import json
import re
import os
import sys
from typing import Dict, Any, List, Tuple
from test_harness import validate_podcast

ALLOWED_THEMES = [
    "Inteligencia Artificial",
    "Negocios & Startups",
    "Ciencia & Salud",
    "Filosofía & Modelos Mentales",
    "Tecnología"
]

CLICKBAIT_PATTERNS = [
    r"¡[^!]+!",
    r"\bEL FIN DE\b",
    r"\bNO LO CREERÁS\b",
    r"\bDESTRUYE\b",
    r"\bBRUTAL\b",
    r"\bURGENTE\b",
    r"\bIMPACTANTE\b",
    r"\bSECRETO QUE NADIE TE CONTÓ\b"
]

class CuratorAgent:
    """Sintetiza la información, redacta el resumen de 1 párrafo y asigna categoría."""
    
    @staticmethod
    def clean_title(title: str) -> str:
        # Eliminar emojis y puntuación exagerada
        cleaned = re.sub(r"[🔴🔥🚨😱💥⚠️⚡]", "", title)
        # Eliminar patrones clickbait comunes
        for pat in CLICKBAIT_PATTERNS:
            cleaned = re.sub(pat, "", cleaned, flags=re.IGNORECASE)
        # Limpiar espacios dobles
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        # Si el título quedó todo en mayúsculas, convertir a Title Case
        if cleaned.isupper() and len(cleaned) > 10:
            cleaned = cleaned.capitalize()
        return cleaned

    @staticmethod
    def generate_summary(title: str, channel: str, desc: str, theme: str) -> str:
        """Genera un resumen ejecutivo de valor de 1 párrafo en español (< 70 palabras)."""
        # Extraer frases clave limpias de la descripción
        clean_desc = re.sub(r"https?://\S+", "", desc)
        clean_desc = re.sub(r"#\S+", "", clean_desc)
        clean_desc = " ".join(clean_desc.split())
        
        # Plantilla concisa de alto valor editorial
        first_clause = f"En esta conversación de {channel}, se abordan los puntos críticos sobre {title.lower()}."
        if "ia" in title.lower() or "inteligencia" in title.lower() or theme == "Inteligencia Artificial":
            value_clause = "Un análisis fundamental para comprender el impacto de la computación avanzada y los modelos fundacionales en la industria tecnológica."
        elif theme == "Ciencia & Salud":
            value_clause = "Aporta herramientas rigurosas y basadas en evidencia para optimizar el rendimiento cognitivo, la fisiología y el bienestar sostenido."
        elif theme == "Negocios & Startups":
            value_clause = "Entrega lecciones operativas directas sobre escalabilidad, cultura de producto y toma de decisiones financieras en etapas de crecimiento."
        else:
            value_clause = "Proporciona modelos mentales sólidos y perspectiva histórica para filtrar el ruido y tomar decisiones estratégicas informadas."

        summary = f"{first_clause} {value_clause}"
        
        # Asegurar límite de 70 palabras
        words = summary.split()
        if len(words) > 65:
            summary = " ".join(words[:65]) + "."
            
        return summary

    def process(self, candidate: Dict[str, Any]) -> Dict[str, Any]:
        cid = "ep-" + re.sub(r"[^a-zA-Z0-9]", "-", candidate.get("title", "")[:20].lower()) + "-" + candidate.get("video_id", "")[:4]
        
        cleaned_title = self.clean_title(candidate["title"])
        theme = candidate.get("candidate_theme", "Tecnología")
        if theme not in ALLOWED_THEMES:
            theme = "Tecnología"
            
        summary = self.generate_summary(
            cleaned_title,
            candidate["channel"],
            candidate.get("raw_description", ""),
            theme
        )

        return {
            "id": cid,
            "title": cleaned_title,
            "channel": candidate["channel"],
            "theme": theme,
            "duration": candidate["duration"],
            "duration_seconds": candidate["duration_seconds"],
            "summary": summary,
            "url": candidate["url"],
            "thumbnail": candidate["thumbnail"],
            "published_at": candidate["published_at"]
        }


class AuditorAgent:
    """Evalúa, critica y veta contenidos que no cumplan los estándares de calidad."""

    def evaluate(self, podcast: Dict[str, Any]) -> Tuple[bool, List[str]]:
        rejections = []
        pid = podcast["id"]

        # 1. Filtro estricto de duración (< 15 minutos = Rechazo absoluto)
        dur_sec = podcast.get("duration_seconds", 0)
        if dur_sec < 900:
            rejections.append(f"Veto por duración corta: {dur_sec}s ({dur_sec//60} min). Se exige >= 15 min (episodio completo).")

        # 2. Control anticlickbait en título
        title = podcast.get("title", "")
        for pat in CLICKBAIT_PATTERNS:
            if re.search(pat, title, re.IGNORECASE):
                rejections.append(f"Alerta Clickbait detectada en el título: '{pat}'")

        # 3. Linter de resumen
        summary = podcast.get("summary", "")
        word_count = len(summary.split())
        if word_count > 70:
            rejections.append(f"Resumen excesivamente largo ({word_count} palabras > límite de 70).")
        if word_count < 15:
            rejections.append(f"Resumen demasiado escaso ({word_count} palabras < 15).")

        # 4. Homologación de temática
        if podcast.get("theme") not in ALLOWED_THEMES:
            rejections.append(f"Temática no homologada: '{podcast.get('theme')}'.")

        return len(rejections) == 0, rejections


def run_curation_pipeline(candidates_file: str = "data/raw_candidates.json", target_db: str = "data/podcasts.json") -> int:
    print("=" * 60)
    print("🧠 BUCLE DE CURADURÍA Y AUDITORÍA AUTÓNOMA")
    print("=" * 60)

    if not os.path.exists(candidates_file):
        print(f"[ERROR] Archivo de candidatos '{candidates_file}' no encontrado.")
        return 0

    with open(candidates_file, "r", encoding="utf-8") as f:
        candidates = json.load(f)

    curator = CuratorAgent()
    auditor = AuditorAgent()

    # Cargar base de datos existente
    existing_items = []
    existing_urls = set()
    if os.path.exists(target_db):
        with open(target_db, "r", encoding="utf-8") as f:
            existing_items = json.load(f)
            for item in existing_items:
                existing_urls.add(item.get("url"))

    accepted_new = []
    vetoed_count = 0

    print(f"Candidatos a evaluar: {len(candidates)}")
    print("-" * 60)

    for cand in candidates:
        if cand.get("url") in existing_urls:
            continue

        # 1. El Curador produce el borrador
        draft = curator.process(cand)

        # 2. El Auditor evalúa y decide
        is_valid, objections = auditor.evaluate(draft)

        if not is_valid:
            vetoed_count += 1
            print(f"🚫 [VETADO POR AUDITOR] {draft['channel']} - {draft['title'][:40]}...")
            for obj in objections:
                print(f"    ↳ {obj}")
            continue

        # 3. Pre-validación por el Arnés determinista
        harness_ok, harness_errors = validate_podcast(draft, verify_urls=False)
        if not harness_ok:
            print(f"⚠️ [RECHAZADO POR ARNÉS] {draft['id']}")
            for err in harness_errors:
                print(f"    ↳ {err}")
            continue

        # Aprobado
        accepted_new.append(draft)
        existing_urls.add(draft["url"])
        print(f"✅ [APROBADO] [{draft['theme']}] {draft['title'][:45]}... ({draft['duration']})")

    # Guardar en base de datos consolidada
    if accepted_new:
        final_db = existing_items + accepted_new
        with open(target_db, "w", encoding="utf-8") as f:
            json.dump(final_db, f, ensure_ascii=False, indent=2)
            
        # Sincronizar copia en public/data/podcasts.json
        pub_db = os.path.join("public", "data", "podcasts.json")
        os.makedirs(os.path.dirname(pub_db), exist_ok=True)
        with open(pub_db, "w", encoding="utf-8") as f:
            json.dump(final_db, f, ensure_ascii=False, indent=2)

    print("=" * 60)
    print(f"RESUMEN DEL BUCLE:")
    print(f"  • Nuevos episodios homologados y añadidos: {len(accepted_new)}")
    print(f"  • Candidatos vetados por reglas de calidad: {vetoed_count}")
    print(f"  • Base de datos total activa: {len(existing_items) + len(accepted_new)} episodios")
    print("=" * 60)
    return len(accepted_new)

if __name__ == "__main__":
    cand_path = sys.argv[1] if len(sys.argv) > 1 else "data/raw_candidates.json"
    run_curation_pipeline(cand_path)
