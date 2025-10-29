from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional

# Importamos las constantes necesarias desde models.py
# (para usarlas como valor en las transiciones, ej. "REGISTRADO")
from models import STATUS_REGISTRADO, STATUS_PAGADO, STATUS_FALLIDO

# La importación de Payment es solo para type-hinting
# (evita una dependencia cíclica en tiempo de ejecución)
if TYPE_CHECKING:
    from models import Payment

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