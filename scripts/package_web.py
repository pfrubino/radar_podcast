import shutil, os

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
public_dir = os.path.join(base_dir, "public")
zip_dest = os.path.join(base_dir, "podcast-radar-web")

shutil.make_archive(zip_dest, "zip", public_dir)
print(f"Archivo empaquetado listo en: {zip_dest}.zip")
