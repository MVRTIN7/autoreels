import os
import subprocess
import sys

# =========================
# VALIDAR ARGUMENTOS
# =========================
if len(sys.argv) < 9:
    print("❌ Error: faltan argumentos")
    sys.exit(1)

marca = sys.argv[1]
modelo = sys.argv[2]
anio = sys.argv[3]
precio = sys.argv[4]
whatsapp = sys.argv[5]

mostrar_precio = sys.argv[6] == "True"
mostrar_whatsapp = sys.argv[7] == "True"

output_filename = sys.argv[8]

# Música opcional
musica_path = sys.argv[9] if len(sys.argv) > 9 and sys.argv[9] != "" else None

# =========================
# RUTAS
# =========================
fotos_dir = "Fotos"
outputs_dir = "outputs"
fuente = "Arial"

os.makedirs(outputs_dir, exist_ok=True)
output_path = os.path.join(outputs_dir, output_filename)

# =========================
# LISTA DE IMÁGENES
# =========================
imagenes = sorted(os.listdir(fotos_dir))

with open("imagenes.txt", "w", encoding="utf-8") as f:
    for img in imagenes:
        f.write(f"file '{fotos_dir}/{img}'\n")
        f.write("duration 1.2\n")

# =========================
# VIDEO BASE 9:16 (SIN ZOOM)
# =========================
subprocess.call([
    "ffmpeg", "-y",
    "-f", "concat", "-safe", "0",
    "-i", "imagenes.txt",
    "-vf",
    "scale=1080:1920:force_original_aspect_ratio=decrease,"
    "pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black",
    "-pix_fmt", "yuv420p",
    "base.mp4"
])

# =========================
# TEXTOS DINÁMICOS
# =========================
filtros = []

filtros.append(
    f"drawtext=font='{fuente}':"
    f"text='{marca} {modelo} {anio}':"
    "x=40:y=40:fontsize=60:fontcolor=white:"
    "box=1:boxcolor=black@0.6"
)

if mostrar_precio:
    filtros.append(
        f"drawtext=font='{fuente}':"
        f"text='Precio $ {precio}':"
        "x=40:y=h-260:fontsize=80:fontcolor=yellow:"
        "box=1:boxcolor=black@0.6"
    )

if mostrar_whatsapp:
    filtros.append(
        f"drawtext=font='{fuente}':"
        f"text='WhatsApp {whatsapp}':"
        "x=40:y=h-160:fontsize=50:fontcolor=white:"
        "box=1:boxcolor=black@0.6"
    )

filtro_final = ",".join(filtros)

# =========================
# VIDEO FINAL
# =========================
if musica_path and os.path.exists(musica_path):
    subprocess.call([
        "ffmpeg", "-y",
        "-i", "base.mp4",
        "-i", musica_path,
        "-vf", filtro_final,
        "-shortest",
        "-map", "0:v:0",
        "-map", "1:a:0",
        output_path
    ])
else:
    subprocess.call([
        "ffmpeg", "-y",
        "-i", "base.mp4",
        "-vf", filtro_final,
        output_path
    ])

print(f"✅ REEL CREADO → {output_path}")

# =========================
# LIMPIEZA
# =========================
if os.path.exists("base.mp4"):
    os.remove("base.mp4")

if os.path.exists("imagenes.txt"):
    os.remove("imagenes.txt")
