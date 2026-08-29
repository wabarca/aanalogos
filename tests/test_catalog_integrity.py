"""
Pruebas de integridad del catálogo estructurado de los 19 índices.
"""

import unittest
from aanalogos.catalog import cargar_catalogo_indices, obtener_estado_fuentes
from aanalogos.data import cargar_todas_oscilaciones


class TestCatalogIntegrity(unittest.TestCase):
    def test_catalog_19_indices_present(self):
        """Verificar que los 19 índices estén presentes en el catálogo."""
        cat = cargar_catalogo_indices()
        self.assertEqual(len(cat), 19)
        expected_indices = [
            "AMO", "AO", "MEI", "ONI", "NAO", "PDO", "TNA",
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

    def test_sources_health_status_dataframe(self):
        """Verificar que la tabla de salud de fuentes contenga los 19 índices."""
        osc = cargar_todas_oscilaciones()
        df_health = obtener_estado_fuentes(osc)
        self.assertEqual(len(df_health), 19)
        self.assertIn("Código", df_health.columns)
        self.assertIn("Estado", df_health.columns)


if __name__ == "__main__":
    unittest.main()
