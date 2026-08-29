import unittest
import datetime
from aanalogos.catalog import determinar_ultimo_mes_disponible, obtener_periodo_evaluacion_operacional
from aanalogos.data import cargar_todas_oscilaciones


class TestOperationalDate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.oscilaciones = cargar_todas_oscilaciones()

    def test_determine_available_month_current_year(self):
        """Verifica que el mes operacional devuelto esté entre 1 y 12 y el año sea coherente."""
        y_op, m_op = determinar_ultimo_mes_disponible(self.oscilaciones)
        now = datetime.datetime.now()
        self.assertIn(y_op, [now.year, now.year - 1])
        self.assertGreaterEqual(m_op, 1)
        self.assertLessEqual(m_op, 12)

    def test_determine_available_month_historical(self):
        """Para un año histórico completo (ej. 2015), debe reportar mes 12 (Diciembre)."""
        y_op, m_op = determinar_ultimo_mes_disponible(self.oscilaciones, year=2015)
        self.assertEqual(y_op, 2015)
        self.assertEqual(m_op, 12)

    def test_operational_lag_rule_current_year(self):
        """Verifica que para el año en curso el mes operacional sea <= mes_actual - 1."""
        now = datetime.datetime.now()
        y_op, m_op = determinar_ultimo_mes_disponible(self.oscilaciones)
        if y_op == now.year:
            self.assertLessEqual(m_op, now.month - 1)

    def test_operational_evaluation_period_all_months(self):
        """
        Verifica formalmente la regla operacional para todos los casos solicitados:
        mes_evaluacion = mes_actual - 1, con año por defecto correspondiente y manejo de cambio de año.
        """
        # Caso Enero 2026 -> Diciembre 2025
        y_ene26, m_ene26 = obtener_periodo_evaluacion_operacional(datetime.date(2026, 1, 15))
        self.assertEqual(y_ene26, 2025)
        self.assertEqual(m_ene26, 12)

        # Caso Febrero 2026 -> Enero 2026
        y_feb26, m_feb26 = obtener_periodo_evaluacion_operacional(datetime.date(2026, 2, 10))
        self.assertEqual(y_feb26, 2026)
        self.assertEqual(m_feb26, 1)

        # Caso Marzo 2026 -> Febrero 2026
        y_mar26, m_mar26 = obtener_periodo_evaluacion_operacional(datetime.date(2026, 3, 1))
        self.assertEqual(y_mar26, 2026)
        self.assertEqual(m_mar26, 2)

        # Caso Julio 2026 -> Junio 2026
        y_jul26, m_jul26 = obtener_periodo_evaluacion_operacional(datetime.date(2026, 7, 20))
        self.assertEqual(y_jul26, 2026)
        self.assertEqual(m_jul26, 6)

        # Caso Agosto 2026 -> Julio 2026
        y_ago26, m_ago26 = obtener_periodo_evaluacion_operacional(datetime.date(2026, 8, 29))
        self.assertEqual(y_ago26, 2026)
        self.assertEqual(m_ago26, 7)

        # Caso Diciembre 2026 -> Noviembre 2026
        y_dic26, m_dic26 = obtener_periodo_evaluacion_operacional(datetime.date(2026, 12, 31))
        self.assertEqual(y_dic26, 2026)
        self.assertEqual(m_dic26, 11)

        # Caso Enero 2027 -> Diciembre 2026 (Cambio de Año)
        y_ene27, m_ene27 = obtener_periodo_evaluacion_operacional(datetime.date(2027, 1, 1))
        self.assertEqual(y_ene27, 2026)
        self.assertEqual(m_ene27, 12)
