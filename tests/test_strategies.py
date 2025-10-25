import unittest
from strategies.validation_strategy import CreditCardValidation, PayPalValidation
# Importamos las constantes desde el Contrato de Datos
from models import STATUS_REGISTRADO, PAYMENT_METHOD_CC 

# --- Datos Mock para Pruebas de Interferencia ---
# Este es el pago que usaremos para SIMULAR que ya existe un pago CC REGISTRADO en el sistema.
INTERFERENCE_PAYMENT = {
    "amount": 500.0, 
    "payment_method": PAYMENT_METHOD_CC, 
    "status": STATUS_REGISTRADO
}

class TestValidationStrategies(unittest.TestCase):
    """Pruebas unitarias para CreditCardValidation y PayPalValidation."""

    def setUp(self):
        # La base de datos simulada se inicializa VACÍA
        # para aislar cada test y evitar interferencia del límite de CC.
        self.db = {} 
        self.cc_validator = CreditCardValidation()
        self.paypal_validator = PayPalValidation()
        self.new_id = "NUEVO_PAGO_PRUEBA"


    # --- Tests para PayPal ---
    
    def test_paypal_valid_amount(self):
        """Prueba PayPal con un monto menor a $5000."""
        # Monto válido: 4999.99
        self.assertTrue(self.paypal_validator.validate(
            self.new_id, 4999.99, self.db))

    def test_paypal_invalid_amount_limit(self):
        """Prueba PayPal con un monto igual o mayor a $5000 (debe fallar)."""
        # Monto inválido: 5000.0 (límite)
        self.assertFalse(self.paypal_validator.validate(
            self.new_id, 5000.0, self.db))
        # Monto inválido: 5000.01 (sobre el límite)
        self.assertFalse(self.paypal_validator.validate(
            self.new_id, 5000.01, self.db))


    # --- Tests para Tarjeta de Crédito (Monto) ---
    
    def test_cc_valid_amount(self):
        """Prueba CC con un monto menor a $10000. (Debe pasar la validación completa)."""
        # Monto válido: 9999.99. 
        # Como self.db está vacío, la segunda condición (límite de pagos) también pasa.
        self.assertTrue(self.cc_validator.validate(
            self.new_id, 9999.99, self.db))

    def test_cc_invalid_amount_limit(self):
        """Prueba CC con un monto igual o mayor a $10000 (debe fallar)."""
        # Monto inválido: 10000.0 (límite)
        self.assertFalse(self.cc_validator.validate(
            self.new_id, 10000.0, self.db))
        # Monto inválido: 10000.01 (sobre el límite)
        self.assertFalse(self.cc_validator.validate(
            self.new_id, 10000.01, self.db))


    # --- Tests para Tarjeta de Crédito (Límite de Pagos Registrados) ---

    def test_cc_invalid_registered_limit(self):
        """Prueba CC: Debe fallar si ya existe otro pago registrado con CC."""
        # Agregamos el pago de interferencia SOLO para este test.
        self.db["PAGO_EXISTENTE_CC"] = INTERFERENCE_PAYMENT
        
        # El monto es válido, pero falla por el límite de 1 pago registrado.
        self.assertFalse(self.cc_validator.validate(
            self.new_id, 100.0, self.db)) 

    def test_cc_valid_registered_limit_self(self):
        """
        Prueba CC: Debe pasar si el único pago CC registrado es el que estamos intentando pagar 
        (la lógica lo excluye).
        """
        # Scenario: Simulamos que el pago que estamos validando ya está REGISTRADO en la DB.
        self.db[self.new_id] = {
            "amount": 100.0, 
            "payment_method": PAYMENT_METHOD_CC, 
            "status": STATUS_REGISTRADO
        }
        
        # La validación debe pasar porque, al excluir el pago actual (self.new_id), no hay OTROS registrados.
        self.assertTrue(self.cc_validator.validate(
            self.new_id, 100.0, self.db))

    def test_cc_valid_registered_limit_other_method(self):
        """Prueba CC: Debe pasar si el único pago registrado es de OTRO método (ej. PayPal)."""
        # Agregamos un pago registrado, pero que no sea CC
        self.db["PAGO_EXISTENTE_PAYPAL"] = {
            "amount": 100.0, 
            "payment_method": "PayPal", # <-- No interfiere con la regla de CC
            "status": STATUS_REGISTRADO
        }
        
        # La validación debe pasar.
        self.assertTrue(self.cc_validator.validate(
            self.new_id, 100.0, self.db))


if __name__ == '__main__':
    unittest.main()