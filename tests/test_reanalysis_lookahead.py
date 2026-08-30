"""
Prueba de aislamiento temporal estricto en modo Reanálisis (prevención de look-ahead bias).
"""

import unittest
from aanalogos.engine import calcular_analogos
from aanalogos.data import cargar_todas_oscilaciones


class TestReanalysisLookAhead(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.oscilaciones = cargar_todas_oscilaciones()

    def test_strict_lookahead_cutoff_2015(self):
        """
        Al reanalizar el caso 2015 con max_year_corte=2015, ningún año > 2015
        puede aparecer como candidato ni ser considerado en la evaluación.
        """
        res = calcular_analogos(
            year_objetivo=2015,
            mes_objetivo=10,
            indices=["AMO", "PDO", "TNA"],
            longitud_ventana=6,
            max_year_corte=2015,
            modo_analisis="Reanálisis Histórico",
            oscilaciones_cargadas=self.oscilaciones
        )
        self.assertTrue(res.es_valido)
        # Verificar que el año objetivo 2015 no esté en los candidatos
        self.assertNotIn(2015, res.anios_candidatos)
        # Verificar que ningún año posterior a 2015 exista en candidatos ni en la tabla
        for y in res.anios_candidatos:
            self.assertLess(y, 2015, f"El año {y} supera el corte temporal de 2015 (Look-ahead bias detectado)")

        if len(res.tabla_trazabilidad) > 0:
            anios_traz = res.tabla_trazabilidad["YEAR"].unique()
            for y in anios_traz:
                self.assertLess(y, 2015)

    def test_retrospective_full_vs_backtesting(self):
        """
        Contrasta el Reanálisis Retrospectivo Completo (sin corte temporal)
        frente al Backtesting Estricto (corte en Y_obj).
        """
        # Modo A: Retrospectivo Completo (evalúa todo el registro histórico)
        res_full = calcular_analogos(
            year_objetivo=2015,
            mes_objetivo=10,
            indices=["AMO", "PDO", "TNA"],
            longitud_ventana=6,
            max_year_corte=None,
            modo_analisis="Reanálisis Histórico",
            oscilaciones_cargadas=self.oscilaciones
        )
        self.assertTrue(res_full.es_valido)
        self.assertEqual(len(res_full.anios_candidatos), 74)
        self.assertIn(2021, res_full.anios_candidatos)

        # Modo B: Backtesting Estricto (solo datos hasta Y_obj)
        res_backtest = calcular_analogos(
            year_objetivo=2015,
            mes_objetivo=10,
            indices=["AMO", "PDO", "TNA"],
            longitud_ventana=6,
            max_year_corte=2015,
            modo_analisis="Reanálisis Histórico",
            oscilaciones_cargadas=self.oscilaciones
        )
        self.assertTrue(res_backtest.es_valido)
        self.assertNotIn(2021, res_backtest.anios_candidatos)
        self.assertTrue(all(y < 2015 for y in res_backtest.anios_candidatos))


if __name__ == "__main__":
    unittest.main()
