"""
Pruebas para el descubrimiento y visualización integrada de documentación Markdown.
"""

import os
import unittest
from app import obtener_documentos_disponibles, DIRECTORIO_ACTUAL


class TestDocsViewer(unittest.TestCase):
    def test_obtener_documentos_disponibles_retorna_docs(self):
        """Verifica que el visor descubra los manuales y guías del proyecto."""
        docs = obtener_documentos_disponibles(DIRECTORIO_ACTUAL)
        self.assertIsInstance(docs, dict)
        self.assertGreater(len(docs), 5)
        
        # Comprobar que documentos clave estén presentes
        etiquetas = list(docs.keys())
        self.assertTrue(any("Manual de Usuario" in k for k in etiquetas))
        self.assertTrue(any("Metodología Científica" in k for k in etiquetas))
        self.assertTrue(any("Catálogo de Índices" in k for k in etiquetas))
        
        # Comprobar que todas las rutas correspondan a archivos existentes
        for etiqueta, ruta in docs.items():
            self.assertTrue(os.path.isfile(ruta), f"El archivo para {etiqueta} no existe: {ruta}")

    def test_directorio_inexistente_no_falla(self):
        """Si se pasa un directorio inexistente, debe retornar dict vacío o README sin romper."""
        docs = obtener_documentos_disponibles("C:/ruta/inexistente/invalida")
        self.assertIsInstance(docs, dict)


if __name__ == "__main__":
    unittest.main()
