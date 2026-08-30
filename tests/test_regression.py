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
        """Validar caso de referencia: 2015, Octubre, AMO + PDO + TNA."""
        res = calcular_analogos(2015, 10, ["AMO", "PDO", "TNA"], oscilaciones_cargadas=self.oscilaciones)
        
        self.assertTrue(res.es_valido)
        self.assertEqual(len(res.anios_candidatos), 74)
        self.assertNotIn(2015, res.anios_candidatos)
        
        # Verificar TOP 7 años análogos certificados
        top_7_esperados = [2021, 2014, 2012, 2003, 2001, 1990, 1957]
        top_7_obtenidos = res.tabla_coincidencias.head(7).index.tolist()
        
        for y in top_7_esperados:
            self.assertIn(y, top_7_obtenidos)
            self.assertEqual(res.tabla_coincidencias.loc[y, "Total"], 2)

        # Verificar métricas específicas de 1957 (AMO=1, PDO=1, TNA=0)
        df_tr = res.tabla_trazabilidad
        tr_1957 = df_tr[df_tr["YEAR"] == 1957].set_index("Indice")
        self.assertAlmostEqual(tr_1957.loc["AMO", "Pearson"], 0.8322, places=4)
        self.assertAlmostEqual(tr_1957.loc["AMO", "MAD"], 0.0868, places=4)
        self.assertEqual(tr_1957.loc["AMO", "Coincidencia"], 1)

        self.assertAlmostEqual(tr_1957.loc["PDO", "Pearson"], 0.6445, places=4)
        self.assertAlmostEqual(tr_1957.loc["PDO", "MAD"], 0.5517, places=4)
        self.assertEqual(tr_1957.loc["PDO", "Coincidencia"], 1)

        self.assertAlmostEqual(tr_1957.loc["TNA", "Pearson"], 0.7439, places=4)
        self.assertAlmostEqual(tr_1957.loc["TNA", "MAD"], 0.3367, places=4)
        self.assertEqual(tr_1957.loc["TNA", "Coincidencia"], 0)


if __name__ == "__main__":
    unittest.main()
