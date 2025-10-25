import unittest
from models import (
    Payment,
    REGISTRADO,
    FALLIDO,
    PAGADO,
    PAYMENT_METHOD_CC,
    PAYMENT_METHOD_PAYPAL
)


class TestPaymentState(unittest.TestCase):

    def setUp(self):
        """Se ejecuta antes de cada test."""
        self.pago = Payment(REGISTRADO(), 1, 1000, PAYMENT_METHOD_CC)
        self.assertEqual(self.pago.status, "REGISTRADO")

    # --- REGISTRADO ---
    def test_registrado_a_fallido(self):
        self.pago.pago_fallido()
        self.assertIsInstance(self.pago._state, FALLIDO)
        self.assertEqual(self.pago.status, "FALLIDO")

    def test_registrado_a_pagado(self):
        self.pago.pago_exitoso()
        self.assertIsInstance(self.pago._state, PAGADO)
        self.assertEqual(self.pago.status, "PAGADO")

    def test_registrado_revertir(self):
        msg = self.pago.revertir()
        self.assertIsInstance(self.pago._state, REGISTRADO)
        self.assertEqual(self.pago.status, "REGISTRADO")

    def test_registrado_updatear(self):
        self.pago.updatear(1200, PAYMENT_METHOD_PAYPAL)
        self.assertEqual(self.pago.amount, 1200)
        self.assertEqual(self.pago.payment_method, PAYMENT_METHOD_PAYPAL)
        self.assertIsInstance(self.pago._state, REGISTRADO)
        self.assertEqual(self.pago.status, "REGISTRADO")

    # --- FALLIDO ---
    def test_fallido_revertir_a_registrado(self):
        self.pago.pago_fallido()
        self.assertEqual(self.pago.status, "FALLIDO")

        self.pago.revertir()
        self.assertIsInstance(self.pago._state, REGISTRADO)
        self.assertEqual(self.pago.status, "REGISTRADO")

    def test_fallido_no_puede_pagar(self):
        self.pago.pago_fallido()
        self.assertEqual(self.pago.status, "FALLIDO")

        msg = self.pago.pago_exitoso()
        self.assertEqual(self.pago.status, "FALLIDO")

    def test_fallido_no_puede_updatear(self):
        self.pago.pago_fallido()
        antes=self.pago.amount
        self.pago.updatear(1300, PAYMENT_METHOD_CC)
        self.assertEqual(self.pago.status, "FALLIDO")
        self.assertEqual(antes,self.pago.amount)

    # --- PAGADO ---
    def test_pagado_no_puede_fallar(self):
        self.pago.pago_exitoso()
        self.assertEqual(self.pago.status, "PAGADO")

        msg = self.pago.pago_fallido()
        self.assertEqual(self.pago.status, "PAGADO")

    def test_pagado_no_puede_revertir(self):
        self.pago.pago_exitoso()
        msg = self.pago.revertir()
        self.assertEqual(self.pago.status, "PAGADO")

    def test_pagado_no_puede_updatear(self):
        self.pago.pago_exitoso()
        self.pago.updatear(1500, PAYMENT_METHOD_PAYPAL)
        self.assertEqual(self.pago.amount, 1000)  # No debe cambiar
        self.assertEqual(self.pago.payment_method, PAYMENT_METHOD_CC)
        self.assertEqual(self.pago.status, "PAGADO")


if __name__ == "__main__":
    unittest.main()
