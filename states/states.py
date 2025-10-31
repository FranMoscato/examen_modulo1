from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional
from pydantic import BaseModel, Field

# Importamos las constantes necesarias desde models.py
# (para usarlas como valor en las transiciones, ej. "REGISTRADO")
from models import STATUS_REGISTRADO, STATUS_PAGADO, STATUS_FALLIDO

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

class State(ABC):
    """
    Clase base abstracta para los Estados.
    Define la interfaz de estado y mantiene una referencia al Contexto (Payment).
    """
    _context: Optional['Payment'] = None

    @property
    def context(self) -> 'Payment':
        # Se asegura que la propiedad 'context' esté establecida
        if self._context is None:
            raise AttributeError("El contexto no ha sido establecido para el estado.")
        return self._context

    @context.setter
    def context(self, context: 'Payment') -> None:
        self._context = context

    # --- Métodos de Interfaz (Triggers/Acciones) ---

    @abstractmethod
    def handle1(self) -> str: # pago_fallido
        """Intenta pasar al estado FALLIDO."""
        pass

    @abstractmethod
    def handle2(self) -> str: # pago_exitoso
        """Intenta pasar al estado PAGADO."""
        pass

    @abstractmethod
    def handle3(self) -> str: # revertir
        """Intenta volver al estado REGISTRADO."""
        pass

    @abstractmethod
    def handle4(self, amount: float, method: str) -> str: # updatear
        """Intenta actualizar los datos del pago."""
        pass


class REGISTRADO(State):
    """Estado Concreto: El pago ha sido registrado."""
    def handle1(self) -> str: # pago_fallido
        # Transición a FALLIDO
        self.context.transition_to(FALLIDO())
        return f'Transición a {STATUS_FALLIDO}. Pago ha fallado.'

    def handle2(self) -> str: # pago_exitoso
        # Transición a PAGADO
        self.context.transition_to(PAGADO())
        return f'Transición a {STATUS_PAGADO}. Pago exitoso.'

    def handle3(self) -> str: # revertir
        # Se mantiene en REGISTRADO
        return f'Este pago ya esta en estado {STATUS_REGISTRADO}'

    def handle4(self, amount: float, method: str) -> str: # updatear
        # Se actualizan los datos y se mantiene el estado
        self.context.amount=amount
        self.context.payment_method=method
        self.context.transition_to(REGISTRADO())
        return 'Registro Updateado'

class FALLIDO(State):
    """Estado Concreto: El pago falló."""
    def handle1(self) -> str: # pago_fallido
        return f'Este pago ya esta en estado {STATUS_FALLIDO}'

    def handle2(self) -> str: # pago_exitoso
        return f'Este pago ya esta en estado {STATUS_FALLIDO}'

    def handle3(self) -> str: # revertir
        # Transición a REGISTRADO (Permitido para reintentar/modificar)
        self.context.transition_to(REGISTRADO())
        return 'Registro revertido con exito'

    def handle4(self, amount: float, method: str) -> str: # updatear
        return f'Este pago ya esta en estado {STATUS_FALLIDO}'

class PAGADO(State):
    """Estado Concreto: El pago fue procesado con éxito."""
    # Una vez PAGADO, la política es no permitir cambios de estado ni de datos.
    def handle1(self) -> str: # pago_fallido
        return f'Este pago ya esta en estado {STATUS_PAGADO}'

    def handle2(self) -> str: # pago_exitoso
        return f'Este pago ya esta en estado {STATUS_PAGADO}'

    def handle3(self) -> str: # revertir
        return f'Este pago ya esta en estado {STATUS_PAGADO}'

    def handle4(self, amount: float, method: str) -> str: # updatear
        return f'Este pago ya esta en estado {STATUS_PAGADO}'


if __name__ == "__main__":
    # prueba local
    from models import Payment
    pago = Payment(REGISTRADO(), "123", 1000, "Tarjeta de Credito")
    print(f"Estado inicial: {pago.status}")
    pago.pago_exitoso()
    print(f"Estado tras éxito: {pago.status}")
    pago.revertir()
    print(f"Estado tras revertir (en PAGADO): {pago.status}")
    pago.pago_fallido()
    print(f"Estado tras fallido (en PAGADO): {pago.status}")