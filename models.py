from __future__ import annotations
from typing import Dict, Any, TYPE_CHECKING
from pydantic import BaseModel, Field
from states.states import State

# 1. Definición de Constantes (Contrato de Datos)

STATUS_REGISTRADO = "REGISTRADO"
STATUS_PAGADO = "PAGADO"
STATUS_FALLIDO = "FALLIDO"

PAYMENT_METHOD_CC = "Tarjeta de Credito"
PAYMENT_METHOD_PAYPAL = "PayPal"

class PaymentData(BaseModel):
    """
    Este es el Modelo de DATOS (Pydantic) que usará FastAPI
    para validar la API y representar la estructura de data.json.
    """
    model_config = {
        "populate_by_name": True 
    }
    
    amount: float
    payment_method: str
    status: str

class Payment:
    """
    El Contexto (Payment) define la interfaz de interés para los clientes.
    Mantiene una referencia al objeto de Estado actual.
    """

    _state: State = None

    # Atributos principales
    payment_id: str
    amount: float
    payment_method: str

    # Atributo de Estado en STRING (Para persistencia/API)
    status: str

    def __init__(self, state: State,id: str, amount: float, method: str) -> None:
        self.payment_id=id
        self.amount=amount
        self.payment_method=method
        self.status=type(state).__name__
        self.transition_to(state)

    def transition_to(self, state: State):
        """
        El Contexto permite cambiar el objeto de Estado en tiempo de ejecución.
        """
        self._state = state
        self._state.context = self
        # Actualiza el status en string (ej. "REGISTRADO")
        self.status = type(state).__name__

    # --- Métodos que delegan el comportamiento al objeto de estado actual ---
    # Los métodos públicos del Contexto llaman al método abstracto del Estado.

    def pago_fallido(self) -> str:
        # handle1 en el estado
        return self._state.handle1()

    def pago_exitoso(self) -> str:
        # handle2 en el estado
        return self._state.handle2()

    def revertir(self) -> str:
        # handle3 en el estado
        return self._state.handle3()

    def updatear(self, amount: float, method: str) -> str:
        # handle4 en el estado
        return self._state.handle4(amount, method)