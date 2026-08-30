"""
Pruebas de integridad del catálogo estructurado de los 19 índices.
"""

import unittest
from aanalogos.catalog import cargar_catalogo_indices, obtener_estado_fuentes
from aanalogos.data import cargar_todas_oscilaciones


class TestCatalogIntegrity(unittest.TestCase):
    def test_catalog_all_indices_present(self):
        """Verificar que los 19 índices base + 3 nuevas series ENSO (22 total) estén presentes en el catálogo."""
        cat = cargar_catalogo_indices()
        self.assertGreaterEqual(len(cat), 22)
        expected_indices = [
            "AMO", "AO", "MEI", "ONI", "ONIv5", "ONIv6", "RONI", "NAO", "PDO", "TNA",
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
        """Verificar que la tabla de salud de fuentes contenga los índices del catálogo."""
        osc = cargar_todas_oscilaciones()
        df_health = obtener_estado_fuentes(osc)
        self.assertGreaterEqual(len(df_health), 22)
        self.assertIn("Código", df_health.columns)
        self.assertIn("Estado", df_health.columns)
        self.assertIn("Tipo de Variable", df_health.columns)
        self.assertIn("Variable en Motor", df_health.columns)


if __name__ == "__main__":
    unittest.main()
