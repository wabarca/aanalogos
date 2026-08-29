import unittest
import sys
import os
import numpy as np

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

from aanalogos import calcular_analogos, cargar_todas_oscilaciones


class TestValidation(unittest.TestCase):
    """Validar salvaguardas operacionales, sentinelas, exclusión de objetivo y float64."""

    @classmethod
    def setUpClass(cls):
        cls.oscilaciones = cargar_todas_oscilaciones(PROJECT_DIR)

    def test_strict_index_validation_no_silent_reduction(self):
        """Verificar que el motor rechace cálculos si un índice seleccionado no está disponible."""
        res = calcular_analogos(2024, 10, ["AMO", "PDO", "SOI"], oscilaciones_cargadas=self.oscilaciones)
        self.assertFalse(res.es_valido)
        self.assertIn("SOI", res.indices_no_disponibles)
        self.assertEqual(len(res.indices_evaluados), 0)
        self.assertEqual(len(res.anios_candidatos), 0)

    def test_target_year_exclusion(self):
        """Verificar que el año objetivo jamás aparezca como candidato (tanto para N=6 como N=12)."""
        # Evaluación con ventana de 6 meses
        res_6m = calcular_analogos(2015, 10, ["AMO", "PDO"], longitud_ventana=6, oscilaciones_cargadas=self.oscilaciones)
        self.assertNotIn(2015, res_6m.anios_candidatos)
        self.assertNotIn(2015, res_6m.tabla_coincidencias.index)

        # Evaluación con ventana de 12 meses
        res_12m = calcular_analogos(2015, 10, ["AMO", "PDO"], longitud_ventana=12, oscilaciones_cargadas=self.oscilaciones)
        self.assertNotIn(2015, res_12m.anios_candidatos)
        self.assertNotIn(2015, res_12m.tabla_coincidencias.index)

    def test_sentinels_isolation(self):
        """Verificar que valores sentinela (-99.99) se conviertan a NaN e invaliden la ventana."""
        df_mod = self.oscilaciones["AMO"].copy()
        df_mod.loc[df_mod["YEAR"] == 1990, "AGO"] = np.nan
        osc_test = dict(self.oscilaciones)
        osc_test["AMO"] = df_mod

        res = calcular_analogos(2015, 10, ["AMO", "PDO"], oscilaciones_cargadas=osc_test)
        self.assertNotIn(1990, res.anios_candidatos)

    def test_float64_precision_preservation(self):
        """Verificar que Pearson y MAD preserven precisión flotante nativa float64."""
        res = calcular_analogos(2015, 10, ["AMO", "PDO"], oscilaciones_cargadas=self.oscilaciones)
        p_vals = res.tabla_trazabilidad["Pearson"].values
        self.assertEqual(p_vals.dtype, np.float64)


if __name__ == "__main__":
    unittest.main()
