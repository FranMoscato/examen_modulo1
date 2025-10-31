from __future__ import annotations
from typing import Dict, Any, TYPE_CHECKING

# 1. Definición de Constantes (Contrato de Datos)

STATUS_REGISTRADO = "REGISTRADO"
STATUS_PAGADO = "PAGADO"
STATUS_FALLIDO = "FALLIDO"

PAYMENT_METHOD_CC = "Tarjeta de Credito"
PAYMENT_METHOD_PAYPAL = "PayPal"