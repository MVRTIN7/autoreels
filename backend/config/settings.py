# backend/config/settings.py
import os

# =====================
# MERCADO PAGO
# =====================
MP_ACCESS_TOKEN = os.getenv("MP_ACCESS_TOKEN")

if not MP_ACCESS_TOKEN:
    raise ValueError("❌ MP_ACCESS_TOKEN no está definido en las variables de entorno")

# =====================
# PLANES DE CRÉDITOS
# =====================
PLANES_CREDITOS = {
    1: 1000,
    5: 4500,
    10: 8000
}

# =====================
# ADMIN
# =====================
ADMIN_EMAIL = "admin@autoreels.cl"
ADMIN_PASSWORD = "supersecreto123"
