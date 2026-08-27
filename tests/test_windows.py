import unittest
import sys
import os
import numpy as np

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

from aanalogos import extraer_ventana, obtener_descripcion_ventana, cargar_todas_oscilaciones


class TestWindows(unittest.TestCase):
    """Validar la construcción de ventanas retrospectivas semestrales intra e interanuales."""

    @classmethod
    def setUpClass(cls):
        cls.oscilaciones = cargar_todas_oscilaciones(PROJECT_DIR)

    def test_intra_annual_windows(self):
        """Ventana intra-anual (mes >= 6)."""
        desc = obtener_descripcion_ventana(2015, 10)
        self.assertEqual(desc, ['MAY(2015)', 'JUN(2015)', 'JUL(2015)', 'AGO(2015)', 'SET(2015)', 'OCT(2015)'])
        
        v = extraer_ventana(self.oscilaciones["AMO"], 2015, 10)
        self.assertEqual(len(v), 6)
        self.assertFalse(np.isnan(v).any())

    def test_cross_year_windows(self):
        """Ventana interanual que cruza diciembre/enero (mes < 6)."""
        desc_feb = obtener_descripcion_ventana(2015, 2)
        self.assertEqual(desc_feb, ['SET(2014)', 'OCT(2014)', 'NOV(2014)', 'DIC(2014)', 'ENE(2015)', 'FEB(2015)'])
        
        v_feb = extraer_ventana(self.oscilaciones["AMO"], 2015, 2)
        self.assertEqual(len(v_feb), 6)
        self.assertFalse(np.isnan(v_feb).any())


if __name__ == "__main__":
    unittest.main()
