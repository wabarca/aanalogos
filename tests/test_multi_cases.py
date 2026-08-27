import unittest
import sys
import os

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

from aanalogos import calcular_analogos, cargar_todas_oscilaciones


class TestMultiCases(unittest.TestCase):
    """Validación multi-caso climatológica (7 escenarios)."""

    @classmethod
    def setUpClass(cls):
        cls.oscilaciones = cargar_todas_oscilaciones(PROJECT_DIR)

    def test_multiple_climatological_scenarios(self):
        casos = [
            (2015, 10, ["AMO", "PDO", "TNA"], 72),
            (1998, 10, ["AMO", "PDO", "TNA"], 72),
            (2009, 10, ["AMO", "PDO", "TNA"], 72),
            (2020, 10, ["AMO", "PDO", "TNA"], 72),
            (2015, 2,  ["AMO", "PDO", "TNA"], 71),
            (2015, 5,  ["AMO", "PDO", "TNA"], 71),
            (2015, 6,  ["AMO", "PDO", "TNA"], 72),
        ]
        for y, m, inds, cands_exp in casos:
            res = calcular_analogos(y, m, inds, oscilaciones_cargadas=self.oscilaciones)
            self.assertTrue(res.es_valido, f"Fallo en caso ({y}, {m})")
            self.assertEqual(len(res.anios_candidatos), cands_exp, f"Discrepancia en candidatos ({y}, {m})")
            self.assertNotIn(y, res.anios_candidatos)


if __name__ == "__main__":
    unittest.main()
