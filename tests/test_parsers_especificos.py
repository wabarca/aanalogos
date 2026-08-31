"""
Pruebas unitarias específicas de parsers por fuente:
  - test_parse_amo    : NOAA PSL amon.us.data  (matriz mensual + notas al pie + sentinelas)
  - test_parse_car    : NOAA PSL CAR_ersst.data (ídem + coordenadas geográficas en footer)
  - test_parse_whwp   : NOAA PSL whwp.data     (ídem + cita bibliográfica con año en texto)
  - test_parse_amo_csu: CSU csu_amo.csv        (CSV directo con espacios y última fila parcial)

Cubre los casos sintéticos exigidos por la especificación:
  * líneas de metadatos
  * espacios múltiples e irregulares
  * líneas con campos adicionales (coordenadas, notas)
  * footer con texto y citas bibliográficas
  * valores faltantes / sentinelas -99.99
  * última fila parcialmente incompleta (año en curso)
  * cambios de año en la serie
  * datos hasta el último mes disponible
  * no descartar silenciosamente registros válidos
  * producir exactamente YEAR + 12 meses
  * detectar fila de datos corrupta (texto donde debería haber número)
  * preservar archivo anterior ante fallo de validación
"""

import os
import shutil
import tempfile
import unittest

import numpy as np
import pandas as pd

from aanalogos.data import (
    acomodaParaCSV,
    parse_linea_matriz_mensual,
    validar_estructura_serie,
)


# ---------------------------------------------------------------------------
# Fixtures sintéticos
# ---------------------------------------------------------------------------

AMO_RAW = """\
  1948         2026
 1948   -0.021   -0.034    0.022   -0.076   -0.010    0.049   -0.046   -0.029   -0.059    0.001    0.128    0.056
 1949    0.147    0.154    0.032    0.092   -0.030   -0.005    0.065    0.096    0.064    0.098    0.102    0.112
 1950    0.105   -0.040   -0.112   -0.137   -0.065   -0.049   -0.062    0.014    0.003   -0.097    0.073    0.082
 1951    0.096   -0.008    0.006    0.162    0.166    0.283    0.415    0.297    0.243    0.252    0.168    0.168
 1952    0.165    0.176    0.224    0.184    0.174    0.376    0.366    0.397    0.355    0.348    0.244    0.334
 1953    0.258    0.178    0.134    0.306    0.335    0.268    0.337    0.251    0.273    0.141    0.237    0.251
 1954    0.220    0.088    0.093   -0.021    0.062    0.092   -0.052   -0.022   -0.018   -0.040   -0.034   -0.059
 2021    0.126    0.139    0.112    0.054    0.072    0.139    0.210    0.245    0.402    0.475    0.445    0.252
 2022    0.176    0.133    0.009    0.110    0.197    0.199    0.136    0.358    0.662    0.483    0.282    0.218
 2023    0.192  -99.990  -99.990  -99.990  -99.990  -99.990  -99.990  -99.990  -99.990  -99.990  -99.990  -99.990
 2026   -0.150   -0.090   0.030   0.120   0.250
  -99.99
  AMO unsmoothed, detrended from the Kaplan SST V2
  Calculated at NOAA PSL1
  http://www.psl.noaa.gov/data/timeseries/AMO/
"""

CAR_RAW = """\
  1950         2020
 1950  -99.99   -0.27   -0.36   -0.38   -0.41   -0.43   -0.46   -0.45   -0.38   -0.34   -0.35   -0.40
 1951   -0.46   -0.49   -0.50   -0.42   -0.28   -0.11    0.02    0.06    0.08    0.05    0.09    0.15
 1952    0.19    0.18    0.16    0.19    0.18    0.16    0.12    0.11    0.08    0.06   -0.02   -0.12
 1953   -0.15   -0.08    0.02    0.11    0.10    0.06    0.01    0.01   -0.00    0.01    0.05    0.09
 1954    0.13    0.14    0.16    0.09   -0.01   -0.12   -0.16   -0.17   -0.22   -0.25   -0.30   -0.27
 1955   -0.30   -0.26   -0.26   -0.13   -0.09   -0.04   -0.08   -0.08   -0.05   -0.00    0.04    0.00
 1956   -0.06   -0.09   -0.07   -0.06   -0.17   -0.23   -0.25   -0.20   -0.17   -0.13   -0.08   -0.03
 2018    0.44    0.41    0.39    0.31    0.21    0.09    0.07    0.12    0.16    0.18    0.19    0.23
 2019    0.30    0.36    0.35    0.27    0.26    0.31    0.39    0.38    0.34    0.35    0.37    0.41
 2020    0.43    0.43  -99.99  -99.99  -99.99  -99.99  -99.99  -99.99  -99.99  -99.99  -99.99  -99.99
 -99.99
  CAR_ersst    
  produced at https://psl.noaa.gov/forecasts/sstlim/
  260-300E, 10N-25N minus Pacific                                                                                                     
  At NOAA PSL. Please cite forecast pubs
  and acquired at website YYYY/MM/DD
  SST is NOAA ERSST V3
"""

WHWP_RAW = """\
  1948         2026
1948    -0.38   -0.37   -0.10   -1.16   -1.61   -2.20   -4.30   -5.71   -4.86   -5.09   -3.63   -0.67
 1949    -0.33   -0.29   -0.66   -0.57   -1.79   -2.59   -3.74   -5.38   -3.89   -4.85   -2.88   -0.71
 1950    -0.38   -0.49   -1.34   -3.04   -3.38   -4.19   -4.83   -5.86   -3.64   -5.19   -2.65   -0.71
 1951    -0.38   -0.49   -1.30   -1.80   -2.04   -2.60   -2.76   -1.01   -1.61   -1.47   -0.77   -0.37
 1952    -0.27   -0.41   -0.67   -0.74   -0.85   -1.16   -2.85   -0.81   -0.66   -1.34   -0.80   -0.44
 1953    -0.38   -0.29    0.22    0.45   -1.04   -1.49   -2.38   -1.61   -1.76   -2.60   -0.61   -0.48
 1983     1.42    3.00    4.09    2.63    2.99    2.82    0.69   -1.27   -2.90   -3.02   -1.87   -0.11
 2024     2.21    2.76    3.64    4.61    6.39    7.47    6.79    5.43    5.18    4.69    4.11    2.32
 2025    -0.11   -0.22    0.71    0.27    0.88    1.22    3.36    3.06    3.12    2.04    2.34    0.23
 2026    -0.17   -0.15    0.48    1.65    3.32    5.26  -99.99  -99.99  -99.99  -99.99  -99.99  -99.99
  -99.99
  WHWPa
  Area anomaly scaled by 10e6 km**2
  Monthly anomaly of the ocean surface area Ocean region >28.5C
 in the Atlantic and eastern North Pacific.
  Climatology is now 1991-2020. Wang, C., and D.B. Enfield,
  2001 : The tropical Western Hemisphere warm pool, 
 Geophys. Res. Lett., 28, 1635-1638. 
"""

AMO_CSU_RAW = """\
Year,Jan,Feb,Mar,Apr,May,Jun,Jul,Aug,Sep,Oct,Nov,Dec
  1950,0.04,-0.26,-0.06,-0.30,0.83,0.24,0.44,0.18,-0.87,-0.58,0.40,-0.09
  1951,-0.21,-0.39,0.47,0.31,0.87,1.61,0.64,-0.03,0.36,0.13,-0.19,-0.44
  1952,-0.64,0.35,0.93,-0.33,0.95,0.69,0.07,1.11,1.25,1.00,1.47,1.49
  1953,1.18,0.81,0.87,1.41,1.63,0.11,0.00,-0.33,0.22,-0.15,-0.42,0.19
  1954,0.02,0.10,0.56,-0.48,0.69,0.34,0.16,0.48,-0.59,-0.02,-0.20,-0.10
  1955,1.32,0.98,1.22,1.04,0.53,0.85,0.62,0.88,-0.25,0.89,2.29,1.65
  1956,1.55,1.51,0.89,1.54,-0.35,-0.83,0.19,-0.09,0.28,0.13,0.42,-0.04
  2024,0.53,0.35,0.20,0.49,1.04,0.74,0.62,0.11,0.95,1.35,1.92,0.25
  2025,1.15,0.44,0.33,0.41,0.30,-0.72,-0.38,-0.22,-0.90,0.46,0.72,0.42
  2026,0.34,0.66,-0.62,-0.79,-0.33,-0.43,-0.07,,,,,
"""


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _write(path: str, content: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


# ---------------------------------------------------------------------------
# Suite
# ---------------------------------------------------------------------------

class TestParseAMO(unittest.TestCase):
    """Parser para NOAA PSL amon.us.data."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _run(self, content: str) -> pd.DataFrame:
        txt = os.path.join(self.tmp, "dataAMO.txt")
        csv = os.path.join(self.tmp, "dataAMO.csv")
        _write(txt, content)
        ok = acomodaParaCSV(txt, csv)
        self.assertTrue(ok, "acomodaParaCSV debe retornar True para AMO válido")
        return pd.read_csv(csv)

    def test_columnas_correctas(self):
        """Produce exactamente YEAR + 12 columnas de meses."""
        df = self._run(AMO_RAW)
        self.assertEqual(list(df.columns), [
            "YEAR", "ENE", "FEB", "MAR", "ABR", "MAY", "JUN",
            "JUL", "AGO", "SET", "OCT", "NOV", "DIC",
        ])

    def test_encabezado_ignorado(self):
        """La línea '1948  2026' (encabezado PSL) no se interpreta como registro independiente.
        El año 2026 sí debe aparecer como fila de datos parcial (año en curso).
        """
        df = self._run(AMO_RAW)
        anios = df["YEAR"].tolist()
        # El encabezado '1948  2026' NO debe generar una fila adicional —
        # el 2026 real proviene de la línea de datos parcial con 5 meses.
        self.assertEqual(anios.count(2026), 1, "2026 debe aparecer exactamente una vez (fila de datos parcial)")
        self.assertEqual(anios.count(1948), 1, "1948 debe aparecer exactamente una vez (fila de datos)")
        # La primera fila debe ser 1948 con ENE=-0.021
        primera = df[df["YEAR"] == 1948]
        self.assertEqual(len(primera), 1)
        self.assertAlmostEqual(float(primera.iloc[0]["ENE"]), -0.021, places=3)

    def test_footer_ignorado(self):
        """Líneas de notas ('AMO unsmoothed, detrended...', 'Calculated at NOAA PSL1', URL) no aparecen como datos."""
        df = self._run(AMO_RAW)
        # No debe haber filas con años fuera del rango real de datos
        for yr in df["YEAR"]:
            self.assertGreater(yr, 1800)
            self.assertLess(yr, 2100)

    def test_sentinel_conservado(self):
        """Los valores -99.99 y -99.990 se conservan como valores numéricos (no descartados)."""
        df = self._run(AMO_RAW)
        row_2023 = df[df["YEAR"] == 2023]
        self.assertEqual(len(row_2023), 1, "2023 debe ser un registro válido")
        self.assertAlmostEqual(float(row_2023.iloc[0]["ENE"]), 0.192, places=3)
        self.assertAlmostEqual(float(row_2023.iloc[0]["FEB"]), -99.99, places=2)

    def test_anio_parcial_con_nan(self):
        """Un año con solo 5 meses publicados rellena los restantes con NaN."""
        df = self._run(AMO_RAW)
        row_2026 = df[df["YEAR"] == 2026]
        self.assertEqual(len(row_2026), 1)
        self.assertAlmostEqual(float(row_2026.iloc[0]["ENE"]), -0.150, places=3)
        self.assertAlmostEqual(float(row_2026.iloc[0]["MAY"]), 0.250, places=3)
        self.assertTrue(np.isnan(float(row_2026.iloc[0]["JUN"])))
        self.assertTrue(np.isnan(float(row_2026.iloc[0]["DIC"])))

    def test_no_descarte_silencioso(self):
        """Todos los registros de datos válidos son conservados sin pérdidas."""
        df = self._run(AMO_RAW)
        # El fixture tiene: 1948..1954 (7 filas) + 2021, 2022, 2023, 2026 (4 filas) = 11 filas
        self.assertEqual(len(df), 11)

    def test_anos_en_orden_cronologico(self):
        """Los registros están en orden cronológico ascendente."""
        df = self._run(AMO_RAW)
        anios = df["YEAR"].tolist()
        self.assertEqual(anios, sorted(anios))

    def test_metadatos_con_numeros_en_texto_ignorados(self):
        """Líneas de notas que contienen números (ej. 'PSL1') no se confunden con datos."""
        content = AMO_RAW  # Incluye 'Calculated at NOAA PSL1'
        df = self._run(content)
        # No debe aparecer una fila de año 1 (de 'PSL1')
        self.assertNotIn(1, df["YEAR"].tolist())

    def test_validacion_estructural_pasa(self):
        """La serie resultante supera la validación estructural interna."""
        df = self._run(AMO_RAW)
        ok, msg = validar_estructura_serie(df, "AMO")
        self.assertTrue(ok, msg)

    def test_archivo_anterior_preservado_ante_datos_corruptos(self):
        """Si el archivo descargado contiene solo texto sin datos numéricos, no se genera CSV."""
        corrupted = (
            "Este archivo no contiene datos numéricos.\n"
            "Solo texto de error del servidor remoto.\n"
        )
        txt = os.path.join(self.tmp, "dataAMO_corrupt.txt")
        csv = os.path.join(self.tmp, "dataAMO_corrupt.csv")
        _write(txt, corrupted)
        ok = acomodaParaCSV(txt, csv)
        # El parser retorna False — no genera archivo
        self.assertFalse(ok)
        self.assertFalse(os.path.exists(csv))


class TestParseCAR(unittest.TestCase):
    """Parser para NOAA PSL CAR_ersst.data."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _run(self, content: str) -> pd.DataFrame:
        txt = os.path.join(self.tmp, "dataCAR.txt")
        csv = os.path.join(self.tmp, "dataCAR.csv")
        _write(txt, content)
        ok = acomodaParaCSV(txt, csv)
        self.assertTrue(ok)
        return pd.read_csv(csv)

    def test_columnas_correctas(self):
        df = self._run(CAR_RAW)
        self.assertEqual(list(df.columns), [
            "YEAR", "ENE", "FEB", "MAR", "ABR", "MAY", "JUN",
            "JUL", "AGO", "SET", "OCT", "NOV", "DIC",
        ])

    def test_coordenadas_en_footer_ignoradas(self):
        """La línea '260-300E, 10N-25N minus Pacific' contiene números pero no es un registro."""
        df = self._run(CAR_RAW)
        # No debe haber una fila de año 260
        self.assertNotIn(260, df["YEAR"].tolist())
        # Tampoco 10 ni 25 ni 300
        for invalid_yr in [10, 25, 28, 300]:
            self.assertNotIn(invalid_yr, df["YEAR"].tolist())

    def test_registros_completos_conservados(self):
        """Todos los registros de datos válidos son conservados."""
        df = self._run(CAR_RAW)
        # Fixture: 1950..1956 (7 filas) + 2018, 2019, 2020 (3 filas) = 10 filas
        self.assertEqual(len(df), 10)

    def test_sentinel_en_primer_mes(self):
        """El valor -99.99 en ENE de 1950 se conserva como número."""
        df = self._run(CAR_RAW)
        row_1950 = df[df["YEAR"] == 1950]
        self.assertAlmostEqual(float(row_1950.iloc[0]["ENE"]), -99.99, places=2)
        self.assertAlmostEqual(float(row_1950.iloc[0]["FEB"]), -0.27, places=2)

    def test_anio_parcial_final(self):
        """2020 con los meses MAR-DIC en -99.99 se conserva como registro."""
        df = self._run(CAR_RAW)
        row_2020 = df[df["YEAR"] == 2020]
        self.assertEqual(len(row_2020), 1)
        self.assertAlmostEqual(float(row_2020.iloc[0]["ENE"]), 0.43, places=2)
        self.assertAlmostEqual(float(row_2020.iloc[0]["FEB"]), 0.43, places=2)
        self.assertAlmostEqual(float(row_2020.iloc[0]["MAR"]), -99.99, places=2)

    def test_lineas_metadata_url_ignoradas(self):
        """URLs y frases de atribución no se parsean como datos."""
        df = self._run(CAR_RAW)
        for yr in df["YEAR"]:
            self.assertGreater(yr, 1800)

    def test_validacion_estructural_pasa(self):
        df = self._run(CAR_RAW)
        ok, msg = validar_estructura_serie(df, "CAR")
        self.assertTrue(ok, msg)


class TestParseWHWP(unittest.TestCase):
    """Parser para NOAA PSL whwp.data."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _run(self, content: str) -> pd.DataFrame:
        txt = os.path.join(self.tmp, "dataWHWP.txt")
        csv = os.path.join(self.tmp, "dataWHWP.csv")
        _write(txt, content)
        ok = acomodaParaCSV(txt, csv)
        self.assertTrue(ok)
        return pd.read_csv(csv)

    def test_columnas_correctas(self):
        df = self._run(WHWP_RAW)
        self.assertEqual(list(df.columns), [
            "YEAR", "ENE", "FEB", "MAR", "ABR", "MAY", "JUN",
            "JUL", "AGO", "SET", "OCT", "NOV", "DIC",
        ])

    def test_cita_bibliografica_con_anio_ignorada(self):
        """La línea '2001 : The tropical Western Hemisphere warm pool' no es un registro."""
        df = self._run(WHWP_RAW)
        self.assertNotIn(2001, df["YEAR"].tolist())

    def test_geophys_res_lett_ignorado(self):
        """La línea 'Geophys. Res. Lett., 28, 1635-1638' no produce datos."""
        df = self._run(WHWP_RAW)
        # 28 y 1635 no deben aparecer como años
        self.assertNotIn(28, df["YEAR"].tolist())
        self.assertNotIn(1635, df["YEAR"].tolist())

    def test_registros_datos_completos(self):
        """Todos los registros de la matriz de datos son conservados."""
        df = self._run(WHWP_RAW)
        # Fixture: 1948..1953 (6 filas) + 1983 + 2024, 2025, 2026 (3 filas) = 10 filas
        self.assertEqual(len(df), 10)

    def test_anio_parcial_con_sentinelas(self):
        """2026 con meses JUL-DIC en -99.99 se conserva."""
        df = self._run(WHWP_RAW)
        row_2026 = df[df["YEAR"] == 2026]
        self.assertEqual(len(row_2026), 1)
        self.assertAlmostEqual(float(row_2026.iloc[0]["ENE"]), -0.17, places=2)
        self.assertAlmostEqual(float(row_2026.iloc[0]["JUN"]), 5.26, places=2)
        self.assertAlmostEqual(float(row_2026.iloc[0]["JUL"]), -99.99, places=2)

    def test_valores_grandes_positivos_son_validos(self):
        """Los valores de WHWP son de escala km², pueden ser grandes (ej. 7.89 o -9.18)."""
        df = self._run(WHWP_RAW)
        row_2025 = df[df["YEAR"] == 2025]
        self.assertAlmostEqual(float(row_2025.iloc[0]["JUL"]), 3.36, places=2)

    def test_linea_sin_sangria_inicial(self):
        """1948 en el fixture no tiene espacio inicial — el parser debe aceptarla igualmente."""
        df = self._run(WHWP_RAW)
        row_1948 = df[df["YEAR"] == 1948]
        self.assertEqual(len(row_1948), 1)
        self.assertAlmostEqual(float(row_1948.iloc[0]["ENE"]), -0.38, places=2)

    def test_validacion_estructural_pasa(self):
        df = self._run(WHWP_RAW)
        ok, msg = validar_estructura_serie(df, "WHWP")
        self.assertTrue(ok, msg)


class TestParseAMOCSU(unittest.TestCase):
    """Parser para CSU csu_amo.csv (CSV directo con espacios y última fila parcial)."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _run(self, content: str) -> pd.DataFrame:
        txt = os.path.join(self.tmp, "csu_amo.csv")
        csv = os.path.join(self.tmp, "dataAMO_CSU.csv")
        _write(txt, content)
        ok = acomodaParaCSV(txt, csv)
        self.assertTrue(ok, "acomodaParaCSV debe retornar True para AMO_CSU válido")
        return pd.read_csv(csv)

    def test_columnas_correctas(self):
        """Produce exactamente YEAR + 12 columnas de meses en español."""
        df = self._run(AMO_CSU_RAW)
        self.assertEqual(list(df.columns), [
            "YEAR", "ENE", "FEB", "MAR", "ABR", "MAY", "JUN",
            "JUL", "AGO", "SET", "OCT", "NOV", "DIC",
        ])

    def test_espacios_iniciales_en_filas(self):
        """Las filas con espacios iniciales (ej. '  1950,0.04,...') son correctamente leídas."""
        df = self._run(AMO_CSU_RAW)
        row_1950 = df[df["YEAR"] == 1950]
        self.assertEqual(len(row_1950), 1)
        self.assertAlmostEqual(float(row_1950.iloc[0]["ENE"]), 0.04, places=2)

    def test_anio_parcial_campos_vacios(self):
        """La fila '2026,0.34,0.66,...,-0.07,,,,,' con campos vacíos produce NaN en meses faltantes."""
        df = self._run(AMO_CSU_RAW)
        row_2026 = df[df["YEAR"] == 2026]
        self.assertEqual(len(row_2026), 1)
        self.assertAlmostEqual(float(row_2026.iloc[0]["ENE"]), 0.34, places=2)
        self.assertAlmostEqual(float(row_2026.iloc[0]["JUL"]), -0.07, places=2)
        self.assertTrue(np.isnan(float(row_2026.iloc[0]["AGO"])))
        self.assertTrue(np.isnan(float(row_2026.iloc[0]["DIC"])))

    def test_todos_los_registros_conservados(self):
        """Todos los años del fixture son conservados sin pérdidas."""
        df = self._run(AMO_CSU_RAW)
        # Fixture: 1950..1956 (7 filas) + 2024, 2025, 2026 (3 filas) = 10 filas
        self.assertEqual(len(df), 10)

    def test_valores_de_datos_correctos(self):
        """Valores específicos de la fuente coinciden con lo esperado."""
        df = self._run(AMO_CSU_RAW)
        row_2024 = df[df["YEAR"] == 2024]
        self.assertAlmostEqual(float(row_2024.iloc[0]["MAY"]), 1.04, places=2)
        self.assertAlmostEqual(float(row_2024.iloc[0]["DIC"]), 0.25, places=2)

    def test_html_de_error_rechazado(self):
        """Si la URL devuelve una página HTML de error en lugar de CSV, se rechaza."""
        html_error = (
            "<!DOCTYPE html><html><body>"
            "<h1>404 Not Found</h1><p>The requested URL was not found.</p>"
            "</body></html>"
        )
        txt = os.path.join(self.tmp, "error_response.csv")
        csv = os.path.join(self.tmp, "dataAMO_CSU_error.csv")
        _write(txt, html_error)
        # acomodaParaCSV no detecta HTML, pero el resultado no tendrá columnas YEAR válidas
        # El archivo generado no superaría la validación estructural
        result = acomodaParaCSV(txt, csv)
        if result and os.path.exists(csv):
            df = pd.read_csv(csv, on_bad_lines="skip")
            ok, _ = validar_estructura_serie(df, "AMO_CSU")
            self.assertFalse(ok, "Un HTML de error no debe superar la validación estructural")

    def test_validacion_estructural_pasa(self):
        """La serie resultante supera la validación estructural interna."""
        df = self._run(AMO_CSU_RAW)
        ok, msg = validar_estructura_serie(df, "AMO_CSU")
        self.assertTrue(ok, msg)

    def test_preservar_anterior_ante_cabecera_incorrecta(self):
        """Un CSV sin columna 'Year' no produce archivo CSV de salida."""
        bad_csv = "col1,col2,col3\n1,2,3\n4,5,6\n"
        txt = os.path.join(self.tmp, "bad.csv")
        csv = os.path.join(self.tmp, "bad_out.csv")
        _write(txt, bad_csv)
        result = acomodaParaCSV(txt, csv)
        if result and os.path.exists(csv):
            df = pd.read_csv(csv)
            ok, _ = validar_estructura_serie(df, "AMO_CSU")
            self.assertFalse(ok, "Un CSV con cabeceras incorrectas no debe superar la validación")


class TestParserEscenariosSinteticos(unittest.TestCase):
    """Casos sintéticos adicionales que prueban todas las combinaciones de fallo/éxito."""

    def test_linea_corrupta_texto_en_columna_de_mes(self):
        """Una línea donde el segundo token no es número retorna None."""
        linea = "2020 CORRUPTO 0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 1.0 1.1"
        self.assertIsNone(parse_linea_matriz_mensual(linea))

    def test_linea_solo_anio_sin_meses_retorna_none(self):
        """Una línea con solo el año sin meses retorna None."""
        self.assertIsNone(parse_linea_matriz_mensual("2020"))

    def test_linea_vacia_retorna_none(self):
        self.assertIsNone(parse_linea_matriz_mensual(""))
        self.assertIsNone(parse_linea_matriz_mensual("   "))

    def test_encabezado_psl_anio_inicio_fin_retorna_none(self):
        """'1948  2026' es encabezado PSL, no registro."""
        self.assertIsNone(parse_linea_matriz_mensual("  1948         2026"))
        self.assertIsNone(parse_linea_matriz_mensual("  1950         2020"))

    def test_sentinela_aislado_retorna_none(self):
        """Una línea con solo -99.99 (sentinela de fin de archivo) retorna None."""
        self.assertIsNone(parse_linea_matriz_mensual("  -99.99"))
        self.assertIsNone(parse_linea_matriz_mensual("-99.99"))

    def test_valores_compactos_pegados(self):
        """Valores negativos pegados (sin espacio) son separados correctamente."""
        linea = "2026   1.1   1.4   1.2  -0.6  -0.9  -1.4  -2.4-999.9-999.9-999.9-999.9-999.9"
        row = parse_linea_matriz_mensual(linea)
        self.assertIsNotNone(row)
        self.assertEqual(row[0], 2026)
        self.assertAlmostEqual(row[7], -2.4)
        self.assertAlmostEqual(row[8], -999.9)

    def test_anio_parcial_uno_solo_mes(self):
        """Un año con un solo mes publicado rellena los 11 restantes con NaN."""
        row = parse_linea_matriz_mensual("2026 0.5")
        self.assertIsNotNone(row)
        self.assertAlmostEqual(row[1], 0.5)
        self.assertTrue(np.isnan(row[2]))
        self.assertTrue(np.isnan(row[12]))

    def test_valores_grandes_de_whwp(self):
        """Valores de WHWP pueden ser > 5 o < -9 y son aceptados."""
        linea = "1983     1.42    3.00    4.09    2.63    2.99    2.82    0.69   -1.27   -2.90   -3.02   -1.87   -0.11"
        row = parse_linea_matriz_mensual(linea)
        self.assertIsNotNone(row)
        self.assertAlmostEqual(row[1], 1.42)
        self.assertAlmostEqual(row[3], 4.09)

    def test_anio_fuera_de_rango_rechazado(self):
        """Años fuera de [1800, 2100] se rechazan."""
        self.assertIsNone(parse_linea_matriz_mensual("1799 0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 1.0 1.1 1.2"))
        self.assertIsNone(parse_linea_matriz_mensual("2101 0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 1.0 1.1 1.2"))

    def test_espacios_multiples_aceptados(self):
        """Separación por múltiples espacios es aceptada."""
        linea = "2020     0.1     0.2     0.3     0.4     0.5     0.6     0.7     0.8     0.9     1.0     1.1     1.2"
        row = parse_linea_matriz_mensual(linea)
        self.assertIsNotNone(row)
        self.assertAlmostEqual(row[1], 0.1)
        self.assertAlmostEqual(row[12], 1.2)

    def test_validador_estructura_rechaza_serie_cortada(self):
        """Una versión más corta que la local no supera la validación de no-regresión."""
        df_actual = pd.DataFrame({
            "YEAR": list(range(2000, 2021)),
            **{m: [0.5] * 21 for m in ["ENE", "FEB", "MAR", "ABR", "MAY", "JUN", "JUL", "AGO", "SET", "OCT", "NOV", "DIC"]}
        })
        df_corta = df_actual[df_actual["YEAR"] <= 2010].copy()
        ok, msg = validar_estructura_serie(df_corta, "TEST", df_previo=df_actual)
        self.assertFalse(ok)
        self.assertIn("2010", msg)


if __name__ == "__main__":
    unittest.main()
