from __future__ import annotations
from abc import ABC, abstractmethod
from pydantic import BaseModel, Field
from typing import Dict, Any


# 1. Definición de Constantes (Acordadas para el Patrón State)
# Estas constantes serán utilizadas por la lógica de estados y las estrategias.

STATUS_REGISTRADO = "REGISTRADO"
STATUS_PAGADO = "PAGADO"
STATUS_FALLIDO = "FALLIDO"

PAYMENT_METHOD_CC = "Tarjeta de Crédito"
PAYMENT_METHOD_PAYPAL = "PayPal"



class Payment:
    """
    The Context defines the interface of interest to clients. It also maintains
    a reference to an instance of a State subclass, which represents the current
    state of the Context.
    """

    _state = None

    # Atributos principales 
    payment_id= None
    amount= None
    payment_method= None
    
    # Atributo de Estado en STRING
    status: str

    def __init__(self, state: State,id: str, amount: float, method: str) -> None:
        self.payment_id=id
        self.amount=amount
        self.payment_method=method
        self.status=type(state).__name__
        self.transition_to(state)

    def transition_to(self, state: State):
        """
        The Context allows changing the State object at runtime.
        """

        print(f"Context: Transition to {type(state).__name__}")
        self.status=type(state).__name__
        self._state = state
        self._state.context = self

    """
    The Context delegates part of its behavior to the current State object.
    """

    def pago_fallido(self):
        return self._state.handle1()

    def pago_exitoso(self):
        return self._state.handle2()

    def revertir(self):
        return self._state.handle3()

    def updatear(self,amount: float, method: str):
        return self._state.handle4(amount, method)


class State(ABC):

    @property
    def context(self) -> Payment:
        return self._context

    @context.setter
    def context(self, context: Payment) -> None:
        self._context = context

    @abstractmethod
    def handle1(self) -> None:
        pass

    @abstractmethod
    def handle2(self) -> None:
        pass

    @abstractmethod
    def handle3(self) -> None:
        pass

    @abstractmethod
    def handle4(self,amount: float, method: str) -> None:
        pass


class REGISTRADO(State):
    def handle1(self) -> None: #pago_fallido
        self.context.transition_to(FALLIDO())
        return 'Pago fallido'

    def handle2(self) -> None: #pago_exitoso
        self.context.transition_to(PAGADO())
        return 'Pago Exitoso'

    def handle3(self) -> None: #revertir
        return 'Este pago esta en estado REGISTRADO'

    def handle4(self,amount: float, method: str) -> None: #updatear
        self.context.amount=amount
        self.context.payment_method=method
        self.context.transition_to(REGISTRADO())
        return 'Registro Updateado'

class FALLIDO(State):
    def handle1(self) -> None: #pago_fallido
        return 'Este pago esta en estado FALLIDO'

    def handle2(self) -> None: #pago_exitoso
        return 'Este pago esta en estado FALLIDO'

    def handle3(self) -> None: #revertir
        self.context.transition_to(REGISTRADO())
        return 'Registro revertido con exito'

    def handle4(self,amount: float, method: str) -> None: #updatear
        return 'Este pago esta en estado FALLIDO'

class PAGADO(State):
    def handle1(self) -> None: #pago_fallido
        return 'Este pago esta en estado PAGADO'

    def handle2(self) -> None: #pago_exitoso
        return 'Este pago esta en estado PAGADO'

    def handle3(self) -> None: #revertir
        return 'Este pago esta en estado PAGADO'

    def handle4(self,amount: float, method: str) -> None: #updatear
        return 'Este pago esta en estado PAGADO'


if __name__ == "__main__":
    pago = Payment(REGISTRADO(),1,1000,PAYMENT_METHOD_CC)
    print(pago.amount)
    print(pago.payment_method)
    pago.pago_fallido()
    print(pago.status)
    pago.pago_exitoso()
    print(pago.status)
    pago.revertir()
    print(pago.status)
    pago.updatear(1100,PAYMENT_METHOD_PAYPAL)
    print(pago.amount)
    print(pago.payment_method)
