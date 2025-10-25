from abc import ABC, abstractmethod
from typing import List

# Importamos las constantes necesarias desde el Contrato de Datos (models.py)
from models import STATUS_REGISTRADO, PAYMENT_METHOD_CC, PAYMENT_METHOD_PAYPAL 

class ValidationStrategy(ABC):
    """
    Interfaz (Estrategia Abstracta) para todas las validaciones de pagos.
    """
    @abstractmethod
    def validate(self, payment_id: str, amount: float, all_payments_data: dict) -> bool:
        """
        Ejecuta las reglas de validación específicas del método de pago.
        
        Args:
            payment_id (str): ID del pago actual.
            amount (float): Monto del pago a validar.
            all_payments_data (dict): Diccionario que contiene todos los pagos del sistema
                                      (Necesario para la validación de Tarjeta de Crédito).

        Returns:
            bool: True si el pago es válido, False si falla la validación.
        """
        pass

class CreditCardValidation(ValidationStrategy):
    """
    Estrategia Concreta: Validación para Tarjeta de Crédito.
    Reglas: Monto < $10.000 Y no más de 1 pago 'REGISTRADO' con este medio.
    """
    
    def validate(self, payment_id: str, amount: float, all_payments_data: dict) -> bool:
        
        # 1. Verificar que el pago sea menor a $10.000
        if amount >= 10000.0:
            return False

        # 2. Contar pagos registrados con Tarjeta de Crédito (excluyendo el actual)
        count_registered_cc = 0
        
        # El pago actual solo debe contarse si está en estado REGISTRADO y lo estamos re-intentando.
        # Al iterar sobre all_payments_data, evitamos el problema de contar el pago actual
        # si ya existe en la lista de pagos del disco y queremos reintentarlo/actualizarlo.
        
        for pid, payment in all_payments_data.items():
            # Excluye el pago que estamos intentando pagar actualmente (si ya existe en la lista de pagos)
            # Esto maneja el caso donde el pago actual fue registrado pero aún no ha sido pagado.
            if pid == payment_id and payment.get("status") == STATUS_REGISTRADO:
                continue
                
            is_cc = payment.get("payment_method") == PAYMENT_METHOD_CC
            is_registered = payment.get("status") == STATUS_REGISTRADO
            
            # Condición: Valida que no haya más de 1 pago con este medio de pago en estado "REGISTRADO"
            if is_cc and is_registered:
                count_registered_cc += 1

        # 3. Validar el límite (Si ya hay 1 o más, falla la validación)
        if count_registered_cc >= 1:
            return False

        return True # Pasa todas las validaciones

class PayPalValidation(ValidationStrategy):
    """
    Estrategia Concreta: Validación para PayPal.
    [cite_start]Regla: Monto menor a $5000 [cite: 444]
    """
    
    def validate(self, payment_id: str, amount: float, all_payments_data: dict) -> bool:
        
        if amount >= 5000.0:
            return False
            
        return True

# Diccionario Factory para seleccionar la Estrategia correcta
VALIDATION_STRATEGIES = {
    PAYMENT_METHOD_CC: CreditCardValidation(),
    PAYMENT_METHOD_PAYPAL: PayPalValidation()
}

def get_validation_strategy(payment_method: str) -> ValidationStrategy:
    """Selecciona la estrategia de validación según el método de pago."""
    return VALIDATION_STRATEGIES.get(payment_method)