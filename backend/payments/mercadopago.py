import mercadopago
from backend.config.settings import MP_ACCESS_TOKEN, PLANES_CREDITOS

sdk = mercadopago.SDK(MP_ACCESS_TOKEN)

def crear_preferencia(user_id, creditos):

    monto = PLANES_CREDITOS.get(creditos)
    if not monto:
        print("❌ Plan inválido:", creditos)
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
        "metadata": {
            "user_id": user_id,
            "creditos": creditos
        },
        "back_urls": {
            "success": "https://autoreels-production.up.railway.app/",
            "failure": "https://autoreels-production.up.railway.app/",
            "pending": "https://autoreels-production.up.railway.app/"
        },
        "notification_url": "https://autoreels-production.up.railway.app/webhook",
        "auto_return": "approved"
    }

    preference = sdk.preference().create(preference_data)

    print("🟢 RESPUESTA MP:", preference)

    if preference.get("status") != 201:
        print("❌ ERROR MP:", preference)
        return None

    return preference["response"]["init_point"]
