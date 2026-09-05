"""
Pruebas unitarias para la visualización gráfica individual por índice.
Verifica la consistencia absoluta entre los resultados del motor y la figura generada.
"""

import unittest
import numpy as np
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
            # Los textos de los años coincidentes están en la parte superior con rotación vertical de 90°
            try:
                val = int(text.get_text())
                if val in traz_amo["YEAR"].values:
                    anios_en_grafico.append(val)
                    self.assertEqual(text.get_rotation(), 90)
                    self.assertEqual(text.get_ha(), "center")
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

    def test_chart_consecutive_years_alignment(self):
        """
        Verifica que para casos con años consecutivos (ej. 2001, 2002, 2003 y 2012, 2013, 2014),
        las etiquetas se ubiquen exactamente centradas en x = año, con rotación vertical de 90°
        y sin solapamiento de coordenadas.
        """
        fig = generar_grafico_individual_indice(self.resultado, "AMO")
        ax1 = fig.axes[0]
        
        traz_amo = self.resultado.tabla_trazabilidad[self.resultado.tabla_trazabilidad["Indice"] == "AMO"]
        anios_esperados = set(traz_amo[traz_amo["Coincidencia"] == 1]["YEAR"].tolist())

        posiciones_x = []
        for text in ax1.texts:
            try:
                val = int(text.get_text())
                if val in anios_esperados:
                    self.assertEqual(text.get_rotation(), 90)
                    self.assertEqual(text.get_ha(), "center")
                    self.assertEqual(text.get_va(), "bottom")
                    x_pos, y_pos = text.get_position()
                    self.assertEqual(x_pos, val)
                    self.assertAlmostEqual(y_pos, 1.20)
                    posiciones_x.append(x_pos)
            except ValueError:
                pass

        # Verificar que no haya coordenadas X duplicadas
        self.assertEqual(len(posiciones_x), len(set(posiciones_x)))
        self.assertEqual(set(posiciones_x), anios_esperados)
        plt.close(fig)

    def test_extended_axes_and_green_band_bounds(self):
        """
        Verifica que el eje Y1 esté en [-1.50, 1.50], el eje Y2 comience en 0.0,
        el eje X tenga márgenes horizontales y los rectángulos verdes cubran [-1.10, 1.10].
        """
        fig = generar_grafico_individual_indice(self.resultado, "AMO")
        ax1 = fig.axes[0]
        ax2 = fig.axes[1]

        # Límites verticales
        self.assertAlmostEqual(ax1.get_ylim()[0], -1.50)
        self.assertAlmostEqual(ax1.get_ylim()[1], 1.50)
        self.assertAlmostEqual(ax2.get_ylim()[0], 0.0)

        # Límites horizontales con margen
        traz_amo = self.resultado.tabla_trazabilidad[self.resultado.tabla_trazabilidad["Indice"] == "AMO"]
        min_y = traz_amo["YEAR"].min()
        max_y = traz_amo["YEAR"].max()
        self.assertLess(ax1.get_xlim()[0], min_y)
        self.assertGreater(ax1.get_xlim()[1], max_y)

        # Rectángulos verdes: altura = 2.20 (de -1.10 a 1.10)
        patches = [p for p in ax1.patches if isinstance(p, mpatches.FancyBboxPatch)]
        for p in patches:
            self.assertAlmostEqual(p.get_y(), -1.10)
            self.assertAlmostEqual(p.get_height(), 2.20)

        plt.close(fig)

    def test_threshold_halo_no_bbox(self):
        """
        Verifica que las etiquetas de umbral tengan efecto halo (path_effects)
        y NO tengan bbox rectangular blanco.
        """
        fig = generar_grafico_individual_indice(self.resultado, "AMO")
        ax1 = fig.axes[0]
        ax2 = fig.axes[1]

        # Umbral r en ax1
        txt_r = [t for t in ax1.texts if "Umbral r" in t.get_text()]
        self.assertEqual(len(txt_r), 1)
        self.assertIsNone(txt_r[0].get_bbox_patch())
        self.assertTrue(len(txt_r[0].get_path_effects()) > 0)

        # Umbral MAD en ax2
        txt_mad = [t for t in ax2.texts if "Umbral MAD" in t.get_text()]
        self.assertEqual(len(txt_mad), 1)
        self.assertIsNone(txt_mad[0].get_bbox_patch())
        self.assertTrue(len(txt_mad[0].get_path_effects()) > 0)

    def test_sorted_chart_generation(self):
        """Verifica que generar_grafico_individual_indice con orden='pearson_desc' genere una figura válida."""
        fig = generar_grafico_individual_indice(self.resultado, "TNA", orden="pearson_desc")
        self.assertIsInstance(fig, plt.Figure)
        self.assertGreaterEqual(len(fig.axes), 2)
        plt.close(fig)

    def test_sorted_chart_pearson_descending_monotonicity(self):
        """
        Verifica que en el gráfico ordenado (orden='pearson_desc'), los valores de la serie Pearson
        sigan un orden estrictamente no creciente (de mayor a menor correlación).
        """
        fig = generar_grafico_individual_indice(self.resultado, "AMO", orden="pearson_desc")
        ax1 = fig.axes[0]
        self.assertEqual(ax1.get_xlabel(), "Año (ordenado por correlación, mayor a menor)")

        # Extraer la serie Pearson graficada en ax1
        lines = ax1.get_lines()
        # Línea de datos de Pearson (la que tiene color azul #1976D2 y markers)
        line_r = [l for l in lines if l.get_color() == "#1976D2"][0]
        y_data = line_r.get_ydata()

        # Comprobar monotonicidad descendente
        for k in range(len(y_data) - 1):
            self.assertGreaterEqual(y_data[k], y_data[k + 1])

        plt.close(fig)

    def test_sorted_chart_matches_and_pairs_integrity(self):
        """
        Verifica que el gráfico ordenado preserve los pares exactos (Año, Pearson, MAD, Coincidencia)
        y que las bandas verdes se dibujen en las posiciones correctas.
        """
        traz_amo = self.resultado.tabla_trazabilidad[self.resultado.tabla_trazabilidad["Indice"] == "AMO"]
        df_validos = traz_amo.dropna(subset=["Pearson", "MAD"]).sort_values("Pearson", ascending=False).reset_index(drop=True)

        fig = generar_grafico_individual_indice(self.resultado, "AMO", orden="pearson_desc")
        ax1 = fig.axes[0]
        ax2 = fig.axes[1]

        # Comprobar serie Pearson y serie MAD
        line_r = [l for l in ax1.get_lines() if l.get_color() == "#1976D2" and len(l.get_ydata()) > 2][0]
        line_mad = [l for l in ax2.get_lines() if l.get_color() == "#D32F2F" and len(l.get_ydata()) > 2][0]

        np.testing.assert_allclose(line_r.get_ydata(), df_validos["Pearson"].values, rtol=1e-5)
        np.testing.assert_allclose(line_mad.get_ydata(), df_validos["MAD"].values, rtol=1e-5)

        # Comprobar etiquetas de años análogos
        indices_coincidentes = df_validos[df_validos["Coincidencia"] == 1].index.tolist()
        anios_coincidentes = df_validos[df_validos["Coincidencia"] == 1]["YEAR"].tolist()

        etiquetas_x = []
        anios_etiquetados = []
        for text in ax1.texts:
            try:
                val = int(text.get_text())
                if val in anios_coincidentes:
                    anios_etiquetados.append(val)
                    etiquetas_x.append(int(round(text.get_position()[0])))
            except ValueError:
                pass

        self.assertEqual(sorted(etiquetas_x), sorted(indices_coincidentes))
        self.assertEqual(sorted(anios_etiquetados), sorted(anios_coincidentes))

        plt.close(fig)


if __name__ == "__main__":
    unittest.main()
