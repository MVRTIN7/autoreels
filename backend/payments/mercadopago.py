import mercadopago
from backend.config.settings import MP_ACCESS_TOKEN, PLANES_CREDITOS

# =========================
# SDK
# =========================
sdk = mercadopago.SDK(str(MP_ACCESS_TOKEN))


# =========================
# CREAR PREFERENCIA
# =========================
def crear_preferencia(user_id, creditos):

    monto = PLANES_CREDITOS.get(creditos)
    if not monto:
        return None

    preference_data = {
        "items": [
            {
                "title": f"{creditos} Créditos AutoReels",
                "quantity": 1,
                "currency_id": "CLP",
                "unit_price": float(monto)
            }
        ],
        "payer": {
            "email": "test_user@test.com"
        },
        "metadata": {
            "user_id": user_id,
            "creditos": creditos
        },
        "back_urls": {
            "success": "http://127.0.0.1:5000/",
            "failure": "http://127.0.0.1:5000/",
            "pending": "http://127.0.0.1:5000/"
        },

        "notification_url": "https://autoreels-production.up.railway.app/webhook",


    }

    preference = sdk.preference().create(preference_data)

    print("🔍 RESPUESTA MP:", preference)

    if preference.get("status") != 201:
        return None

    return preference["response"]["init_point"]
