#!/usr/bin/env python3
"""
Script de despliegue a la nube (Surge.sh)
Publica la carpeta public/ en un dominio HTTPS global accesible 24/7.
"""

import subprocess
import os
import sys
import json
import base64
import urllib.request

EMAIL = "podcastradar.deploy@gmail.com"
PASSWORD = "PodcastRadarSuperSecretPass2026!"
DOMAIN = "podcast-radar-app.surge.sh"

def get_token():
    auth = base64.b64encode(f"{EMAIL}:{PASSWORD}".encode("utf-8")).decode("utf-8")
    req = urllib.request.Request(
        "https://surge.surge.sh/token",
        data=b"",
        headers={
            "Authorization": f"Basic {auth}",
            "Accept": "application/json"
        }
    )
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        return data["token"]

def deploy():
    print(f"Obteniendo credenciales de despliegue en la nube...")
    token = get_token()
    print(f"Token obtenido exitosamente.")
    
    project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "public"))
    print(f"Subiendo contenido de {project_dir} hacia https://{DOMAIN} ...")
    
    env = os.environ.copy()
    env["SURGE_LOGIN"] = EMAIL
    env["SURGE_TOKEN"] = token
    
    cmd = ["npx", "--yes", "surge", project_dir, "--domain", DOMAIN, "--token", token]
    result = subprocess.run(cmd, env=env, capture_output=True, text=True, shell=True)
    
    print("\n--- Salida del Despliegue ---")
    print(result.stdout)
    if result.stderr:
        print("Errores / Advertencias:")
        print(result.stderr)
        
    if result.returncode == 0:
        print(f"\n=======================================================")
        print(f"🎉 ¡DESPLIEGUE EXITOSO!")
        print(f"Acceso 24/7 desde tu celular (con la PC apagada):")
        print(f"👉 https://{DOMAIN}")
        print(f"=======================================================")
        return True
    else:
        print("\nEl despliegue falló.")
        return False

if __name__ == "__main__":
    success = deploy()
    sys.exit(0 if success else 1)
