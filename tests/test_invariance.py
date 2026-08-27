import unittest
import sys
import os
import pandas as pd

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

from aanalogos import calcular_analogos, cargar_todas_oscilaciones


class TestInvariance(unittest.TestCase):
    """Validar invarianza matemática ante el orden de filas de entrada (eliminación de iloc posicional)."""

    @classmethod
    def setUpClass(cls):
        cls.oscilaciones = cargar_todas_oscilaciones(PROJECT_DIR)

    def test_shuffle_invariance(self):
        osc_shuffled = {
            k: v.sample(frac=1, random_state=123).reset_index(drop=True)
            for k, v in self.oscilaciones.items()
        }
        res_orig = calcular_analogos(2015, 10, ["AMO", "PDO", "TNA"], oscilaciones_cargadas=self.oscilaciones)
        res_shuf = calcular_analogos(2015, 10, ["AMO", "PDO", "TNA"], oscilaciones_cargadas=osc_shuffled)

        pd.testing.assert_frame_equal(res_orig.tabla_coincidencias, res_shuf.tabla_coincidencias)
        pd.testing.assert_frame_equal(res_orig.tabla_trazabilidad, res_shuf.tabla_trazabilidad)


if __name__ == "__main__":
    unittest.main()
