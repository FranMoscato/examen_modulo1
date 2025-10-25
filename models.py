from pydantic import BaseModel, Field
from typing import Dict, Any

# 1. Definición de Constantes (Acordadas para el Patrón State)
# Estas constantes serán utilizadas por la lógica de estados y las estrategias.

STATUS_REGISTRADO = "REGISTRADO"
STATUS_PAGADO = "PAGADO"
STATUS_FALLIDO = "FALLIDO"

PAYMENT_METHOD_CC = "Tarjeta de Crédito"
PAYMENT_METHOD_PAYPAL = "PayPal"

# 2. Clase Payment (El Modelo de Datos Central)
class Payment(BaseModel):
    """
    Representa un pago en el sistema.
    """
    
    # Configuración para permitir la instanciación por nombre del atributo (necesario para los tests)
    model_config = {
        "populate_by_name": True 
    }
    
    # Atributos principales (validación Pydantic)
    payment_id: str = Field(alias="payment_id")
    amount: float
    payment_method: str = Field(alias="payment_method")
    
    # Atributo de Estado (manejado por la lógica de tu compañero)
    status: str