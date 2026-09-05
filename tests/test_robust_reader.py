"""
Pruebas unitarias y de regresión para el lector robusto de fuentes climáticas,
validación estructural no destructiva y actualización segura de series.
"""

import unittest
import os
import tempfile
import pandas as pd
import numpy as np

from aanalogos.data import (
    parse_linea_matriz_mensual,
    acomodaParaCSV,
    acomodaParaCSV_2,
    acomodaParaCSV_3,
    validar_estructura_serie,
    verificar_y_descargar_datos,
)


class TestRobustReader(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_regression_expected_13_fields_line_79_saw_14(self):
        """
        Prueba de regresión específica:
        Un archivo con formato NOAA PSL que contiene notas bibliográficas con comas
        (ej. 'AMO unsmoothed, detrended from the Kaplan SST V2' en línea 79)
        debe ser parseado limpiamente sin generar 'Error tokenizing data: Expected 13 fields in line 79, saw 14'.
        """
        psl_content = (
            " 1948 2023\n"
            " 2021    0.126    0.139    0.112    0.054    0.072    0.139    0.210    0.245    0.402    0.475    0.445    0.252\n"
            " 2022    0.176    0.133    0.009    0.110    0.197    0.199    0.136    0.358    0.662    0.483    0.282    0.218\n"
            " 2023    0.192  -99.990  -99.990  -99.990  -99.990  -99.990  -99.990  -99.990  -99.990  -99.990  -99.990  -99.990\n"
            "  -99.99\n"
            "  AMO unsmoothed, detrended from the Kaplan SST V2\n"
            "  Calculated at NOAA PSL1\n"
            "  http://www.psl.noaa.gov/data/timeseries/AMO/\n"
        )
        txt_path = os.path.join(self.test_dir, "dataAMO.txt")
        csv_path = os.path.join(self.test_dir, "dataAMO.csv")

        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(psl_content)

        ok = acomodaParaCSV(txt_path, csv_path)
        self.assertTrue(ok)
        self.assertTrue(os.path.exists(csv_path))

        df = pd.read_csv(csv_path)
        self.assertEqual(len(df), 3)
        self.assertEqual(list(df["YEAR"]), [2021, 2022, 2023])
        self.assertAlmostEqual(df.iloc[0]["ENE"], 0.126)
        self.assertAlmostEqual(df.iloc[2]["ENE"], 0.192)
        self.assertAlmostEqual(df.iloc[2]["FEB"], -99.99)

    def test_variable_whitespace_and_compact_floats(self):
        """
        Verifica el manejo de espacios irregulares y números negativos pegados
        (ej. '-2.4-999.9-999.9' en SOI).
        """
        line_compact = "2026   1.1   1.4   1.2  -0.6  -0.9  -1.4  -2.4-999.9-999.9-999.9-999.9-999.9"
        row = parse_linea_matriz_mensual(line_compact)
        self.assertIsNotNone(row)
        self.assertEqual(row[0], 2026)
        self.assertAlmostEqual(row[1], 1.1)
        self.assertAlmostEqual(row[7], -2.4)
        self.assertAlmostEqual(row[8], -999.9)
        self.assertAlmostEqual(row[12], -999.9)

    def test_partial_year_publication_with_missing_months(self):
        """
        Verifica que un año parcialmente publicado (ej. 2026 con solo 5 meses)
        rellene adecuadamente los meses restantes con np.nan.
        """
        line_partial = "2026 -0.4 -0.1 0.1 0.5 1.0"
        row = parse_linea_matriz_mensual(line_partial)
        self.assertIsNotNone(row)
        self.assertEqual(row[0], 2026)
        self.assertAlmostEqual(row[1], -0.4)
        self.assertAlmostEqual(row[5], 1.0)
        self.assertTrue(np.isnan(row[6]))
        self.assertTrue(np.isnan(row[12]))

    def test_citations_and_text_footers_ignored_as_data(self):
        """
        Verifica que líneas de citas con años (ej. '2001 : The tropical Western Hemisphere...')
        sean ignoradas y no interpretadas como registros de datos climáticos.
        """
        citation_line = "2001 : The tropical Western Hemisphere warm pool, Wang & Enfield"
        row = parse_linea_matriz_mensual(citation_line)
        self.assertIsNone(row)

        header_line = " 1948 2026"
        self.assertIsNone(parse_linea_matriz_mensual(header_line))

        sentinel_line = " -99.99"
        self.assertIsNone(parse_linea_matriz_mensual(sentinel_line))

    def test_structural_validation_rules(self):
        """Verifica las reglas del validador estructural de series."""
        df_valid = pd.DataFrame({
            "YEAR": list(range(2000, 2021)),
            **{m: [0.5] * 21 for m in ["ENE", "FEB", "MAR", "ABR", "MAY", "JUN", "JUL", "AGO", "SET", "OCT", "NOV", "DIC"]}
        })
        valido, msg = validar_estructura_serie(df_valid, "TEST")
        self.assertTrue(valido)

        df_incompleto = df_valid.drop(columns=["DIC"])
        valido, msg = validar_estructura_serie(df_incompleto, "TEST")
        self.assertFalse(valido)
        self.assertIn("faltan las columnas", msg)

        df_dup = df_valid.copy()
        df_dup.iloc[5, df_dup.columns.get_loc("YEAR")] = 2000
        valido, msg = validar_estructura_serie(df_dup, "TEST")
        self.assertFalse(valido)
        self.assertIn("duplicados", msg)

        df_str = df_valid.copy()
        df_str["ENE"] = ["corrupto"] * len(df_str)
        valido, msg = validar_estructura_serie(df_str, "TEST")
        self.assertFalse(valido)
        self.assertIn("numéricos", msg)

        df_truncado = df_valid.iloc[:5]
        valido, msg = validar_estructura_serie(df_truncado, "TEST", df_previo=df_valid)
        self.assertFalse(valido)

    def test_csu_direct_csv_parsing(self):
        """Verifica la ingesta correcta de fuentes directas CSV (como CSU AMO)."""
        csv_csu = (
            "Year,Jan,Feb,Mar,Apr,May,Jun,Jul,Aug,Sep,Oct,Nov,Dec\n"
            "2024,0.53,0.35,0.20,0.49,1.04,0.74,0.62,0.11,0.95,1.35,1.92,0.25\n"
            "2025,1.15,0.44,0.33,0.41,0.30,-0.72,-0.38,-0.22,-0.90,0.46,0.72,0.42\n"
        )
        in_path = os.path.join(self.test_dir, "csu_raw.csv")
        out_path = os.path.join(self.test_dir, "dataAMO_CSU.csv")

        with open(in_path, "w", encoding="utf-8") as f:
            f.write(csv_csu)

        ok = acomodaParaCSV(in_path, out_path)
        self.assertTrue(ok)
        df = pd.read_csv(out_path)
        self.assertEqual(len(df), 2)
        self.assertIn("ENE", df.columns)
        self.assertIn("DIC", df.columns)
        self.assertAlmostEqual(df.iloc[0]["MAY"], 1.04)


if __name__ == "__main__":
    unittest.main()
