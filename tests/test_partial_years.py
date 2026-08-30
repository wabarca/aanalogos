"""
Pruebas de ingestión y manejo de series mensuales con años parcialmente publicados.
"""

import os
import tempfile
import unittest
import numpy as np
import pandas as pd
import datetime

from aanalogos.data import acomodaParaCSV, acomodaParaCSV_2, acomodaParaCSV_3, cargar_todas_oscilaciones
from aanalogos.quality import limpiar_datos_indice
from aanalogos.catalog import (
    determinar_ultimo_mes_disponible,
    obtener_periodo_evaluacion_operacional,
    obtener_estado_fuentes,
    cargar_catalogo_indices
)


class TestPartialYears(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_partial_year_text_parser_acomodaParaCSV(self):
        """
        Verifica que acomodaParaCSV procese correctamente un archivo de texto donde
        2025 tiene 12 meses y 2026 tiene sólo 5 meses publicados (enero a mayo).
        """
        txt_path = os.path.join(self.temp_dir.name, "dataTest.txt")
        csv_path = os.path.join(self.temp_dir.name, "dataTest.csv")

        # Crear archivo de texto con 2025 (12 meses) y 2026 (5 meses)
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write("YEAR ENE FEB MAR ABR MAY JUN JUL AGO SET OCT NOV DIC\n")
            f.write("2025 -0.4 -0.2 -0.1 0.0 0.0 0.0 -0.1 -0.3 -0.4 -0.5 -0.6 -0.5\n")
            f.write("2026 -0.4 -0.1 0.1 0.5 1.0\n")

        ok = acomodaParaCSV(txt_path, csv_path)
        self.assertTrue(ok)

        # Leer CSV resultante
        df_raw = pd.read_csv(csv_path)
        df_clean = limpiar_datos_indice(df_raw)

        # 1. 2026 debe conservarse en el DataFrame
        self.assertIn(2026, df_clean["YEAR"].values)
        self.assertEqual(len(df_clean), 2)

        # 2. Verificar valores de 2026
        row_2026 = df_clean[df_clean["YEAR"] == 2026].iloc[0]
        self.assertAlmostEqual(row_2026["ENE"], -0.4)
        self.assertAlmostEqual(row_2026["FEB"], -0.1)
        self.assertAlmostEqual(row_2026["MAR"], 0.1)
        self.assertAlmostEqual(row_2026["ABR"], 0.5)
        self.assertAlmostEqual(row_2026["MAY"], 1.0)

        # 3. Junio a Diciembre deben ser NaN
        for mes in ["JUN", "JUL", "AGO", "SET", "OCT", "NOV", "DIC"]:
            self.assertTrue(np.isnan(row_2026[mes]), f"El mes {mes} de 2026 debe ser NaN")

        # 4. Probar determinación de último mes disponible para 2026
        osc = {"TEST": df_clean}
        # Con fecha de referencia en agosto de 2026
        y_disp, m_disp = determinar_ultimo_mes_disponible(osc, year=2026, fecha_referencia=datetime.date(2026, 8, 15))
        self.assertEqual(y_disp, 2026)
        self.assertEqual(m_disp, 5, "Mayo (5) debe ser identificado como el último mes disponible de 2026")

        # 5. Probar estado de fuentes
        df_health = obtener_estado_fuentes(osc, catalogo={"TEST": {"name": "Test Index", "institution": "Test"}})
        self.assertEqual(df_health.iloc[0]["Último Año"], 2026)
        self.assertIn("MAY (2026)", df_health.iloc[0]["Último Mes"])

    def test_partial_year_html_parser_regex_and_padding(self):
        """
        Verifica que el formateo para tablas HTML gestione adecuadamente filas parciales
        sin descartarlas.
        """
        txt_path = os.path.join(self.temp_dir.name, "dataONIv5_test.txt")
        csv_path = os.path.join(self.temp_dir.name, "dataONIv5_test.csv")

        with open(txt_path, "w", encoding="utf-8") as f:
            f.write("YEAR ENE FEB MAR ABR MAY JUN JUL AGO SET OCT NOV DIC\n")
            f.write("2024 1.9 1.6 1.3 0.8 0.5 0.2 0.1 -0.1 -0.2 -0.2 -0.3 -0.4\n")
            f.write("2025 -0.4 -0.2 -0.1 0.0 0.0 0.0 -0.1 -0.3 -0.4 -0.5 -0.6 -0.5\n")
            f.write("2026 -0.4 -0.1 0.1 0.5 1.0 -99.99 -99.99 -99.99 -99.99 -99.99 -99.99 -99.99\n")

        ok = acomodaParaCSV(txt_path, csv_path)
        self.assertTrue(ok)

        df = limpiar_datos_indice(pd.read_csv(csv_path))
        self.assertEqual(len(df), 3)
        row_2026 = df[df["YEAR"] == 2026].iloc[0]
        self.assertEqual(row_2026["MAY"], 1.0)
        self.assertTrue(np.isnan(row_2026["JUN"]))
        self.assertTrue(np.isnan(row_2026["DIC"]))

    def test_current_enso_series_availability(self):
        """
        Verifica el estado actual de las series ONIv5, ONIv6 y RONI en el repositorio local.
        """
        osc = cargar_todas_oscilaciones()
        for k in ["ONIv5", "ONIv6", "RONI"]:
            self.assertIn(k, osc)
            df = osc[k]
            self.assertGreaterEqual(len(df), 50)
            y_max = int(df["YEAR"].max())
            self.assertGreaterEqual(y_max, 2025)


if __name__ == "__main__":
    unittest.main()
