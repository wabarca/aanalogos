"""
Módulo de gestión y visualización de documentación Markdown interna para Aanalogos.
Permite descubrir documentos disponibles, resolver rutas relativas de forma segura
y transformar enlaces internos para navegación nativa sin abandonar Streamlit.
"""

import os
import re
from typing import Dict, Optional
from urllib.parse import unquote

NOMBRES_LEGIBLES_DOCS = {
    "manual_usuario.md": "📘 Manual de Usuario",
    "metodologia.md": "🔬 Metodología Científica",
    "indices.md": "🌊 Catálogo de Índices y Fuentes",
    "validacion_climatologica.md": "✅ Validación Climatológica",
    "referencias.md": "📚 Referencias Bibliográficas",
    "arquitectura.md": "🏛️ Arquitectura de Software",
    "despliegue_institucional.md": "🏢 Despliegue Institucional y systemd",
    "instalacion_linux.md": "🐧 Instalación en Linux",
    "instalacion_windows.md": "🪟 Instalación en Windows",
    "reproducibilidad.md": "🧪 Protocolo de Reproducibilidad",
    "mantenimiento.md": "🔧 Manual de Mantenimiento",
    "auditoria.md": "🔍 Auditoría del Sistema",
    "auditoria_temporal_metodologica.md": "⏱️ Auditoría Temporal y Ventanas",
    "auditoria_final_cierre.md": "📋 Auditoría Final de Cierre",
    "auditoria_repositorio.md": "📁 Auditoría del Repositorio",
    "informe_preparacion_institucional.md": "📄 Informe de Preparación Institucional",
    "informe_fase3.md": "📑 Informe Técnico Fase 3",
    "README.md": "📖 Índice General de Documentación",
}


def obtener_documentos_disponibles(directorio_base: str) -> Dict[str, str]:
    """
    Obtiene dinámicamente los documentos Markdown existentes en docs/ y en la raíz,
    asignando títulos legibles y preservando compatibilidad en cualquier entorno de despliegue.
    Retorna un diccionario {Etiqueta_Amigable: Ruta_Absoluta}.
    """
    docs_dir = os.path.join(directorio_base, "docs")
    docs_map = {}

    # 1. Documento raíz README.md o docs/README.md
    docs_readme = os.path.join(docs_dir, "README.md")
    if os.path.isfile(docs_readme):
        docs_map["📖 Índice General (docs/README)"] = docs_readme

    root_readme = os.path.join(directorio_base, "README.md")
    if os.path.isfile(root_readme):
        docs_map["🏠 README Principal del Proyecto"] = root_readme

    # 2. Documentos en docs/
    if os.path.isdir(docs_dir):
        for fname in sorted(os.listdir(docs_dir)):
            if fname.endswith(".md") and not fname.startswith(".") and fname != "README.md":
                full_path = os.path.join(docs_dir, fname)
                etiqueta = NOMBRES_LEGIBLES_DOCS.get(
                    fname, f"📄 {fname[:-3].replace('_', ' ').title()}"
                )
                docs_map[etiqueta] = full_path

    return docs_map


def resolver_enlace_markdown(
    href: str, ruta_doc_actual: str, directorio_base: str
) -> Optional[str]:
    """
    Resuelve un enlace relativo de un documento Markdown a una ruta relativa segura
    dentro del repositorio. Retorna None si es un enlace externo, ancla pura o si sale
    del directorio_base permitido.
    """
    if not href:
        return None

    href = unquote(href.strip())

    # Manejar esquema file://docs/...
    if href.lower().startswith("file://"):
        href = re.sub(r"^file:///?", "", href, flags=re.IGNORECASE)

    # Ignorar enlaces web externos (http, https, mailto, etc.) y anclas puras (#seccion)
    if re.match(r"^(https?://|mailto:|ftp:|tel:|#)", href, re.IGNORECASE):
        return None

    # Separar ancla si existe (ej. metodologia.md#formulacion)
    href_path, sep, anchor = href.partition("#")

    # Debe ser un archivo con extensión .md
    if not href_path.lower().endswith(".md"):
        return None

    dir_actual = os.path.dirname(os.path.abspath(ruta_doc_actual))
    target_abs = os.path.normpath(os.path.join(dir_actual, href_path))
    directorio_base_abs = os.path.normpath(os.path.abspath(directorio_base))

    # Seguridad: no permitir salir del repositorio (prevenir path traversal ../../..)
    if not target_abs.startswith(directorio_base_abs):
        return None

    rel_path = os.path.relpath(target_abs, directorio_base_abs).replace("\\", "/")
    return f"{rel_path}{sep}{anchor}" if sep else rel_path


def transformar_enlaces_markdown(
    contenido_md: str, ruta_doc_actual: str, directorio_base: str
) -> str:
    """
    Transforma enlaces relativos a archivos .md dentro del contenido Markdown para que
    apunten al parámetro interno de navegación (?doc=...) con target="_self", permitiendo
    que Streamlit intercepte la navegación internamente sin recargar la página en una URL inválida.
    """
    def repl_md(match):
        texto = match.group(1)
        href = match.group(2)
        rel_doc = resolver_enlace_markdown(href, ruta_doc_actual, directorio_base)
        if rel_doc:
            return f'<a href="?doc={rel_doc}" target="_self">{texto}</a>'
        return match.group(0)

    def repl_html(match):
        attrs_before = match.group(1)
        href = match.group(2)
        attrs_after = match.group(3)
        if href.startswith("?doc=") or href.startswith("?"):
            return match.group(0)
        rel_doc = resolver_enlace_markdown(href, ruta_doc_actual, directorio_base)
        if rel_doc:
            return f'<a {attrs_before}href="?doc={rel_doc}" target="_self"{attrs_after}>'
        return match.group(0)

    # Reemplazar sintaxis Markdown [texto](enlace)
    patron_md = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
    contenido_trans = patron_md.sub(repl_md, contenido_md)

    # Reemplazar enlaces HTML <a href="...">
    patron_html = re.compile(r'<a\s+([^>]*?)href=["\']([^"\']+)["\']([^>]*)>', re.IGNORECASE)
    contenido_trans = patron_html.sub(repl_html, contenido_trans)

    return contenido_trans


def buscar_etiqueta_documento(
    doc_ref: str, docs_disponibles: Dict[str, str], directorio_base: str
) -> Optional[str]:
    """
    Dado un identificador o ruta relativa de documento (ej. 'indices.md', 'docs/metodologia.md', 'README.md'),
    encuentra la etiqueta coincidente en el diccionario docs_disponibles.
    """
    if not doc_ref or not docs_disponibles:
        return None

    doc_ref_clean = unquote(doc_ref).split("#")[0].replace("\\", "/").strip()
    target_abs = os.path.normpath(os.path.join(directorio_base, doc_ref_clean))
    target_base = os.path.basename(doc_ref_clean).lower()

    # 1. Coincidencia exacta por ruta absoluta
    for etiqueta, ruta in docs_disponibles.items():
        if os.path.normpath(ruta) == target_abs:
            return etiqueta

    # 2. Coincidencia por ruta relativa normalizada
    for etiqueta, ruta in docs_disponibles.items():
        rel_disp = os.path.relpath(ruta, directorio_base).replace("\\", "/").lower()
        if rel_disp == doc_ref_clean.lower():
            return etiqueta

    # 3. Coincidencia por nombre de archivo (basename)
    for etiqueta, ruta in docs_disponibles.items():
        if os.path.basename(ruta).lower() == target_base:
            return etiqueta

    # 4. Coincidencia por contenido de etiqueta
    for etiqueta in docs_disponibles:
        if target_base in etiqueta.lower() or doc_ref_clean.lower() in etiqueta.lower():
            return etiqueta

    return None
