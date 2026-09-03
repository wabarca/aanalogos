"""
Pruebas exhaustivas para el módulo de documentación interna y navegación Markdown.
Verifica resolución de enlaces, transformación con target_self y protección contra path traversal.
"""

import os
import unittest
from aanalogos.docs import (
    obtener_documentos_disponibles,
    resolver_enlace_markdown,
    transformar_enlaces_markdown,
    buscar_etiqueta_documento,
)

DIRECTORIO_PROYECTO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class TestDocsViewer(unittest.TestCase):
    def setUp(self):
        self.base_dir = DIRECTORIO_PROYECTO
        self.doc_readme_docs = os.path.join(self.base_dir, "docs", "README.md")
        self.doc_metodologia = os.path.join(self.base_dir, "docs", "metodologia.md")
        self.doc_readme_root = os.path.join(self.base_dir, "README.md")
        self.docs_map = obtener_documentos_disponibles(self.base_dir)

    def test_descubrimiento_documentos(self):
        """Verifica que el visor descubra los manuales, guías y READMEs disponibles."""
        self.assertIsInstance(self.docs_map, dict)
        self.assertGreater(len(self.docs_map), 5)

        # Documentos esenciales deben estar presentes
        etiquetas = list(self.docs_map.keys())
        self.assertTrue(any("Manual de Usuario" in k for k in etiquetas))
        self.assertTrue(any("Metodología Científica" in k for k in etiquetas))
        self.assertTrue(any("Catálogo de Índices" in k for k in etiquetas))

        # Todas las rutas mapeadas deben existir en disco
        for etiqueta, ruta in self.docs_map.items():
            self.assertTrue(os.path.isfile(ruta), f"El archivo para '{etiqueta}' no existe: {ruta}")

    def test_resolver_enlace_interno_mismo_directorio(self):
        """Verifica la resolución de un enlace relativo entre archivos en docs/."""
        res = resolver_enlace_markdown("indices.md", self.doc_readme_docs, self.base_dir)
        self.assertEqual(res, "docs/indices.md")

    def test_resolver_enlace_con_subida_directorio(self):
        """Verifica la resolución de ../README.md desde docs/README.md."""
        res = resolver_enlace_markdown("../README.md", self.doc_readme_docs, self.base_dir)
        self.assertEqual(res, "README.md")

    def test_resolver_enlace_desde_raiz_a_docs(self):
        """Verifica la resolución de docs/indices.md desde README.md en raíz."""
        res = resolver_enlace_markdown("docs/indices.md", self.doc_readme_root, self.base_dir)
        self.assertEqual(res, "docs/indices.md")

    def test_resolver_enlace_con_ancla(self):
        """Verifica la resolución de un enlace con ancla interna (ej. metodologia.md#seccion1)."""
        res = resolver_enlace_markdown("metodologia.md#seccion1", self.doc_readme_docs, self.base_dir)
        self.assertEqual(res, "docs/metodologia.md#seccion1")

    def test_enlaces_externos_no_se_interceptan(self):
        """Verifica que URLs externas (http, https, mailto) retornen None para no ser transformadas."""
        self.assertIsNone(resolver_enlace_markdown("https://psl.noaa.gov", self.doc_readme_docs, self.base_dir))
        self.assertIsNone(resolver_enlace_markdown("http://cpc.ncep.noaa.gov/data", self.doc_readme_docs, self.base_dir))
        self.assertIsNone(resolver_enlace_markdown("mailto:met@marn.gob.sv", self.doc_readme_docs, self.base_dir))
        self.assertIsNone(resolver_enlace_markdown("#ancla-local", self.doc_readme_docs, self.base_dir))

    def test_seguridad_path_traversal_bloqueado(self):
        """Verifica que intentos de escapar del directorio del proyecto sean rechazados (retornan None)."""
        self.assertIsNone(resolver_enlace_markdown("../../../../../etc/passwd.md", self.doc_readme_docs, self.base_dir))
        self.assertIsNone(resolver_enlace_markdown("..\\..\\..\\secreto.md", self.doc_readme_docs, self.base_dir))

    def test_transformar_enlaces_markdown_completo(self):
        """Verifica que la transformación Markdown reemplace enlaces relativos por enlaces con ?doc= y target_self."""
        texto_md = (
            "Consulte el [Catálogo de Índices](indices.md) y la "
            "[Metodología](metodologia.md#pearson) o visite [NOAA](https://psl.noaa.gov)."
        )
        res = transformar_enlaces_markdown(texto_md, self.doc_readme_docs, self.base_dir)

        # Los enlaces internos deben tener ?doc= y target="_self"
        self.assertIn('<a href="?doc=docs/indices.md" target="_self">Catálogo de Índices</a>', res)
        self.assertIn('<a href="?doc=docs/metodologia.md#pearson" target="_self">Metodología</a>', res)
        # El enlace externo debe mantenerse intacto
        self.assertIn("[NOAA](https://psl.noaa.gov)", res)

    def test_buscar_etiqueta_documento(self):
        """Verifica que buscar_etiqueta_documento resuelva diversos formatos de entrada."""
        etiqueta_idx = buscar_etiqueta_documento("indices.md", self.docs_map, self.base_dir)
        self.assertIsNotNone(etiqueta_idx)
        self.assertIn("Catálogo de Índices", etiqueta_idx)

        etiqueta_rel = buscar_etiqueta_documento("docs/metodologia.md", self.docs_map, self.base_dir)
        self.assertIsNotNone(etiqueta_rel)
        self.assertIn("Metodología Científica", etiqueta_rel)

        etiqueta_ancla = buscar_etiqueta_documento("metodologia.md#formula", self.docs_map, self.base_dir)
        self.assertIsNotNone(etiqueta_ancla)
        self.assertIn("Metodología Científica", etiqueta_ancla)

        # Documento inexistente debe retornar None sin lanzar excepción
        etiqueta_inexistente = buscar_etiqueta_documento("archivo_fantasma_123.md", self.docs_map, self.base_dir)
        self.assertIsNone(etiqueta_inexistente)


if __name__ == "__main__":
    unittest.main()
