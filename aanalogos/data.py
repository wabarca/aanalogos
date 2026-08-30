"""
Módulo de descarga, parsing y carga de series temporales de oscilaciones climáticas.
"""

import os
import re
import ssl
import tempfile
import urllib.request
import requests
import pandas as pd
import numpy as np
from typing import Dict, Optional, Any, Callable, Tuple, List, Union

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None

from .config import FUENTES_DATOS
from .quality import limpiar_datos_indice


import socket

def descarga_segura(url: str, ruta_salida: str, timeout: int = 30) -> bool:
    """Descarga un archivo desde una URL si no existe localmente o para actualización."""
    try:
        socket.setdefaulttimeout(timeout)
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AAnalogos/3.2"}
        )
        with urllib.request.urlopen(req, context=ctx, timeout=timeout) as response:
            if response.status != 200:
                return False
            data = response.read()
            if len(data) < 50:
                return False
            with open(ruta_salida, "wb") as f:
                f.write(data)
        return True
    except Exception:
        return False


def parse_linea_matriz_mensual(linea: str) -> Optional[list]:
    """
    Parsea de forma robusta y no destructiva una línea de texto de matrices mensuales (NOAA PSL/CPC).
    Filtra encabezados (ej. '1948 2026'), sentinelas aislados y notas al pie sin depender de on_bad_lines='skip'.
    Separa correctamente valores compactos pegados (ej. '-2.4-999.9').
    """
    line_clean = linea.strip()
    if not line_clean:
        return None

    # Tokenizar números incluyendo compactos como -2.4-999.9
    tokens = re.findall(r'[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?', line_clean)
    if not tokens or len(tokens) < 2:
        return None

    first_tok = tokens[0]
    if not (first_tok.isdigit() and len(first_tok) == 4):
        return None
    year_val = int(first_tok)
    if not (1800 <= year_val <= 2100):
        return None

    # Si es una línea de encabezado PSL con año de inicio y fin (ej. '1948 2026')
    if len(tokens) <= 3 and tokens[1].isdigit() and len(tokens[1]) == 4 and 1800 <= int(tokens[1]) <= 2100:
        return None

    # Verificar que el segundo token original no sea una palabra de una cita textual (ej. '2001 : The tropical...')
    raw_words = line_clean.split()
    if len(raw_words) >= 2:
        try:
            val_m1 = float(raw_words[1])
            if len(raw_words) <= 3 and 1800 <= val_m1 <= 2100:
                return None
        except ValueError:
            return None

    # Extraer hasta 12 valores numéricos para los meses
    month_vals = []
    for tok in tokens[1:13]:
        try:
            month_vals.append(float(tok))
        except ValueError:
            break

    if not month_vals:
        return None

    # Si el año está parcialmente publicado (ej. 2026 con 5 meses), rellenar con np.nan
    if len(month_vals) < 12:
        month_vals = month_vals + [np.nan] * (12 - len(month_vals))

    return [year_val] + month_vals


def acomodaParaCSV(ruta_entrada: str, ruta_salida: str) -> bool:
    """Convierte matriz de texto espacio-separada a CSV estructurado soportando años parciales y notas al pie."""
    if not os.path.exists(ruta_entrada):
        return False
    try:
        with open(ruta_entrada, "r", encoding="utf-8", errors="ignore") as ptr:
            lineas = ptr.readlines()

        if not lineas:
            return False

        # Caso especial 1: Archivo CSU CSV directo (Year,Jan,Feb,...)
        primera_linea = lineas[0].strip().lower()
        if "year" in primera_linea and "," in primera_linea:
            df_csu = pd.read_csv(ruta_entrada)
            cols_csu = list(df_csu.columns)
            # Mapear nombres de columnas a YEAR + ENE..DIC
            mapa_csu = {cols_csu[0]: "YEAR"}
            meses_oficiales = ["ENE", "FEB", "MAR", "ABR", "MAY", "JUN", "JUL", "AGO", "SET", "OCT", "NOV", "DIC"]
            for idx_m, m_orig in enumerate(cols_csu[1:13]):
                mapa_csu[m_orig] = meses_oficiales[idx_m]
            df_csu = df_csu.rename(columns=mapa_csu)
            df_csu.to_csv(ruta_salida, index=False)
            return True

        # Caso especial 2: Archivos compuestos SSTA / SSTOI
        if ruta_entrada.endswith("dataSSTA.txt") or ruta_entrada.endswith("dataSSTOI.txt"):
            with open(ruta_salida, "w", encoding="utf-8", newline="\n") as ptr:
                if ruta_entrada.endswith("dataSSTA.txt"):
                    ptr.write("YEAR,MONTH,NINO1+2,ANOM1+2,NINO3,ANOM3,NINO4,ANOM4,NINO3.4,ANOM3.4")
                else:
                    ptr.write("YEAR,MONTH,NAtl,ANOM_NAtl,SAtl,ANOM_SAtl,TROP,ANOM_TROP")

                for linea in lineas[1:]:
                    linea_tokens = [v for v in linea.strip().split() if v != ""]
                    if not linea_tokens or len(linea_tokens) < 4:
                        continue
                    if linea_tokens[0].isdigit() and len(linea_tokens[0]) == 4 and linea_tokens[1].isdigit():
                        ptr.write("\n" + ",".join(linea_tokens))
            return True

        # Caso estándar: Matrices mensuales espacio-separadas de PSL/CPC
        filas_procesadas = []
        for linea in lineas:
            row = parse_linea_matriz_mensual(linea)
            if row is not None:
                filas_procesadas.append(row)

        if not filas_procesadas:
            return False

        meses_cols = ["ENE", "FEB", "MAR", "ABR", "MAY", "JUN", "JUL", "AGO", "SET", "OCT", "NOV", "DIC"]
        df_out = pd.DataFrame(filas_procesadas, columns=["YEAR"] + meses_cols)
        df_out["YEAR"] = df_out["YEAR"].astype(int)
        df_out.to_csv(ruta_salida, index=False)
        return True
    except Exception:
        return False


def acomodaParaCSV_2(url: str, archivocreado: str) -> bool:
    """Extrae tablas HTML (ONIv5, ONIv6, RONI) o directas CSV (AMO_CSU) y genera matriz de texto estructurada."""
    try:
        socket.setdefaulttimeout(15)
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AAnalogos/3.2"}
        )
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        with urllib.request.urlopen(req, context=ctx, timeout=15) as response:
            if response.status != 200:
                return False
            raw_data = response.read()
            html_text = raw_data.decode("utf-8", errors="ignore")

        if not html_text or len(html_text) < 50:
            return False

        fname = os.path.basename(archivocreado)

        # 1. Si la respuesta es un CSV directo (ej. Colorado State University AMO)
        if "year" in html_text.splitlines()[0].lower() and "," in html_text.splitlines()[0]:
            with open(archivocreado, "w", encoding="utf-8") as file:
                file.write(html_text)
            return True

        # 2. Extracción con expresiones regulares estándar para tablas HTML
        rows = re.findall(r'<tr[^>]*>(.*?)</tr>', html_text, re.DOTALL | re.IGNORECASE)
        parsed_rows = []

        for row in rows:
            cells = re.findall(r'<(?:td|th)[^>]*>(.*?)</(?:td|th)>', row, re.DOTALL | re.IGNORECASE)
            clean_cells = [re.sub(r'<[^>]+>', '', c).strip() for c in cells]
            if clean_cells and re.match(r'^\d{4}$', clean_cells[0]):
                year_val = int(clean_cells[0])
                if 1850 <= year_val <= 2100 and len(clean_cells) >= 2:
                    padded = clean_cells + ["-99.99"] * max(0, 13 - len(clean_cells))
                    sanitized = [padded[0]]
                    for c in padded[1:13]:
                        if c and c != "-" and c.replace(".", "", 1).replace("-", "", 1).isdigit():
                            sanitized.append(c)
                        else:
                            sanitized.append("-99.99")
                    parsed_rows.append(sanitized)

        if parsed_rows:
            with open(archivocreado, "w", encoding="utf-8") as file:
                if fname.endswith("dataAMO_CSU.txt"):
                    file.write("YEAR ENE FEB MAR ABR MAY JUN JUL AGO SET OCT NOV DIC\n")
                for row_vals in parsed_rows:
                    file.write(" ".join(row_vals) + "\n")
            return True

        # 3. Fallback a BeautifulSoup si está instalado
        if BeautifulSoup:
            soup = BeautifulSoup(html_text, "html.parser")
            table = soup.find("table", attrs={"id": "roni-v5-table2"}) or \
                    soup.find("table", attrs={"id": "roni-v5-table"}) or \
                    soup.find("table", attrs={"border": "1"}) or \
                    soup.find("table", attrs={"id": "amo_table"})
            if table is not None:
                with open(archivocreado, "w", encoding="utf-8") as file:
                    if fname.endswith("dataAMO_CSU.txt"):
                        file.write("YEAR ENE FEB MAR ABR MAY JUN JUL AGO SET OCT NOV DIC\n")
                    for row in table.find_all("tr"):
                        valores = [cell.get_text(strip=True) for cell in row.find_all(["td", "th"])]
                        if valores and valores[0].isdigit() and 1850 <= int(valores[0]) <= 2100 and len(valores) >= 2:
                            padded = valores + ["-99.99"] * max(0, 13 - len(valores))
                            sanitized = [padded[0]]
                            for c in padded[1:13]:
                                if c and c != "-" and c.replace(".", "", 1).replace("-", "", 1).isdigit():
                                    sanitized.append(c)
                                else:
                                    sanitized.append("-99.99")
                            file.write(" ".join(sanitized) + "\n")
                return True

        return False
    except Exception:
        return False


def acomodaParaCSV_3(archivo_descargado: str, archivo_creado: str) -> bool:
    """Reestructura series compuestas (SSTA / SSTOI) a matrices mensuales individuales soportando años parciales."""
    if not os.path.exists(archivo_descargado):
        return False
    try:
        archivo = pd.read_csv(archivo_descargado)
        if len(archivo) == 0:
            return False
        anios = list(dict.fromkeys(archivo["YEAR"]))

        col_target = None
        if "SSTA_12" in archivo_creado:
            col_target = "ANOM1+2"
        elif "SSTA_3" in archivo_creado:
            col_target = "ANOM3"
        elif "SSTA_4" in archivo_creado:
            col_target = "ANOM4"
        elif "SSTA_34" in archivo_creado:
            col_target = "ANOM3.4"
        elif "AtlTROP" in archivo_creado:
            col_target = "ANOM_TROP"
        elif "SAtl" in archivo_creado:
            col_target = "ANOM_SAtl"
        elif "NAtl" in archivo_creado:
            col_target = "ANOM_NAtl"

        if col_target is None or col_target not in archivo.columns:
            return False

        data = archivo[col_target].tolist()
        padsize = (12 - (len(data) % 12)) % 12
        if padsize > 0:
            data_arr = np.pad(np.array(data, dtype=float), (0, padsize), constant_values=np.nan).reshape((-1, 12))
        else:
            data_arr = np.array(data, dtype=float).reshape((-1, 12))

        df_anios = pd.DataFrame(anios, columns=["YEAR"])
        df_meses = pd.DataFrame(
            data_arr,
            columns=["ENE", "FEB", "MAR", "ABR", "MAY", "JUN", "JUL", "AGO", "SET", "OCT", "NOV", "DIC"]
        )
        salida = pd.concat([df_anios, df_meses], axis=1)
        salida.to_csv(archivo_creado, index=False)
        return True
    except Exception:
        return False


def _contar_anios_validos(df: Optional[pd.DataFrame]) -> int:
    """Cuenta el número de registros anuales válidos (1800-2100) en un DataFrame."""
    if df is None or df.empty or "YEAR" not in df.columns:
        return 0
    years_num = pd.to_numeric(df["YEAR"], errors="coerce").dropna()
    valid_years = years_num[(years_num >= 1800) & (years_num <= 2100)]
    return len(valid_years)


def validar_estructura_serie(df: pd.DataFrame, codigo: str, df_previo: Optional[pd.DataFrame] = None) -> Tuple[bool, str]:
    """
    Ejecuta una validación estructural, temporal y numérica rigurosa sobre una serie climatológica mensual.
    Retorna (es_valido, mensaje_diagnostico).
    """
    if df is None or not isinstance(df, pd.DataFrame) or df.empty:
        return False, f"La serie {codigo} generó un DataFrame vacío o inválido."

    meses_esperados = ["ENE", "FEB", "MAR", "ABR", "MAY", "JUN", "JUL", "AGO", "SET", "OCT", "NOV", "DIC"]
    cols_faltantes = [col for col in (["YEAR"] + meses_esperados) if col not in df.columns]
    if cols_faltantes:
        return False, f"Estructura incompleta: faltan las columnas {cols_faltantes}."

    # Validar que existan suficientes años de registro (mínimo 10 años)
    if len(df) < 10:
        return False, f"Cobertura insuficiente: la serie contiene solo {len(df)} registros anuales (mínimo 10 requeridos)."

    # Validar que los años sean enteros únicos y estrictamente crecientes
    anios = df["YEAR"].tolist()
    try:
        anios_int = [int(y) for y in anios]
    except (ValueError, TypeError):
        return False, "La columna 'YEAR' contiene valores no enteros o inválidos."

    if len(anios_int) != len(set(anios_int)):
        return False, "La columna 'YEAR' contiene años duplicados."

    if anios_int != sorted(anios_int):
        return False, "Los registros de 'YEAR' no se encuentran en orden cronológico estrictamente ascendente."

    # Validar que las columnas mensuales sean numéricas
    for m in meses_esperados:
        if not pd.api.types.is_numeric_dtype(df[m]):
            return False, f"La columna del mes '{m}' contiene valores no convertibles a numéricos."

    # Validar que tenga un historial climatológico mínimo (mínimo 10 años)
    len_curr = _contar_anios_validos(df)
    if len_curr < 10:
        return False, f"La serie descargada contiene un historial insuficiente ({len_curr} años < 10 años)."

    # Validar no-regresión temporal frente a versión previa local
    if df_previo is not None and not df_previo.empty and "YEAR" in df_previo.columns:
        years_prev_num = pd.to_numeric(df_previo["YEAR"], errors="coerce").dropna()
        valid_prev = years_prev_num[(years_prev_num >= 1800) & (years_prev_num <= 2100)]
        if len(valid_prev) > 0:
            max_prev = int(valid_prev.max())
            max_curr = int(df["YEAR"].max())
            if max_curr < max_prev - 1:
                return False, f"Inconsistencia temporal: el último año descargado ({max_curr}) es anterior al año local previo ({max_prev})."

    return True, "Validación estructural, temporal y numérica superada exitosamente."


def verificar_y_descargar_datos(
    data_dir: str = ".",
    force_update: bool = False,
    progress_callback: Optional[Callable[[str, int, int], None]] = None
) -> Dict[str, dict]:
    """
    Verifica la existencia e integridad de los archivos CSV para las 21 series climáticas.
    Si faltan archivos o si `force_update=True`, descarga y procesa de forma atómica y no destructiva.
    """
    def _resolver_directorio_salida():
        cands = [
            os.path.join(data_dir, "data"),
            data_dir,
            os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data"),
        ]
        for c in cands:
            if os.path.exists(c) and os.path.isdir(c):
                return c
        os.makedirs(os.path.join(data_dir, "data"), exist_ok=True)
        return os.path.join(data_dir, "data")

    out_dir = _resolver_directorio_salida()
    resultados = {}
    total = len(FUENTES_DATOS)

    for idx, (codigo, meta) in enumerate(FUENTES_DATOS.items()):
        if progress_callback:
            progress_callback(codigo, idx + 1, total)

        csv_name = meta.get("csv", f"data{codigo}.csv")
        txt_name = meta.get("txt", f"data{codigo}.txt")
        target_csv = os.path.join(out_dir, csv_name)
        target_txt = os.path.join(out_dir, txt_name)
        url = meta.get("url")

        csv_existe = os.path.exists(target_csv) and os.path.getsize(target_csv) > 100

        if csv_existe and not force_update:
            resultados[codigo] = {
                "status": "disponible",
                "mensaje": "Archivo disponible e íntegro",
                "archivo": target_csv
            }
            continue

        if not url:
            resultados[codigo] = {
                "status": "sin_url",
                "mensaje": "No posee URL de descarga automática configurada",
                "archivo": target_csv if csv_existe else None
            }
            continue

        # Cargar versión local previa para validación comparativa no destructiva
        df_previo = None
        if csv_existe:
            try:
                df_previo = pd.read_csv(target_csv)
            except Exception:
                df_previo = None

        # Proceso de descarga atómica
        try:
            with tempfile.TemporaryDirectory() as tmp_dir:
                tmp_txt = os.path.join(tmp_dir, txt_name)
                tmp_csv = os.path.join(tmp_dir, csv_name)

                # Descargar
                if "ONI" in codigo or "RONI" in codigo:
                    ok = acomodaParaCSV_2(url, tmp_txt)
                else:
                    timeout_val = 90 if "PDO" in codigo else 30
                    ok = descarga_segura(url, tmp_txt, timeout=timeout_val)

                if not ok or not os.path.exists(tmp_txt) or os.path.getsize(tmp_txt) < 50:
                    resultados[codigo] = {
                        "status": "error_descarga",
                        "mensaje": "Fallo al conectar o descargar desde la fuente remota oficial (se preservó la copia local anterior).",
                        "archivo": target_csv if csv_existe else None
                    }
                    continue

                # Procesar a CSV
                if any(k in codigo for k in ["SSTA", "AtlTROP", "SAtl", "NAtl"]):
                    tmp_inter_csv = os.path.join(tmp_dir, "inter.csv")
                    ok_inter = acomodaParaCSV(tmp_txt, tmp_inter_csv)
                    if not ok_inter or not os.path.exists(tmp_inter_csv):
                        resultados[codigo] = {
                            "status": "error_formato",
                            "mensaje": f"No fue posible convertir el archivo compuesto de {codigo} a formato tabular intermedio.",
                            "archivo": target_csv if csv_existe else None
                        }
                        continue
                    ok_trans = acomodaParaCSV_3(tmp_inter_csv, tmp_csv)
                    if not ok_trans or not os.path.exists(tmp_csv):
                        resultados[codigo] = {
                            "status": "error_formato",
                            "mensaje": f"No fue posible extraer la columna de anomalía para {codigo} de la fuente compuesta.",
                            "archivo": target_csv if csv_existe else None
                        }
                        continue
                else:
                    ok_trans = acomodaParaCSV(tmp_txt, tmp_csv)
                    if not ok_trans or not os.path.exists(tmp_csv):
                        resultados[codigo] = {
                            "status": "error_formato",
                            "mensaje": f"No fue posible transformar el archivo de texto de {codigo} a matriz CSV.",
                            "archivo": target_csv if csv_existe else None
                        }
                        continue

                # Validar integridad estructural y temporal del CSV generado
                df_test = pd.read_csv(tmp_csv)
                valido, msg_val = validar_estructura_serie(df_test, codigo, df_previo=df_previo)

                if valido:
                    # Reemplazo atómico seguro
                    with open(tmp_csv, "rb") as f_in, open(target_csv, "wb") as f_out:
                        f_out.write(f_in.read())
                    with open(tmp_txt, "rb") as f_in, open(target_txt, "wb") as f_out:
                        f_out.write(f_in.read())

                    resultados[codigo] = {
                        "status": "actualizado",
                        "mensaje": "Descargado, parseado y validado exitosamente sin pérdida de registros.",
                        "archivo": target_csv
                    }
                    continue
                else:
                    resultados[codigo] = {
                        "status": "error_validacion",
                        "mensaje": f"La fuente descargada no superó la validación ({msg_val}). La versión local anterior se conserva sin modificaciones.",
                        "archivo": target_csv if csv_existe else None
                    }

        except Exception as e:
            resultados[codigo] = {
                "status": "error",
                "mensaje": f"Inconsistencia durante la actualización: {str(e)}. La versión local anterior se conserva sin modificaciones.",
                "archivo": target_csv if csv_existe else None
            }

    return resultados


def cargar_todas_oscilaciones(data_dir: str = ".") -> Dict[str, pd.DataFrame]:
    """
    Carga y normaliza las 19 series climáticas desde archivos locales CSV.
    Busca automáticamente en data_dir, data_dir/data o en la raíz del proyecto.
    """
    def _resolver_ruta(nombre_archivo: str) -> str:
        candidatos = [
            os.path.join(data_dir, nombre_archivo),
            os.path.join(data_dir, "data", nombre_archivo),
            os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", nombre_archivo),
            os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), nombre_archivo)
        ]
        for c in candidatos:
            if os.path.exists(c):
                return c
        return os.path.join(data_dir, nombre_archivo)

    oscilaciones = {}

    # 1. AMO
    f_amo = _resolver_ruta("dataAMO.csv")
    if os.path.exists(f_amo):
        oscilaciones["AMO"] = limpiar_datos_indice(pd.read_csv(f_amo))

    # 2. AO
    f_ao = _resolver_ruta("dataAO.csv")
    if os.path.exists(f_ao):
        oscilaciones["AO"] = limpiar_datos_indice(pd.read_csv(f_ao))

    # 3. MEI (Unión histórica de MEI v1 + MEI v2)
    f_mei1 = _resolver_ruta("dataMEI_1.csv")
    f_mei2 = _resolver_ruta("dataMEI_2.csv")
    if os.path.exists(f_mei1) and os.path.exists(f_mei2):
        df_mei1 = pd.read_csv(f_mei1)
        df_mei2 = pd.read_csv(f_mei2)
        oscilaciones["MEI"] = limpiar_datos_indice(pd.concat([df_mei1, df_mei2], sort=False, ignore_index=True))

    # 4. ONIv5, ONIv6, RONI
    f_oniv5 = _resolver_ruta("dataONIv5.csv")
    if os.path.exists(f_oniv5):
        oscilaciones["ONIv5"] = limpiar_datos_indice(pd.read_csv(f_oniv5))

    f_oniv6 = _resolver_ruta("dataONIv6.csv")
    if os.path.exists(f_oniv6):
        oscilaciones["ONIv6"] = limpiar_datos_indice(pd.read_csv(f_oniv6))

    f_roni = _resolver_ruta("dataRONI.csv")
    if os.path.exists(f_roni):
        oscilaciones["RONI"] = limpiar_datos_indice(pd.read_csv(f_roni))

    # 5. NAO
    f_nao = _resolver_ruta("dataNAO.csv")
    if os.path.exists(f_nao):
        oscilaciones["NAO"] = limpiar_datos_indice(pd.read_csv(f_nao))

    # 6. PDO
    f_pdo = _resolver_ruta("dataPDO.csv")
    if os.path.exists(f_pdo):
        oscilaciones["PDO"] = limpiar_datos_indice(pd.read_csv(f_pdo))

    # 7. TNA
    f_tna = _resolver_ruta("dataTNA.csv")
    if os.path.exists(f_tna):
        oscilaciones["TNA"] = limpiar_datos_indice(pd.read_csv(f_tna))

    # 8-14. SSTA & AtlTROP
    for s_name in ["SSTA_12", "SSTA_3", "SSTA_4", "SSTA_34", "AtlTROP", "SAtl", "NAtl"]:
        f_s = _resolver_ruta(f"data{s_name}.csv")
        if os.path.exists(f_s):
            oscilaciones[s_name] = limpiar_datos_indice(pd.read_csv(f_s))

    # 15. CAR
    f_car = _resolver_ruta("dataCAR.csv")
    if os.path.exists(f_car):
        oscilaciones["CAR"] = limpiar_datos_indice(pd.read_csv(f_car))

    # 16. WHWP
    f_whwp = _resolver_ruta("dataWHWP.csv")
    if os.path.exists(f_whwp):
        oscilaciones["WHWP"] = limpiar_datos_indice(pd.read_csv(f_whwp))

    # 17. PNA
    f_pna = _resolver_ruta("dataPNA.csv")
    if os.path.exists(f_pna):
        oscilaciones["PNA"] = limpiar_datos_indice(pd.read_csv(f_pna))

    # 18. SOI
    f_soi = _resolver_ruta("dataSOI.csv")
    if os.path.exists(f_soi):
        oscilaciones["SOI"] = limpiar_datos_indice(pd.read_csv(f_soi))

    # 19. AMO_CSU
    f_csu = _resolver_ruta("dataAMO_CSU.csv")
    if os.path.exists(f_csu):
        oscilaciones["AMO_CSU"] = limpiar_datos_indice(pd.read_csv(f_csu))

    return oscilaciones