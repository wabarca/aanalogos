"""
Pruebas de integridad del catálogo estructurado de los 19 índices.
"""

import unittest
from aanalogos.catalog import cargar_catalogo_indices, obtener_estado_fuentes
from aanalogos.data import cargar_todas_oscilaciones


class TestCatalogIntegrity(unittest.TestCase):
    def test_catalog_all_indices_present(self):
        """Verificar que los 18 índices base + 3 series ENSO definitivas (21 total) estén presentes en el catálogo y ONI no exista."""
        cat = cargar_catalogo_indices()
        self.assertEqual(len(cat), 21, "El catálogo debe contener exactamente 21 series climáticas")
        self.assertNotIn("ONI", cat, "El identificador genérico 'ONI' no debe existir en el catálogo")
        
        expected_indices = [
            "AMO", "AO", "MEI", "ONIv5", "ONIv6", "RONI", "NAO", "PDO", "TNA",
            "SSTA_12", "SSTA_3", "SSTA_4", "SSTA_34",
            "AtlTROP", "SAtl", "NAtl", "CAR", "WHWP", "PNA", "SOI", "AMO_CSU"
        ]
        for idx in expected_indices:
            self.assertIn(idx, cat)
            meta = cat[idx]
            self.assertIn("name", meta)
            self.assertIn("institution", meta)
            self.assertIn("region", meta)
            self.assertIn("variable", meta)
            self.assertIn("units", meta)
            self.assertIn("variable_type", meta)
            self.assertIn("exact_variable_used", meta)

    def test_sources_health_status_dataframe(self):
        """Verificar que la tabla de salud de fuentes contenga los 21 índices del catálogo y no contenga ONI."""
        osc = cargar_todas_oscilaciones()
        df_health = obtener_estado_fuentes(osc)
        self.assertEqual(len(df_health), 21)
        self.assertNotIn("ONI", df_health["Código"].values, "'ONI' no debe figurar en la tabla de salud")
        self.assertIn("Código", df_health.columns)
        self.assertIn("Estado", df_health.columns)
        self.assertIn("Tipo de Variable", df_health.columns)
        self.assertIn("Variable en Motor", df_health.columns)


    def test_sources_health_status_when_sources_are_empty_or_missing(self):
        """Verificar que obtener_estado_fuentes funcione determinísticamente sin UnboundLocalError y sea serializable en PyArrow."""
        import pandas as pd
        import pyarrow as pa
        
        # Probar con diccionario completamente vacío
        df_health_empty = obtener_estado_fuentes({})
        self.assertEqual(len(df_health_empty), 21)
        self.assertIn("Estado", df_health_empty.columns)
        for _, row in df_health_empty.iterrows():
            self.assertIn(row["Estado"], ["No descargado", "Error", "Disponible", "Cobertura Parcial"])
            self.assertTrue(pd.isna(row["Primer Año"]))
            self.assertTrue(pd.isna(row["Último Año"]))
            self.assertEqual(row["Años Registrados"], 0)

        # Verificar serialización directa en PyArrow sin errores de tipo mixto
        tbl = pa.Table.from_pandas(df_health_empty)
        self.assertEqual(tbl.num_rows, 21)


if __name__ == "__main__":
    unittest.main()
