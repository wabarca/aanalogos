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


if __name__ == "__main__":
    unittest.main()
