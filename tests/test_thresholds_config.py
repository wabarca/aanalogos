"""
Pruebas para umbrales configurables por el usuario y trazabilidad.
"""

import unittest
from aanalogos.engine import calcular_analogos
from aanalogos.config import obtener_umbrales_metodologicos
from aanalogos.data import cargar_todas_oscilaciones


class TestThresholdsConfig(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.oscilaciones = cargar_todas_oscilaciones()

    def test_custom_thresholds_applied(self):
        """Verificar que umbrales personalizados se aplican y se reflejan en la trazabilidad."""
        # Caso con umbrales muy estrictos (r > 0.99, MAD < 0.01)
        umbrales_estrictos = {
            "AMO": (0.99, 0.01),
            "PDO": (0.99, 0.01),
            "TNA": (0.99, 0.01)
        }
        res_estricto = calcular_analogos(
            year_objetivo=2015,
            mes_objetivo=10,
            indices=["AMO", "PDO", "TNA"],
            umbrales_personalizados=umbrales_estrictos,
            oscilaciones_cargadas=self.oscilaciones
        )
        self.assertTrue(res_estricto.es_valido)
        # Con umbrales cuasi-imposibles, todos los totales deben ser 0
        self.assertEqual(int(res_estricto.tabla_coincidencias["Total"].max()), 0)

        # Verificar que la trazabilidad registró los umbrales personalizados
        traz = res_estricto.tabla_trazabilidad
        self.assertEqual(traz["Umbral_r"].iloc[0], 0.99)
        self.assertEqual(traz["Umbral_MAD"].iloc[0], 0.01)

    def test_restore_default_thresholds(self):
        """Verificar que obtener_umbrales_metodologicos devuelve los valores oficiales."""
        defs = obtener_umbrales_metodologicos()
        self.assertEqual(defs["AMO"], (0.6, 0.3))
        self.assertEqual(defs["PDO"], (0.4, 0.6))
        self.assertEqual(defs["TNA"], (0.5, 0.3))


if __name__ == "__main__":
    unittest.main()
