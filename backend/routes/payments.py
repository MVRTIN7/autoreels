from flask import Blueprint, request, redirect
from backend.payments.mercadopago import crear_preferencia, sdk
import json
import os

payments_bp = Blueprint("payments", __name__)

USERS_FILE = "data/users.json"


# =========================
# CREAR PAGO
# =========================
@payments_bp.route("/crear-pago", methods=["POST"])
def crear_pago():
    try:
        user_id = request.cookies.get("user_id")
        creditos = int(request.form.get("creditos", 0))

        if not user_id or creditos <= 0:
            return "❌ Datos inválidos", 400

        link_pago = crear_preferencia(user_id, creditos)

        if not link_pago:
            return "❌ Error creando pago", 400

        return redirect(link_pago)

    except Exception as e:
        print("❌ Error crear-pago:", e)
        return "❌ Error interno", 500


# =========================
# WEBHOOK MERCADO PAGO
# =========================
@payments_bp.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.json
        if not data:
            return "No data", 400

        payment_id = data.get("data", {}).get("id")
        if not payment_id:
            return "No payment id", 200

        pago = sdk.payment().get(payment_id)
        info = pago.get("response", {})

        if info.get("status") != "approved":
            return "Not approved", 200

        metadata = info.get("metadata", {})
        creditos = int(metadata.get("creditos", 0))
        user_id = metadata.get("user_id")

        if not user_id or creditos <= 0:
            return "Invalid metadata", 200

        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, "r", encoding="utf-8") as f:
                usuarios = json.load(f)
        else:
            usuarios = {}

        if user_id not in usuarios:
            usuarios[user_id] = {"creditos": 0}

        usuarios[user_id]["creditos"] += creditos

        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(usuarios, f, indent=4)

        print(f"✅ Créditos sumados: {creditos} a usuario {user_id}")

        return "OK", 200

    except Exception as e:
        print("❌ Error webhook:", e)
        return "Error", 500

