"""
Pruebas automatizadas de auditoría de variables de entrada, series ENSO (ONIv5, ONIv6, RONI)
y verificación de columnas de anomalía vs temperatura absoluta en SSTA.
"""

import unittest
import numpy as np
import pandas as pd
from aanalogos.catalog import cargar_catalogo_indices
from aanalogos.data import cargar_todas_oscilaciones
from aanalogos import calcular_analogos


class TestVariableAuditAndEnso(unittest.TestCase):
    def setUp(self):
        self.catalogo = cargar_catalogo_indices()
        self.oscilaciones = cargar_todas_oscilaciones()

    def test_enso_series_presence(self):
        """Verificar que ONIv5, ONIv6 y RONI existan como series independientes y ONI genérico no exista."""
        self.assertNotIn("ONI", self.catalogo, "'ONI' genérico no debe existir en el catálogo")
        self.assertNotIn("ONI", self.oscilaciones, "'ONI' genérico no debe existir en las oscilaciones cargadas")
        for enso_id in ["ONIv5", "ONIv6", "RONI"]:
            self.assertIn(enso_id, self.catalogo, f"{enso_id} debe estar en el catálogo")
            self.assertIn(enso_id, self.oscilaciones, f"{enso_id} debe estar cargada en oscilaciones")
            df = self.oscilaciones[enso_id]
            self.assertGreaterEqual(len(df), 50, f"{enso_id} debe tener al menos 50 años registrados")
            self.assertIn("YEAR", df.columns)
            self.assertIn("ENE", df.columns)

    def test_variable_audit_metadata_fields(self):
        """Verificar que todas las series tengan definidos los campos de auditoría de variables."""
        for codigo, meta in self.catalogo.items():
            self.assertIn("variable_type", meta, f"{codigo} debe tener 'variable_type'")
            self.assertIn("variable_column", meta, f"{codigo} debe tener 'variable_column'")
            self.assertIn("exact_variable_used", meta, f"{codigo} debe tener 'exact_variable_used'")
            self.assertIn(meta["variable_type"], ["anomalía", "índice", "índice estandarizado", "índice derivado", "variable absoluta"])

    def test_ssta_series_are_anomalies_not_absolute_sst(self):
        """
        Verificación física: Demostrar que las series SSTA (SSTA_12, SSTA_3, SSTA_4, SSTA_34, AtlTROP, SAtl, NAtl)
        contienen anomalías térmicas (típicamente entre -5.0 °C y +5.0 °C) y NO temperaturas absolutas (> 15.0 °C).
        """
        ssta_keys = ["SSTA_12", "SSTA_3", "SSTA_4", "SSTA_34", "AtlTROP", "SAtl", "NAtl"]
        for k in ssta_keys:
            if k in self.oscilaciones and self.oscilaciones[k] is not None:
                df = self.oscilaciones[k]
                meses_cols = [c for c in df.columns if c != "YEAR"]
                valores_validos = df[meses_cols].values.flatten()
                valores_validos = valores_validos[~np.isnan(valores_validos)]
                valores_validos = valores_validos[(valores_validos >= -50.0) & (valores_validos <= 50.0)]
                
                # Para una anomalía de TSM, el valor absoluto medio debe ser menor a 5.0 °C
                mean_abs = np.mean(np.abs(valores_validos))
                self.assertLess(mean_abs, 5.0, f"La serie {k} debe ser anomalía (mean_abs={mean_abs:.2f} < 5.0 °C)")
                
                # Ningún valor de anomalía debe superar los 12 °C (las SST absolutas tropicales son 20..30 °C)
                max_val = np.max(valores_validos)
                self.assertLess(max_val, 12.0, f"La serie {k} no debe contener temperaturas absolutas (max={max_val:.2f})")

    def test_calculation_with_new_enso_series(self):
        """Verificar que el motor de análogos calcule correctamente usando ONIv5, ONIv6 y RONI."""
        for enso_id in ["ONIv5", "ONIv6", "RONI"]:
            res = calcular_analogos(
                year_objetivo=2015,
                mes_objetivo=10,
                indices=[enso_id, "PDO"],
                longitud_ventana=12,
                oscilaciones_cargadas=self.oscilaciones
            )
            self.assertTrue(res.es_valido, f"El resultado para {enso_id} debe ser válido")
            self.assertGreater(len(res.tabla_coincidencias), 0, f"Debe generar candidatos válidos para {enso_id} + PDO")
            self.assertNotIn(2015, res.tabla_coincidencias.index, "Año objetivo 2015 debe ser excluido")


    def test_expected_sources_urls(self):
        """Comprobar que las URLs de las nuevas series ENSO y fuentes operacionales sean las esperadas."""
        expected_urls = {
            "ONIv5": "https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/enso/oni/v5/",
            "ONIv6": "https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/enso/oni/v6/",
            "RONI": "https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/enso/roni/",
            "AMO": "https://psl.noaa.gov/data/correlation/amon.us.data",
            "SOI": "https://psl.noaa.gov/data/correlation/soi.data",
            "AMO_CSU": "https://tropical.colostate.edu/Forecast/downloadable/csu_amo.csv",
            "AO": "https://www.cpc.ncep.noaa.gov/products/precip/CWlink/daily_ao_index/monthly.ao.index.b50.current.ascii.table",
            "MEI": "https://psl.noaa.gov/enso/mei/data/meiv2.data",
            "NAO": "https://psl.noaa.gov/data/correlation/nao.data",
            "PDO": "https://www.ncei.noaa.gov/pub/data/cmb/ersst/v5/index/ersst.v5.pdo.dat",
            "TNA": "https://psl.noaa.gov/data/correlation/tna.data",
            "SSTA_12": "https://www.cpc.ncep.noaa.gov/data/indices/sstoi.indices",
            "SSTA_34": "https://www.cpc.ncep.noaa.gov/data/indices/sstoi.indices",
            "AtlTROP": "https://ftp.cpc.ncep.noaa.gov/wd52dg/data/indices/sstoi.atl.indices",
            "SAtl": "https://ftp.cpc.ncep.noaa.gov/wd52dg/data/indices/sstoi.atl.indices",
            "NAtl": "https://ftp.cpc.ncep.noaa.gov/wd52dg/data/indices/sstoi.atl.indices",
            "CAR": "https://psl.noaa.gov/data/correlation/CAR_ersst.data",
            "WHWP": "https://psl.noaa.gov/data/correlation/whwp.data",
            "PNA": "https://psl.noaa.gov/data/correlation/pna.data",
            "SSTA_3": "https://www.cpc.ncep.noaa.gov/data/indices/sstoi.indices",
            "SSTA_4": "https://www.cpc.ncep.noaa.gov/data/indices/sstoi.indices"
        }
        for codigo, url_esperada in expected_urls.items():
            self.assertIn(codigo, self.catalogo, f"{codigo} debe existir en el catálogo")
            self.assertEqual(self.catalogo[codigo]["url"], url_esperada, f"URL de {codigo} debe coincidir")


if __name__ == "__main__":
    unittest.main()

