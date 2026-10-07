"""
Pruebas unitarias para el módulo de persistencia de checkpoints y mecanismo anti-sleep.
"""

import unittest
from aanalogos.checkpoint import (
    obtener_configuracion_defecto,
    validar_y_sanitizar_checkpoint,
    codificar_checkpoint,
    decodificar_checkpoint,
    generar_componente_cliente,
)
from aanalogos.config import UMBRALES_OSCILACIONES


class TestCheckpoint(unittest.TestCase):
    def test_obtener_configuracion_defecto(self):
        """Verifica que la configuración por defecto posea todos los campos necesarios."""
        cfg = obtener_configuracion_defecto()
        self.assertIn("indices", cfg)
        self.assertIn("modo_analisis", cfg)
        self.assertIn("longitud_ventana", cfg)
        self.assertIn("year_objetivo", cfg)
        self.assertIn("mes_objetivo", cfg)
        self.assertIn("tipo_reanalisis", cfg)
        self.assertIn("umbrales_usuario", cfg)
        self.assertIn("seccion", cfg)
        self.assertEqual(cfg["modo_analisis"], "Operacional")
        self.assertEqual(cfg["longitud_ventana"], 12)
        self.assertEqual(sorted(cfg["indices"]), sorted(["RONI", "TNA", "ONIv6"]))

    def test_validar_y_sanitizar_valid(self):
        """Verifica que un diccionario con valores válidos sea saneado y preservado."""
        datos = {
            "indices": ["AMO", "PDO"],
            "modo_analisis": "Reanálisis Histórico",
            "longitud_ventana": 6,
            "year_objetivo": 1997,
            "mes_objetivo": 11,
            "tipo_reanalisis": "Backtesting / Simulación Tiempo Real (Corte en $Y_{\\text{obj}}$)",
            "umbrales_usuario": {"AMO": [0.75, 0.20]},
            "seccion": "3. Análisis de años análogos",
        }
        res = validar_y_sanitizar_checkpoint(datos)
        self.assertEqual(res["indices"], ["AMO", "PDO"])
        self.assertEqual(res["modo_analisis"], "Reanálisis Histórico")
        self.assertEqual(res["longitud_ventana"], 6)
        self.assertEqual(res["year_objetivo"], 1997)
        self.assertEqual(res["mes_objetivo"], 11)
        self.assertIn("Backtesting", res["tipo_reanalisis"])
        self.assertEqual(res["umbrales_usuario"]["AMO"], (0.75, 0.20))

    def test_validar_y_sanitizar_invalid_values(self):
        """Verifica que entradas anómalas o corruptas sean sanitizadas a valores seguros."""
        datos_corruptos = {
            "indices": ["INDICE_INEXISTENTE", 12345],
            "modo_analisis": "MODO_HACK",
            "longitud_ventana": 999,
            "year_objetivo": 1800,  # fuera de rango
            "mes_objetivo": 25,     # fuera de rango
            "tipo_reanalisis": None,
            "umbrales_usuario": {"AMO": [999.0, -50.0]},  # umbrales fuera de rango físico
            "seccion": "SECCION_FALSA",
        }
        res = validar_y_sanitizar_checkpoint(datos_corruptos)
        self.assertEqual(res["indices"], ["RONI", "TNA", "ONIv6"])
        self.assertEqual(res["modo_analisis"], "Operacional")
        self.assertEqual(res["longitud_ventana"], 12)
        self.assertEqual(res["year_objetivo"], 2015)
        self.assertEqual(res["mes_objetivo"], 10)
        self.assertEqual(res["umbrales_usuario"]["AMO"], UMBRALES_OSCILACIONES["AMO"])

    def test_encode_decode_roundtrip(self):
        """Verifica la serialización y deserialización sin pérdida de información."""
        original = {
            "indices": ["CAR", "TNA", "WHWP"],
            "modo_analisis": "Reanálisis Histórico",
            "longitud_ventana": 6,
            "year_objetivo": 2005,
            "mes_objetivo": 8,
            "tipo_reanalisis": "Retrospectivo Completo (Todos los años históricos)",
            "umbrales_usuario": {k: list(v) for k, v in UMBRALES_OSCILACIONES.items()},
            "seccion": "3. Análisis de años análogos",
        }
        codificado = codificar_checkpoint(original)
        self.assertIsInstance(codificado, str)
        self.assertGreater(len(codificado), 20)

        decodificado = decodificar_checkpoint(codificado)
        self.assertEqual(decodificado["indices"], original["indices"])
        self.assertEqual(decodificado["modo_analisis"], original["modo_analisis"])
        self.assertEqual(decodificado["longitud_ventana"], original["longitud_ventana"])
        self.assertEqual(decodificado["year_objetivo"], original["year_objetivo"])
        self.assertEqual(decodificado["mes_objetivo"], original["mes_objetivo"])

    def test_decodificar_checkpoint_corrupto(self):
        """Verifica que una cadena corrupta no lance excepción y retorne configuración por defecto."""
        res = decodificar_checkpoint("NOT_A_VALID_BASE64_OR_JSON!!!")
        self.assertIsInstance(res, dict)
        self.assertEqual(res["modo_analisis"], "Operacional")

    def test_generar_componente_cliente(self):
        """Verifica que el componente HTML incluya los scripts de Keep-Alive y LocalStorage."""
        cfg = obtener_configuracion_defecto()
        html = generar_componente_cliente(cfg)
        self.assertIn("localStorage.setItem", html)
        self.assertIn("Worker", html)
        self.assertIn("_stcore/health", html)
        self.assertIn("aanalogos_user_checkpoint_v1", html)


if __name__ == "__main__":
    unittest.main()
