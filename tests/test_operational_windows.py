"""
Pruebas de validación para ventanas operacionales de 12 meses.
"""

import unittest
import pandas as pd
import numpy as np
from aanalogos.windows import extraer_ventana, obtener_descripcion_ventana
from aanalogos.config import LONGITUD_VENTANA_OPERACIONAL, LONGITUD_VENTANA_METODOLOGICA


class TestOperationalWindows(unittest.TestCase):
    def setUp(self):
        # Crear DataFrame sintético de 3 años consecutivos
        # 2024: 1..12, 2025: 13..24, 2026: 25..36
        self.df_synthetic = pd.DataFrame([
            {"YEAR": 2024, "ENE": 1, "FEB": 2, "MAR": 3, "ABR": 4, "MAY": 5, "JUN": 6,
             "JUL": 7, "AGO": 8, "SET": 9, "OCT": 10, "NOV": 11, "DIC": 12},
            {"YEAR": 2025, "ENE": 13, "FEB": 14, "MAR": 15, "ABR": 16, "MAY": 17, "JUN": 18,
             "JUL": 19, "AGO": 20, "SET": 21, "OCT": 22, "NOV": 23, "DIC": 24},
            {"YEAR": 2026, "ENE": 25, "FEB": 26, "MAR": 27, "ABR": 28, "MAY": 29, "JUN": 30,
             "JUL": 31, "AGO": 32, "SET": 33, "OCT": 34, "NOV": 35, "DIC": 36},
        ])

    def test_12m_window_december(self):
        """Para mes=12 y longitud 12, debe extraer exactamente los 12 meses del mismo año."""
        v = extraer_ventana(self.df_synthetic, 2025, 12, longitud_ventana=12)
        self.assertIsNotNone(v)
        self.assertEqual(len(v), 12)
        expected = [float(x) for x in range(13, 25)]
        self.assertEqual(v, expected)

    def test_12m_window_october(self):
        """Para mes=10 y longitud 12, debe extraer NOV-DIC del año previo + ENE-OCT del año actual."""
        v = extraer_ventana(self.df_synthetic, 2026, 10, longitud_ventana=12)
        self.assertIsNotNone(v)
        self.assertEqual(len(v), 12)
        expected = [23.0, 24.0, 25.0, 26.0, 27.0, 28.0, 29.0, 30.0, 31.0, 32.0, 33.0, 34.0]
        self.assertEqual(v, expected)

    def test_12m_window_january(self):
        """Para mes=1 y longitud 12, debe extraer FEB-DIC del año previo + ENE del año actual."""
        v = extraer_ventana(self.df_synthetic, 2025, 1, longitud_ventana=12)
        self.assertIsNotNone(v)
        self.assertEqual(len(v), 12)
        expected = [2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0]
        self.assertEqual(v, expected)

    def test_12m_window_february(self):
        """Para mes=2 y longitud 12, debe extraer MAR-DIC del año previo + ENE-FEB del año actual."""
        v = extraer_ventana(self.df_synthetic, 2026, 2, longitud_ventana=12)
        self.assertIsNotNone(v)
        self.assertEqual(len(v), 12)
        expected = [15.0, 16.0, 17.0, 18.0, 19.0, 20.0, 21.0, 22.0, 23.0, 24.0, 25.0, 26.0]
        self.assertEqual(v, expected)

        # Verificar etiquetas de meses correspondientes
        desc_feb = obtener_descripcion_ventana(2026, 2, longitud_ventana=12)
        self.assertEqual(len(desc_feb), 12)
        self.assertEqual(desc_feb[0], "MAR(2025)")
        self.assertEqual(desc_feb[-2], "ENE(2026)")
        self.assertEqual(desc_feb[-1], "FEB(2026)")

    def test_window_descriptions_12m(self):
        """Verificar etiquetas legibles de la ventana de 12 meses."""
        desc_oct = obtener_descripcion_ventana(2026, 10, longitud_ventana=12)
        self.assertEqual(len(desc_oct), 12)
        self.assertEqual(desc_oct[0], "NOV(2025)")
        self.assertEqual(desc_oct[1], "DIC(2025)")
        self.assertEqual(desc_oct[2], "ENE(2026)")
        self.assertEqual(desc_oct[-1], "OCT(2026)")

    def test_specific_operational_windows_descriptions(self):
        """
        Verifica las descripciones exactas de las ventanas de 12 meses para los casos obligatorios:
        - Agosto 2026 (mes eval = Julio 2026): AGO(2025) .. JUL(2026)
        - Marzo 2026 (mes eval = Febrero 2026): MAR(2025) .. FEB(2026)
        - Enero 2027 (mes eval = Diciembre 2026): ENE(2026) .. DIC(2026)
        """
        # Caso Agosto 2026 (M_eval = 7, Y_eval = 2026) -> Ago 2025 a Jul 2026
        desc_ago = obtener_descripcion_ventana(2026, 7, longitud_ventana=12)
        self.assertEqual(len(desc_ago), 12)
        self.assertEqual(desc_ago[0], "AGO(2025)")
        self.assertEqual(desc_ago[-1], "JUL(2026)")

        # Caso Marzo 2026 (M_eval = 2, Y_eval = 2026) -> Mar 2025 a Feb 2026
        desc_mar = obtener_descripcion_ventana(2026, 2, longitud_ventana=12)
        self.assertEqual(len(desc_mar), 12)
        self.assertEqual(desc_mar[0], "MAR(2025)")
        self.assertEqual(desc_mar[-1], "FEB(2026)")

        # Caso Enero 2027 (M_eval = 12, Y_eval = 2026) -> Ene 2026 a Dic 2026
        desc_ene27 = obtener_descripcion_ventana(2026, 12, longitud_ventana=12)
        self.assertEqual(len(desc_ene27), 12)
        self.assertEqual(desc_ene27[0], "ENE(2026)")
        self.assertEqual(desc_ene27[-1], "DIC(2026)")

    def test_backwards_compatibility_6m(self):
        """Comprobar que el valor por defecto sigue siendo 6 meses."""
        v_default = extraer_ventana(self.df_synthetic, 2025, 10)
        self.assertEqual(len(v_default), 6)
        expected_6m = [17.0, 18.0, 19.0, 20.0, 21.0, 22.0]
        self.assertEqual(v_default, expected_6m)


if __name__ == "__main__":
    unittest.main()
