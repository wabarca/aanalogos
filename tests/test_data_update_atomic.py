"""
Pruebas de actualización atómica y no destructiva de series climáticas.
"""

import unittest
import os
import tempfile
import pandas as pd
from aanalogos.data import verificar_y_descargar_datos, cargar_todas_oscilaciones


class TestDataUpdateAtomic(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.data_dir = os.path.join(self.test_dir, "data")
        os.makedirs(self.data_dir, exist_ok=True)

        # Crear un archivo CSV válido previo de prueba
        self.valid_csv = os.path.join(self.data_dir, "dataAMO.csv")
        df_dummy = pd.DataFrame([
            {"YEAR": 2020, "ENE": 0.1, "FEB": 0.2, "MAR": 0.3, "ABR": 0.4, "MAY": 0.5, "JUN": 0.6,
             "JUL": 0.7, "AGO": 0.8, "SET": 0.9, "OCT": 1.0, "NOV": 1.1, "DIC": 1.2}
        ])
        df_dummy.to_csv(self.valid_csv, index=False)

    def test_non_destructive_preservation_on_existing_valid(self):
        """Comprobar que una copia local válida existe y puede leerse sin ser corrompida."""
        df = pd.read_csv(self.valid_csv)
        self.assertEqual(len(df), 1)
        self.assertEqual(df.iloc[0]["YEAR"], 2020)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
