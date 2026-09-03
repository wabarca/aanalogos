"""
Pruebas unitarias para la visualización gráfica individual por índice.
Verifica la consistencia absoluta entre los resultados del motor y la figura generada.
"""

import unittest
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

from aanalogos.engine import calcular_analogos
from aanalogos.data import cargar_todas_oscilaciones
from aanalogos.charts import generar_grafico_individual_indice, formatear_mes_anio


class TestIndividualChart(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.oscilaciones = cargar_todas_oscilaciones()
        # Cálculo de referencia: 2015, mes 10, AMO + PDO + TNA
        cls.resultado = calcular_analogos(
            year_objetivo=2015,
            mes_objetivo=10,
            indices=["AMO", "PDO", "TNA"],
            longitud_ventana=6,
            oscilaciones_cargadas=cls.oscilaciones
        )
        assert cls.resultado.es_valido

    def test_formatear_mes_anio(self):
        """Verifica el formateo limpio de cadenas mes/año."""
        self.assertEqual(formatear_mes_anio("ABR(2025)"), "Abr 2025")
        self.assertEqual(formatear_mes_anio("OCT(2015)"), "Oct 2015")
        self.assertEqual(formatear_mes_anio("DIC 2020"), "Dic 2020")
        self.assertEqual(formatear_mes_anio("Mayo 2024"), "Mayo 2024")

    def test_chart_generation_valid(self):
        """Verifica que generar_grafico_individual_indice produce un objeto Figure válido."""
        fig = generar_grafico_individual_indice(self.resultado, "AMO")
        self.assertIsInstance(fig, plt.Figure)
        self.assertGreaterEqual(len(fig.axes), 2)  # ax1 y ax2 (twinx)
        plt.close(fig)

    def test_chart_consistency_with_engine_matches(self):
        """
        Verifica que los años resaltados en el gráfico coincidan exactamente con las coincidencias
        calculadas por el motor en la tabla de trazabilidad y se ubiquen en la zona superior.
        """
        traz = self.resultado.tabla_trazabilidad
        traz_amo = traz[traz["Indice"] == "AMO"]
        anios_coincidentes_motor = sorted(traz_amo[traz_amo["Coincidencia"] == 1]["YEAR"].tolist())

        fig = generar_grafico_individual_indice(self.resultado, "AMO")
        ax1 = fig.axes[0]

        anios_en_grafico = []
        for text in ax1.texts:
            # Los textos de los años coincidentes están en la parte superior con rotación de 45°
            try:
                val = int(text.get_text())
                if val in traz_amo["YEAR"].values:
                    anios_en_grafico.append(val)
                    self.assertEqual(text.get_rotation(), 45)
                    self.assertGreaterEqual(text.get_position()[1], 1.0)
            except ValueError:
                pass

        anios_en_grafico = sorted(anios_en_grafico)
        self.assertEqual(anios_coincidentes_motor, anios_en_grafico)
        plt.close(fig)

    def test_full_height_patches(self):
        """Verifica que los rectángulos verdes de años análogos abarquen prácticamente toda la altura del gráfico."""
        fig = generar_grafico_individual_indice(self.resultado, "AMO")
        ax1 = fig.axes[0]
        patches = [p for p in ax1.patches if isinstance(p, mpatches.FancyBboxPatch)]
        traz_amo = self.resultado.tabla_trazabilidad[self.resultado.tabla_trazabilidad["Indice"] == "AMO"]
        num_coincidencias = len(traz_amo[traz_amo["Coincidencia"] == 1])
        
        self.assertEqual(len(patches), num_coincidencias)
        for p in patches:
            # La altura del rectángulo debe cubrir prácticamente todo el eje Y (ej. >= 2.0)
            self.assertGreaterEqual(p.get_height(), 2.0)
        plt.close(fig)

    def test_chart_zero_matches_handled_gracefully(self):
        """Verifica que un caso con 0 coincidencias se grafique normalmente sin errores."""
        # Umbrales imposibles para forzar 0 coincidencias
        res_cero = calcular_analogos(
            year_objetivo=2015,
            mes_objetivo=10,
            indices=["AMO"],
            umbrales_personalizados={"AMO": (0.999, 0.001)},
            oscilaciones_cargadas=self.oscilaciones
        )
        self.assertTrue(res_cero.es_valido)

        fig = generar_grafico_individual_indice(res_cero, "AMO")
        self.assertIsInstance(fig, plt.Figure)
        ax1 = fig.axes[0]
        patches = [p for p in ax1.patches if isinstance(p, mpatches.FancyBboxPatch)]
        self.assertEqual(len(patches), 0)
        plt.close(fig)

    def test_invalid_index_raises_value_error(self):
        """Verifica que solicitar un índice que no estuvo en el análisis arroje ValueError."""
        with self.assertRaises(ValueError):
            generar_grafico_individual_indice(self.resultado, "INDICE_INEXISTENTE")


if __name__ == "__main__":
    unittest.main()
