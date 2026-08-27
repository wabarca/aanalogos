"""
Configuraciones, constantes y umbrales univariados por oscilación climática.
"""

LONGITUD_VENTANA = 6
UMBRAL_SENTINELA_MIN = -50.0
UMBRAL_SENTINELA_MAX = 50.0

# Umbrales específicos validados para cada una de las 19 oscilaciones
# Estructura: indice -> (r_minimo, mad_maximo)
UMBRALES_OSCILACIONES = {
    "ONI": (0.6, 0.6),
    "AMO": (0.6, 0.3),
    "SOI": (0.6, 0.3),
    "AMO_CSU": (0.6, 0.3),
    "AO": (0.4, 1.0),
    "MEI": (0.4, 0.5),
    "NAO": (0.6, 0.8),
    "PDO": (0.4, 0.6),
    "TNA": (0.5, 0.3),
    "SSTA_12": (0.6, 0.6),
    "SSTA_34": (0.6, 0.6),
    "AtlTROP": (0.6, 0.6),
    "SAtl": (0.6, 0.6),
    "NAtl": (0.6, 0.6),
    "CAR": (0.6, 0.6),
    "WHWP": (0.6, 0.6),
    "PNA": (0.6, 0.6),
    "SSTA_3": (0.5, 0.7),
    "SSTA_4": (0.38, 0.7),
}

NOMBRES_MESES = [
    "ENE", "FEB", "MAR", "ABR", "MAY", "JUN",
    "JUL", "AGO", "SET", "OCT", "NOV", "DIC"
]

FUENTES_DATOS = {
    "AMO": {"url": "https://psl.noaa.gov/data/correlation/amon.us.data", "txt": "dataAMO.txt", "csv": "dataAMO.csv"},
    "AO": {"url": "https://www.cpc.ncep.noaa.gov/products/precip/CWlink/daily_ao_index/monthly.ao.index.b50.current.ascii.table", "txt": "dataAO.txt", "csv": "dataAO.csv"},
    "MEI": {"url": "https://psl.noaa.gov/enso/mei/data/meiv2.data", "txt": "dataMEI_2.txt", "csv": "dataMEI_2.csv"},
    "ONI": {"url": "https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/enso/oni/v6/", "txt": "dataONI.txt", "csv": "dataONI.csv"},
    "NAO": {"url": "https://psl.noaa.gov/data/correlation/nao.data", "txt": "dataNAO.txt", "csv": "dataNAO.csv"},
    "PDO": {"url": "https://www.ncei.noaa.gov/pub/data/cmb/ersst/v5/v6/index/ersst.v6.pdo.dat", "txt": "dataPDO.txt", "csv": "dataPDO.csv"},
    "TNA": {"url": "https://psl.noaa.gov/data/correlation/tna.data", "txt": "dataTNA.txt", "csv": "dataTNA.csv"},
    "SSTA_12": {"url": "https://www.cpc.ncep.noaa.gov/data/indices/sstoi.indices", "txt": "dataSSTA.txt", "csv": "dataSSTA_12.csv"},
    "SSTA_3": {"url": "https://www.cpc.ncep.noaa.gov/data/indices/sstoi.indices", "txt": "dataSSTA.txt", "csv": "dataSSTA_3.csv"},
    "SSTA_4": {"url": "https://www.cpc.ncep.noaa.gov/data/indices/sstoi.indices", "txt": "dataSSTA.txt", "csv": "dataSSTA_4.csv"},
    "SSTA_34": {"url": "https://www.cpc.ncep.noaa.gov/data/indices/sstoi.indices", "txt": "dataSSTA.txt", "csv": "dataSSTA_34.csv"},
    "AtlTROP": {"url": "https://ftp.cpc.ncep.noaa.gov/wd52dg/data/indices/sstoi.atl.indices", "txt": "dataSSTOI.txt", "csv": "dataAtlTROP.csv"},
    "SAtl": {"url": "https://ftp.cpc.ncep.noaa.gov/wd52dg/data/indices/sstoi.atl.indices", "txt": "dataSSTOI.txt", "csv": "dataSAtl.csv"},
    "NAtl": {"url": "https://ftp.cpc.ncep.noaa.gov/wd52dg/data/indices/sstoi.atl.indices", "txt": "dataSSTOI.txt", "csv": "dataNAtl.csv"},
    "CAR": {"url": "https://psl.noaa.gov/data/correlation/CAR_ersst.data", "txt": "dataCAR.txt", "csv": "dataCAR.csv"},
    "WHWP": {"url": "https://psl.noaa.gov/data/correlation/whwp.data", "txt": "dataWHWP.txt", "csv": "dataWHWP.csv"},
    "PNA": {"url": "https://psl.noaa.gov/data/correlation/pna.data", "txt": "dataPNA.txt", "csv": "dataPNA.csv"},
    "SOI": {"url": "https://www.cpc.ncep.noaa.gov/data/indices/soi", "txt": "dataSOI.txt", "csv": "dataSOI.csv"},
    "AMO_CSU": {"url": "https://tropical.colostate.edu/archive.html#amo", "txt": "dataAMO_CSU.txt", "csv": "dataAMO_CSU.csv"},
}
