# 📡 Podcast Radar - Sistema Multiagente de Curaduría y Automatización

Podcast Radar es una aplicación web moderna, **mobile-first**, optimizada para el consumo desde smartphones, que funciona como un radar inteligente de episodios de podcasts de YouTube. 

El usuario no busca episodios manualmente: un equipo coordinado de agentes autónomos rastrea novedades semanales, aplica filtros de calidad y anticlickbait, traduce y sintetiza el valor en 1 único párrafo, y actualiza la cartelera de forma periódica.

---

## 🌟 Características Principales

1. **Diseño Mobile-First Estilo App Nativa:**
   - Interfaz limpia, modo oscuro (`slate-950`) con detalles de radar (`emerald-500`).
   - Targets táctiles generosos ($\ge 44\text{px}$) y transiciones fluidas.
   - Acceso inmediato desde el smartphone a través de la red Wi-Fi local o despliegue estático.

2. **Curaduría y Auto-Corrección con IA:**
   - **Agente Curador:** Limpia títulos clickbait, extrae la duración real y redacta un resumen ejecutivo de alto valor (máx. 70 palabras).
   - **Agente Auditor:** Veta clips y shorts (< 15 minutos), verifica categorías y comprueba consistencia editorial.
   - **Traducción Automática:** Episodios internacionales de alta relevancia se sintetizan en español neutro de alto nivel.

3. **Arnés Determinista de Calidad:**
   - Validador estricto de esquema (`id`, `title`, `channel`, `theme`, `duration`, `summary`, `url`, `thumbnail`, `published_at`).
   - Verificación de enlaces HTTP 200 en vivo (YouTube y miniaturas).
   - Linter que prohíbe resúmenes largos o videos cortos.

4. **Experiencia de Usuario Interactiva:**
   - **Badge de Duración Flotante:** Identificación visual rápida del tiempo de escucha (`⏱️ 1h 15m`, `⏱️ 33 min`).
   - **Chips de Temática Deslizables:** *Todos*, *Inteligencia Artificial*, *Ciencia & Salud*, *Negocios & Startups*, *Filosofía & Modelos Mentales*.
   - **Buscador en Tiempo Real:** Filtra instantáneamente por texto, invitados o temas.
   - **Gestión de "Vistos":** Botón de un toque para archivar lo escuchado (guardado en `localStorage`) con panel para revisar y desmarcar archivados.

5. **Automatización Semanal:**
   - Rutina programable (`weekly_scheduler.py`) que rastrea novedades semanales, descarta duplicados y actualiza la web.
   - Configuración lista para **GitHub Actions** (`.github/workflows/weekly_radar.yml`) ejecutándose cada lunes a las 07:00 AM UTC.

---

## 📁 Estructura del Proyecto

```
podcast-radar/
├── config/
│   └── preferences.json        # Canales semilla favoritos y consultas de afinidad
├── data/
│   ├── podcasts.json           # Base de datos homologada por el arnés (18 episodios)
│   ├── raw_candidates.json     # Candidatos crudos del rastreo
│   └── automation_log.json     # Historial de ejecuciones automáticas
├── public/
│   ├── index.html              # Interfaz web móvil (Tailwind, Lucide Icons)
│   ├── app.js                  # Lógica de estado reactivo y persistencia
│   └── data/podcasts.json      # Sincronización para despliegue web
├── scripts/
│   ├── discovery.py            # Agente Rastreador de YouTube y temas afines
│   ├── curator_auditor.py      # Bucle editorial Curador-Auditor
│   ├── test_harness.py         # Arnés determinista de validación
│   └── weekly_scheduler.py     # Orquestador del ciclo semanal automático
├── .github/workflows/
│   └── weekly_radar.yml        # Automatización en la nube (GitHub Actions)
├── serve.py                    # Servidor local con detección de IP para móvil
├── start_server.bat            # Acceso directo para iniciar servidor (Windows)
└── run_radar_weekly.bat        # Acceso directo para ejecutar ciclo semanal
```

---

## 🚀 Guía de Inicio Rápido

### 1. Iniciar la Web y Verla en tu Celular

Ejecuta el servidor con un comando:
```bash
python serve.py
```
O simplemente haz doble clic en `start_server.bat`.

La consola te mostrará dos enlaces:
- **En tu computadora:** `http://localhost:8080`
- **Desde tu celular (misma red Wi-Fi):** `http://<TU_IP_LOCAL>:8080` (ej. `http://192.168.1.45:8080`)

*(También puedes abrir directamente [public/index.html](file:///c:/Users/aa2k8086/Desktop/Anti/podcast-radar/public/index.html) haciendo doble clic en el archivo).*

---

### 2. Personalizar tus Canales y Gustos

Edita el archivo [config/preferences.json](file:///c:/Users/aa2k8086/Desktop/Anti/podcast-radar/config/preferences.json):
- En `seed_channels` añade los nombres y canales que sueles escuchar.
- En `similarity_queries` especifica conceptos clave para que el rastreador descubra podcasts afines automáticamente.

---

### 3. Ejecutar el Ciclo Semanal Manualmente

Para activar el descubrimiento y actualización bajo demanda:
```bash
python scripts/weekly_scheduler.py
```
O con el acceso directo `run_radar_weekly.bat`.

---

### 4. Ejecutar el Arnés de Pruebas

Para validar la integridad de la base de datos y enlaces en cualquier momento:
```bash
python scripts/test_harness.py data/podcasts.json
```
