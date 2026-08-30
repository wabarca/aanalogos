import unittest
import sys
import os
import pandas as pd

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

from aanalogos import calcular_analogos, ResultadoAnalogos, cargar_todas_oscilaciones


class TestRegression(unittest.TestCase):
    """Prueba de regresión científica estricta contra el caso de referencia validado."""

    @classmethod
    def setUpClass(cls):
        cls.oscilaciones = cargar_todas_oscilaciones(PROJECT_DIR)

    def test_benchmark_2015_m10_amo_pdo_tna(self):
        """Validar caso de referencia: 2015, Octubre, AMO + PDO + TNA.

        Benchmark certificado con fuente PDO oficial NOAA PSL (pdo.data).
        Con esta fuente, 1957 obtiene PDO=0 (Pearson=-0.53, fuera de umbral r>=0.4),
        por lo que su Total=1. El séptimo lugar del TOP 7 pasa a 2022.
        """
        res = calcular_analogos(2015, 10, ["AMO", "PDO", "TNA"], oscilaciones_cargadas=self.oscilaciones)
        
        self.assertTrue(res.es_valido)
        self.assertEqual(len(res.anios_candidatos), 74)
        self.assertNotIn(2015, res.anios_candidatos)
        
        # Verificar TOP 6 años análogos con Total=2 (AMO + TNA)
        top_6_total2 = [2021, 2014, 2012, 2003, 2001, 1990]
        top_7_obtenidos = res.tabla_coincidencias.head(7).index.tolist()
        
        for y in top_6_total2:
            self.assertIn(y, top_7_obtenidos)
            self.assertEqual(res.tabla_coincidencias.loc[y, "Total"], 2)

        # El 7° lugar es 2022 (Total=1, solo AMO)
        self.assertIn(2022, top_7_obtenidos)
        self.assertEqual(res.tabla_coincidencias.loc[2022, "Total"], 1)

        # Verificar métricas específicas de 1957 con fuente PSL (AMO=1, PDO=0, TNA=0)
        df_tr = res.tabla_trazabilidad
        tr_1957 = df_tr[df_tr["YEAR"] == 1957].set_index("Indice")
        self.assertAlmostEqual(tr_1957.loc["AMO", "Pearson"], 0.8322, places=4)
        self.assertAlmostEqual(tr_1957.loc["AMO", "MAD"], 0.0868, places=4)
        self.assertEqual(tr_1957.loc["AMO", "Coincidencia"], 1)

        # PDO 1957 vs 2015: tendencia opuesta (r=-0.53), sin coincidencia
        self.assertAlmostEqual(tr_1957.loc["PDO", "Pearson"], 0.2909, places=4)
        self.assertAlmostEqual(tr_1957.loc["PDO", "MAD"], 0.5667, places=4)
        self.assertEqual(tr_1957.loc["PDO", "Coincidencia"], 0)

        self.assertAlmostEqual(tr_1957.loc["TNA", "Pearson"], 0.7439, places=4)
        self.assertAlmostEqual(tr_1957.loc["TNA", "MAD"], 0.3367, places=4)
        self.assertEqual(tr_1957.loc["TNA", "Coincidencia"], 0)


if __name__ == "__main__":
    unittest.main()
