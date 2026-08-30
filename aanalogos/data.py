"""
Módulo de descarga, parsing y carga de series temporales de oscilaciones climáticas.
"""

import os
import tempfile
import urllib.request
import requests
import pandas as pd
import numpy as np
from typing import Dict, Optional, Any, Callable

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None

from .config import FUENTES_DATOS
from .quality import limpiar_datos_indice


def descarga_segura(url: str, ruta_salida: str, timeout: int = 10) -> bool:
    """Descarga un archivo desde una URL si no existe localmente o para actualización."""
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AAnalogos/3.1"}
        )
        with urllib.request.urlopen(req, timeout=timeout) as response:
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


def acomodaParaCSV(ruta_entrada: str, ruta_salida: str) -> bool:
    """Convierte matriz de texto espacio-separada a CSV estructurado soportando años parciales."""
    if not os.path.exists(ruta_entrada):
        return False
    try:
        with open(ruta_entrada, "r", encoding="utf-8", errors="ignore") as ptr:
            lineas = ptr.readlines()

        if not lineas:
            return False

        with open(ruta_salida, "w", encoding="utf-8", newline="\n") as ptr:
            if ruta_entrada.endswith("dataSSTA.txt"):
                ptr.write("YEAR,MONTH,NINO1+2,ANOM1+2,NINO3,ANOM3,NINO4,ANOM4,NINO3.4,ANOM3.4")
            elif ruta_entrada.endswith("dataSSTOI.txt"):
                ptr.write("YEAR,MONTH,NAtl,ANOM_NAtl,SAtl,ANOM_SAtl,TROP,ANOM_TROP")
            else:
                ptr.write("YEAR,ENE,FEB,MAR,ABR,MAY,JUN,JUL,AGO,SET,OCT,NOV,DIC")

            for linea in lineas[1:]:
                linea_tokens = [v for v in linea.strip().split(" ") if v != ""]
                if not linea_tokens:
                    continue
                # Si la fila corresponde a matriz mensual y tiene menos de 13 tokens (ej. año parcial 2026 con 5 meses),
                # rellenar con cadenas vacías para que pandas las interprete como NaN
                if not (ruta_entrada.endswith("dataSSTA.txt") or ruta_entrada.endswith("dataSSTOI.txt")):
                    if len(linea_tokens) < 13:
                        linea_tokens = linea_tokens + [""] * (13 - len(linea_tokens))
                    elif len(linea_tokens) > 13:
                        linea_tokens = linea_tokens[:13]
                ptr.write("\n" + ",".join(linea_tokens))
        return True
    except Exception:
        return False


def acomodaParaCSV_2(url: str, archivocreado: str) -> bool:
    """Extrae tablas HTML (ej. ONIv5, ONIv6, RONI o AMO_CSU) y genera matriz de texto soportando años parciales."""
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AAnalogos/3.2"}
        )
        with urllib.request.urlopen(req, timeout=15) as response:
            if response.status != 200:
                return False
            html_text = response.read().decode("utf-8", errors="ignore")

        if not html_text or len(html_text) < 100:
            return False

        fname = os.path.basename(archivocreado)

        # 1. Extracción con expresiones regulares estándar (sin dependencia de bs4)
        import re
        rows = re.findall(r'<tr[^>]*>(.*?)</tr>', html_text, re.DOTALL | re.IGNORECASE)
        parsed_rows = []

        for row in rows:
            cells = re.findall(r'<(?:td|th)[^>]*>(.*?)</(?:td|th)>', row, re.DOTALL | re.IGNORECASE)
            clean_cells = [re.sub(r'<[^>]+>', '', c).strip() for c in cells]
            if clean_cells and re.match(r'^\d{4}$', clean_cells[0]):
                year_val = int(clean_cells[0])
                # Aceptar filas válidas incluso si el año está parcialmente publicado (>= 2 celdas: año + meses disponibles)
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

        # 2. Fallback a BeautifulSoup si está instalado
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


def verificar_y_descargar_datos(
    data_dir: str = ".",
    force_update: bool = False,
    progress_callback: Optional[Callable[[str, int, int], None]] = None
) -> Dict[str, dict]:
    """
    Verifica la existencia e integridad de los archivos CSV para las 19 series climáticas.
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

        # Proceso de descarga atómica
        try:
            with tempfile.TemporaryDirectory() as tmp_dir:
                tmp_txt = os.path.join(tmp_dir, txt_name)
                tmp_csv = os.path.join(tmp_dir, csv_name)

                # Descargar
                if "ONI" in codigo or "AMO_CSU" in codigo:
                    ok = acomodaParaCSV_2(url, tmp_txt)
                else:
                    ok = descarga_segura(url, tmp_txt)

                if not ok or not os.path.exists(tmp_txt) or os.path.getsize(tmp_txt) < 50:
                    resultados[codigo] = {
                        "status": "error_descarga",
                        "mensaje": "Fallo al descargar fuente remota (se preservó dato local si existía)",
                        "archivo": target_csv if csv_existe else None
                    }
                    continue

                # Procesar a CSV
                if any(k in codigo for k in ["SSTA", "AtlTROP", "SAtl", "NAtl"]):
                    # Requiere paso intermedio con dataSSTA.csv o dataSSTOI.csv
                    tmp_inter_csv = os.path.join(tmp_dir, "inter.csv")
                    acomodaParaCSV(tmp_txt, tmp_inter_csv)
                    acomodaParaCSV_3(tmp_inter_csv, tmp_csv)
                else:
                    acomodaParaCSV(tmp_txt, tmp_csv)

                # Validar integridad del CSV generado
                if os.path.exists(tmp_csv) and os.path.getsize(tmp_csv) > 100:
                    df_test = pd.read_csv(tmp_csv)
                    if len(df_test) >= 10 and "YEAR" in df_test.columns:
                        # Reemplazo atómico
                        with open(tmp_csv, "rb") as f_in, open(target_csv, "wb") as f_out:
                            f_out.write(f_in.read())
                        with open(tmp_txt, "rb") as f_in, open(target_txt, "wb") as f_out:
                            f_out.write(f_in.read())

                        resultados[codigo] = {
                            "status": "actualizado",
                            "mensaje": "Descargado y validado exitosamente",
                            "archivo": target_csv
                        }
                        continue

            resultados[codigo] = {
                "status": "error_formato",
                "mensaje": "El archivo descargado no superó la prueba de formato CSV",
                "archivo": target_csv if csv_existe else None
            }

        except Exception as e:
            resultados[codigo] = {
                "status": "error",
                "mensaje": f"Excepción durante actualización: {str(e)}",
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
        oscilaciones["AMO"] = limpiar_datos_indice(pd.read_csv(f_amo, skipfooter=4, engine="python", skiprows=[1, 2]))

    # 2. AO
    f_ao = _resolver_ruta("dataAO.csv")
    if os.path.exists(f_ao):
        oscilaciones["AO"] = limpiar_datos_indice(pd.read_csv(f_ao))

    # 3. MEI
    f_mei1 = _resolver_ruta("dataMEI_1.csv")
    f_mei2 = _resolver_ruta("dataMEI_2.csv")
    if os.path.exists(f_mei1) and os.path.exists(f_mei2):
        df_mei1 = pd.read_csv(f_mei1)
        df_mei2 = pd.read_csv(f_mei2, skipfooter=4, engine="python")
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
        oscilaciones["NAO"] = limpiar_datos_indice(pd.read_csv(f_nao, skipfooter=3, engine="python", skiprows=[1, 2]))

    # 6. PDO
    f_pdo = _resolver_ruta("dataPDO.csv")
    if os.path.exists(f_pdo):
        oscilaciones["PDO"] = limpiar_datos_indice(pd.read_csv(f_pdo, skiprows=[i for i in range(1, 98)]))

    # 7. TNA
    f_tna = _resolver_ruta("dataTNA.csv")
    if os.path.exists(f_tna):
        oscilaciones["TNA"] = limpiar_datos_indice(pd.read_csv(f_tna, skipfooter=7, engine="python", skiprows=[1, 2]))

    # 8-14. SSTA & AtlTROP
    for s_name in ["SSTA_12", "SSTA_3", "SSTA_4", "SSTA_34", "AtlTROP", "SAtl", "NAtl"]:
        f_s = _resolver_ruta(f"data{s_name}.csv")
        if os.path.exists(f_s):
            oscilaciones[s_name] = limpiar_datos_indice(pd.read_csv(f_s))

    # 15. CAR
    f_car = _resolver_ruta("dataCAR.csv")
    if os.path.exists(f_car):
        oscilaciones["CAR"] = limpiar_datos_indice(pd.read_csv(f_car, skipfooter=7, engine="python"))

    # 16. WHWP
    f_whwp = _resolver_ruta("dataWHWP.csv")
    if os.path.exists(f_whwp):
        oscilaciones["WHWP"] = limpiar_datos_indice(pd.read_csv(f_whwp, skipfooter=8, engine="python", skiprows=[1, 2]))

    # 17. PNA
    f_pna = _resolver_ruta("dataPNA.csv")
    if os.path.exists(f_pna):
        oscilaciones["PNA"] = limpiar_datos_indice(pd.read_csv(f_pna, skipfooter=3, engine="python", skiprows=[1, 2]))

    # 18. SOI
    f_soi = _resolver_ruta("dataSOI.csv")
    if os.path.exists(f_soi):
        oscilaciones["SOI"] = limpiar_datos_indice(pd.read_csv(f_soi, skiprows=[i for i in range(1, 88)], skipfooter=9, engine="python"))

    # 19. AMO_CSU
    f_csu = _resolver_ruta("dataAMO_CSU.csv")
    if os.path.exists(f_csu):
        oscilaciones["AMO_CSU"] = limpiar_datos_indice(pd.read_csv(f_csu))

    return oscilaciones