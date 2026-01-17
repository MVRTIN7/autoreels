# backend/config/settings.py
import os
# =====================
# MERCADO PAGO
# =====================
MP_PUBLIC_KEY = os.getenv("APP_USR-dd17344d-a0e7-4d80-978f-d7a696220a31")
MP_ACCESS_TOKEN = os.getenv("APP_USR-4456530589942283-011417-56c9693ff1ffd2b4816075f30e70744c-643401778")

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
