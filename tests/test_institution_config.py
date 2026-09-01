"""
Pruebas unitarias de configuración institucional y desacoplamiento de branding.
"""

import unittest
import os
import tempfile
import yaml
from aanalogos.catalog import cargar_configuracion_institucional


class TestInstitutionConfig(unittest.TestCase):
    def test_default_institution_config_when_no_file(self):
        """Si se especifica un archivo inexistente, retorna los valores por defecto neutros sin fallar."""
        cfg = cargar_configuracion_institucional(config_path="/ruta/inexistente/institution.yaml")
        self.assertIn("name", cfg)
        self.assertIn("division", cfg)
        self.assertIn("logo", cfg)
        self.assertIsNone(cfg["logo"])
        self.assertTrue(len(cfg["name"]) > 0)
        self.assertTrue(len(cfg["division"]) > 0)

    def test_load_custom_institution_yaml(self):
        """Carga correctamente una configuración YAML personalizada."""
        custom_data = {
            "institution": {
                "name": "Instituto Meteorológico Nacional",
                "division": "Departamento de Climatología",
                "logo": "docs/img/logo_MARN.png"
            }
        }
        with tempfile.NamedTemporaryFile("w", suffix=".yaml", delete=False, encoding="utf-8") as f:
            yaml.dump(custom_data, f)
            temp_path = f.name

        try:
            cfg = cargar_configuracion_institucional(config_path=temp_path)
            self.assertEqual(cfg["name"], "Instituto Meteorológico Nacional")
            self.assertEqual(cfg["division"], "Departamento de Climatología")
            # El logo existe en docs/img/logo_MARN.png
            if os.path.exists("docs/img/logo_MARN.png"):
                self.assertIsNotNone(cfg["logo"])
                self.assertTrue(cfg["logo"].lower().endswith(".png"))
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_handles_non_existent_or_invalid_logo_gracefully(self):
        """Si el logo especificado no existe o no es un PNG, lo establece en None sin generar excepción."""
        custom_data = {
            "institution": {
                "name": "Servicio de Hidrometeorología",
                "division": "Unidad de Pronóstico",
                "logo": "ruta/al/logo_inexistente.png"
            }
        }
        with tempfile.NamedTemporaryFile("w", suffix=".yaml", delete=False, encoding="utf-8") as f:
            yaml.dump(custom_data, f)
            temp_path = f.name

        try:
            cfg = cargar_configuracion_institucional(config_path=temp_path)
            self.assertEqual(cfg["name"], "Servicio de Hidrometeorología")
            self.assertEqual(cfg["division"], "Unidad de Pronóstico")
            self.assertIsNone(cfg["logo"])
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_active_repo_institution_config(self):
        """Verifica que la configuración activa en el repositorio se cargue adecuadamente."""
        cfg = cargar_configuracion_institucional()
        self.assertIsInstance(cfg, dict)
        self.assertIn("name", cfg)
        self.assertIn("division", cfg)
        self.assertIn("logo", cfg)


if __name__ == "__main__":
    unittest.main()
