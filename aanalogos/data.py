"""
Módulo de descarga, parsing y carga de series temporales de oscilaciones climáticas.
"""

import os
import urllib.request
import requests
import pandas as pd
import numpy as np
from typing import Dict, Optional

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None

from .config import FUENTES_DATOS
from .quality import limpiar_datos_indice


def descarga_segura(url: str, ruta_salida: str, timeout: int = 5) -> None:
    """Descarga un archivo desde una URL si no existe localmente."""
    if os.path.exists(ruta_salida):
        return
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        )
        with urllib.request.urlopen(req, timeout=timeout) as response:
            with open(ruta_salida, "wb") as f:
                f.write(response.read())
    except Exception:
        pass


def acomodaParaCSV(ruta_entrada: str, ruta_salida: str) -> None:
    if not os.path.exists(ruta_entrada) or os.path.exists(ruta_salida):
        return
    with open(ruta_entrada, "r") as ptr:
        lineas = ptr.readlines()

    with open(ruta_salida, "w") as ptr:
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
            ptr.write("\n" + ",".join(linea_tokens))


def acomodaParaCSV_2(url: str, archivocreado: str) -> None:
    if os.path.exists(archivocreado):
        return
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        r = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(r.text, "html.parser") if BeautifulSoup else None
        if soup is None:
            return

        if archivocreado.endswith("dataONI.txt"):
            table = soup.find("table", attrs={"border": "1"})
        elif archivocreado.endswith("dataAMO_CSU.txt"):
            table = soup.find("table", attrs={"id": "amo_table"})
        else:
            table = None

        if table is not None:
            with open(archivocreado, "w") as file:
                if archivocreado.endswith("dataAMO_CSU.txt"):
                    file.write("YEAR ENE FEB MAR ABR MAY JUN JUL AGO SET OCT NOV DIC\n")
                for row in table.find_all("tr")[0:]:
                    valores = [cell.get_text(strip=True) for cell in row.find_all("td")]
                    if valores:
                        file.write(" ".join(valores) + "\n")
    except Exception:
        pass


def acomodaParaCSV_3(archivo_descargado: str, archivo_creado: str) -> None:
    if not os.path.exists(archivo_descargado) or os.path.exists(archivo_creado):
        return
    archivo = pd.read_csv(archivo_descargado)
    anios = [archivo["YEAR"][i] for i in range(0, len(archivo), 12)]

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
        return

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

    # 4. ONI
    f_oni = _resolver_ruta("dataONI.csv")
    if os.path.exists(f_oni):
        oscilaciones["ONI"] = limpiar_datos_indice(pd.read_csv(f_oni))

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
