from flask import Flask, render_template, request, jsonify, send_from_directory, make_response
from backend.routes.payments import payments_bp
import os
import subprocess
import uuid
import json
import time

app = Flask(__name__)
app.register_blueprint(payments_bp)


# =========================
# CARPETAS
# =========================
UPLOAD_FOLDER = "Fotos"
MUSIC_FOLDER = "Musica"
OUTPUT_FOLDER = "outputs"
USERS_FILE = "data/users.json"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(MUSIC_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
os.makedirs("data", exist_ok=True)

# =========================
# CONFIG
# =========================
EXT_VALIDAS = (".jpg", ".jpeg", ".png")
MAX_FOTOS = 10

# =========================
# USUARIOS (FUNCIONES BASE)
# =========================
def cargar_usuarios():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def guardar_usuarios(usuarios):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(usuarios, f, indent=4)

def obtener_usuario(user_id):
    usuarios = cargar_usuarios()

    if user_id not in usuarios:
        usuarios[user_id] = {
            "creditos": 0,   # 🔴 parte sin créditos
            "creado": time.time()
        }
        guardar_usuarios(usuarios)

    return usuarios[user_id]

# =========================
# HOME
# =========================
@app.route("/")
def index():
    user_id = request.cookies.get("user_id")

    if not user_id:
        user_id = uuid.uuid4().hex
        usuario = obtener_usuario(user_id)

        resp = make_response(
            render_template("index.html", creditos=usuario["creditos"])
        )
        resp.set_cookie("user_id", user_id, max_age=60*60*24*365)
        return resp

    usuario = obtener_usuario(user_id)
    return render_template("index.html", creditos=usuario["creditos"])

# =========================
# SERVIR VIDEO
# =========================
@app.route("/video/<filename>")
def video(filename):
    return send_from_directory(OUTPUT_FOLDER, filename)

# =========================
# GENERAR REEL
# =========================
@app.route("/generar", methods=["POST"])
def generar():

    # 🔒 VALIDAR USUARIO Y CRÉDITOS
    user_id = request.cookies.get("user_id")
    usuario = obtener_usuario(user_id)

    if usuario["creditos"] <= 0:
        return "❌ No tienes créditos disponibles"

    marca = request.form["marca"]
    modelo = request.form["modelo"]
    anio = request.form["anio"]
    precio = request.form["precio"]
    whatsapp = request.form["whatsapp"]

    mostrar_precio = "mostrar_precio" in request.form
    mostrar_whatsapp = "mostrar_whatsapp" in request.form

    # LIMPIAR FOTOS
    for archivo in os.listdir(UPLOAD_FOLDER):
        ruta = os.path.join(UPLOAD_FOLDER, archivo)
        if os.path.isfile(ruta):
            os.remove(ruta)

    # GUARDAR FOTOS
    fotos = request.files.getlist("fotos")
    if len(fotos) > MAX_FOTOS:
        return "❌ Máximo 10 fotos permitidas"

    fotos_validas = 0
    for foto in fotos:
        if foto.filename.lower().endswith(EXT_VALIDAS):
            foto.save(os.path.join(UPLOAD_FOLDER, foto.filename))
            fotos_validas += 1

    if fotos_validas == 0:
        return "❌ Debes subir al menos una imagen válida"

    # MÚSICA
    usar_musica = "usar_musica" in request.form
    musica_path = ""

    if usar_musica:
        musica = request.files.get("musica")
        if musica and musica.filename.lower().endswith(".mp3"):
            musica_path = os.path.join(MUSIC_FOLDER, musica.filename)
            musica.save(musica_path)
        else:
            musica_path = os.path.join(MUSIC_FOLDER, "musica_default.mp3")

    # NOMBRE VIDEO
    video_id = uuid.uuid4().hex[:8]
    safe_marca = "".join(c for c in marca if c.isalnum() or c == "_")
    safe_modelo = "".join(c for c in modelo if c.isalnum() or c == "_")
    output_filename = f"{safe_marca}_{safe_modelo}_{video_id}.mp4"

    # EJECUTAR SCRIPT
    resultado = subprocess.call([
        "python", "generar_video.py",
        marca, modelo, anio, precio, whatsapp,
        str(mostrar_precio),
        str(mostrar_whatsapp),
        output_filename,
        musica_path
    ])

    if resultado != 0:
        return "❌ Error al generar el video"

    # 🔥 DESCONTAR CRÉDITO (SOLO SI SE CREÓ BIEN)
    usuarios = cargar_usuarios()
    usuarios[user_id]["creditos"] -= 1
    guardar_usuarios(usuarios)

    # LIMPIEZA
    for archivo in os.listdir(UPLOAD_FOLDER):
        ruta = os.path.join(UPLOAD_FOLDER, archivo)
        if os.path.isfile(ruta):
            os.remove(ruta)

    if musica_path and "default" not in musica_path:
        if os.path.exists(musica_path):
            os.remove(musica_path)

    return render_template("resultado.html", video=output_filename)

# =========================
# BORRAR VIDEO
# =========================
@app.route("/borrar", methods=["POST"])
def borrar_video():
    try:
        data = json.loads(request.data)
        video = data.get("video")
        ruta = os.path.join(OUTPUT_FOLDER, video)

        if os.path.exists(ruta):
            os.remove(ruta)
            return jsonify({"status": "ok"})

        return jsonify({"status": "not_found"})
    except Exception as e:
        return jsonify({"status": "error", "msg": str(e)}), 500

# =========================
# RUN
# =========================
if __name__ == "__main__":
    app.run(debug=True)
