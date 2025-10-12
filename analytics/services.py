# analytics/services.py

from django.db import models # <-- ¡LA LÍNEA QUE FALTABA!
from django.db.models import (
    Avg, Count, Sum, Case, When, Value, IntegerField, F, Q, FloatField
)
from django.db.models.functions import Coalesce, Cast
from collections import OrderedDict

class KpiManager:
    """
    GestorKPIs: Calcula todas las métricas y datos para gráficos
    a partir de un QuerySet filtrado de CampaignRecord.
    """
    def __init__(self, queryset):
        self.queryset = queryset
        self.total_count = self.queryset.count()
        self.yes_count = self.queryset.filter(y=True).count()

        # Parámetros para rentabilidad
        self.G = 10  # Ganancia unitaria
        self.C = 1   # Costo por llamada

    def _safe_division(self, numerator, denominator, as_percentage=True):
        if denominator == 0:
            return 0
        result = (numerator / denominator)
        return result * 100 if as_percentage else result

    def get_all_kpis(self):
        """
        Calcula todos los KPIs y los devuelve en un diccionario.
        """
        # --- TARJETAS KPI ---
        total_contacts_sum = self.queryset.aggregate(total=Coalesce(Sum('campaign'), Value(0)))['total']
        profitability = (self.yes_count * self.G) - (self.total_count * self.C)

        success_outcome_qs = self.queryset.filter(poutcome='success')
        success_outcome_count = success_outcome_qs.count()
        converted_with_success_history = success_outcome_qs.filter(y=True).count()
        
        return {
            # Data para Tarjetas KPI
            "kpi_cards": {
                "tasa_conversion": self._safe_division(self.yes_count, self.total_count),
                "total_contactos": self.total_count,
                "duracion_promedio": self.queryset.aggregate(avg_dur=Coalesce(Avg('duration'), Value(0.0), output_field=FloatField()))['avg_dur'],
                "rentabilidad_proyectada": profitability,
                "clientes_aceptaron": self.yes_count,
                "historiales_exitosos": success_outcome_count,
                "impacto_historial": self._safe_division(converted_with_success_history, success_outcome_count),
                "indice_eficiencia": self._safe_division(self.yes_count, total_contacts_sum if total_contacts_sum > 0 else 1, as_percentage=False),
                "ganancia_por_llamada": self._safe_division(profitability, total_contacts_sum if total_contacts_sum > 0 else 1, as_percentage=False)
            },
            # Data para Gráficos
            "charts": {
                "conversion_por_edad": self._get_conversion_by_age_data(),
                "distribucion_resultados": self._get_results_distribution_data(),
                "tendencia_mensual": self._get_monthly_trend_data(),
                "exito_por_canal": self._get_success_by_contact_data(),
                "distribucion_demora": self._get_simple_distribution('default'),
                "distribucion_hipoteca": self._get_simple_distribution('housing'),
                "distribucion_prestamo": self._get_simple_distribution('loan'),
                "distribucion_edades": self._get_age_distribution_data(),
                "distribucion_balance": self._get_balance_distribution_data(),
                "distribucion_estado_civil": self._get_marital_distribution_data(),
                "distribucion_duracion": self._get_duration_distribution_data(),
                "distribucion_dia_mes": self._get_day_of_month_data(),
                "contactos_previos_conversion": self._get_previous_contacts_conversion_data(),
                "dias_ultimo_contacto": self._get_pdays_analysis_data(),
            }
        }
    
    # --- Métodos auxiliares para cada gráfico ---
    def _get_conversion_by_age_data(self):
        age_groups = {
            '17-25': (17, 25), '26-35': (26, 35), '36-45': (36, 45),
            '46-55': (46, 55), '56+': (56, 100)
        }
        data = {'labels': list(age_groups.keys()), 'data': []}
        for group, (min_age, max_age) in age_groups.items():
            group_qs = self.queryset.filter(age__gte=min_age, age__lte=max_age)
            total = group_qs.count()
            yes = group_qs.filter(y=True).count()
            data['data'].append(self._safe_division(yes, total))
        return data

    def _get_results_distribution_data(self):
        results = self.queryset.values('y').annotate(count=Count('y')).order_by('y')
        return {
            'labels': ['No Aceptaron', 'Sí Aceptaron'],
            'data': [next((r['count'] for r in results if r['y'] is False), 0),
                     next((r['count'] for r in results if r['y'] is True), 0)]
        }
        
    def _get_monthly_trend_data(self):
        months_order = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
        monthly_data = self.queryset.values('month').annotate(
            total=Count('id'),
            conversions=Count('id', filter=Q(y=True))
        ).order_by()

        data_dict = {d['month']: d for d in monthly_data}
        
        rates = []
        for month in months_order:
            if month in data_dict:
                rates.append(self._safe_division(data_dict[month]['conversions'], data_dict[month]['total']))
            else:
                rates.append(0)
        return {'labels': months_order, 'data': rates}
    
    def _get_success_by_contact_data(self):
        contact_data = self.queryset.exclude(contact='unknown').values('contact').annotate(
            total=Count('id'), conversions=Count('id', filter=Q(y=True))
        )
        return {
            'labels': [d['contact'] for d in contact_data],
            'data': [self._safe_division(d['conversions'], d['total']) for d in contact_data]
        }
        
    def _get_simple_distribution(self, field_name):
        results = self.queryset.values(field_name).annotate(count=Count(field_name)).order_by(field_name)
        return {
            'labels': ['No', 'Sí'],
            'data': [next((r['count'] for r in results if r[field_name] is False), 0),
                     next((r['count'] for r in results if r[field_name] is True), 0)]
        }
        
    def _get_age_distribution_data(self):
        results = self.queryset.annotate(
            age_group=Case(
                When(age__range=(17, 25), then=Value('17-25')),
                When(age__range=(26, 34), then=Value('26-34')),
                When(age__range=(35, 43), then=Value('35-43')),
                When(age__range=(44, 52), then=Value('44-52')),
                When(age__range=(53, 61), then=Value('53-61')),
                When(age__gte=62, then=Value('62+')),
                default=Value('Otro'),
                output_field=models.CharField(),
            )
        ).values('age_group').annotate(count=Count('id')).order_by('age_group')
        return {'labels': [r['age_group'] for r in results], 'data': [r['count'] for r in results]}
        
    def _get_balance_distribution_data(self):
        results = self.queryset.annotate(
            balance_group=Case(
                When(balance__lt=0, then=Value('< 0')),
                When(balance__range=(0, 1000), then=Value('0-1k')),
                When(balance__range=(1001, 2000), then=Value('1k-2k')),
                When(balance__range=(2001, 5000), then=Value('2k-5k')),
                When(balance__gt=5000, then=Value('> 5k')),
                output_field=models.CharField()
            )
        ).values('balance_group').annotate(count=Count('id')).order_by('balance_group')
        return {'labels': [r['balance_group'] for r in results], 'data': [r['count'] for r in results]}

    def _get_marital_distribution_data(self):
        results = self.queryset.values('marital').annotate(count=Count('id'))
        return {'labels': [r['marital'] for r in results], 'data': [r['count'] for r in results]}
        
    def _get_duration_distribution_data(self):
        results = self.queryset.annotate(
            duration_group=Case(
                When(duration__range=(0, 100), then=Value('0-100s')),
                When(duration__range=(101, 200), then=Value('101-200s')),
                When(duration__range=(201, 300), then=Value('201-300s')),
                When(duration__range=(301, 400), then=Value('301-400s')),
                When(duration__range=(401, 500), then=Value('401-500s')),
                When(duration__gt=500, then=Value('500s+')),
                output_field=models.CharField()
            )
        ).values('duration_group').annotate(count=Count('id')).order_by('duration_group')
        return {'labels': [r['duration_group'] for r in results], 'data': [r['count'] for r in results]}

    def _get_day_of_month_data(self):
        days_in_month = list(range(1, 32))
        daily_data = self.queryset.values('day').annotate(
            total=Count('id'), conversions=Count('id', filter=Q(y=True))
        )
        data_dict = {d['day']: d for d in daily_data}
        rates = [self._safe_division(data_dict[d]['conversions'], data_dict[d]['total']) if d in data_dict else 0 for d in days_in_month]
        return {'labels': days_in_month, 'data': rates}
        
    def _get_previous_contacts_conversion_data(self):
        results = self.queryset.filter(previous__lte=10).values('previous').annotate(
            conversions=Cast(Count('id', filter=Q(y=True)), FloatField()),
            total=Cast(Count('id'), FloatField())
        ).order_by('previous')

        data = results.annotate(
            rate=Case(
                When(total__gt=0, then=(F('conversions') / F('total')) * 100),
                default=Value(0.0),
                output_field=FloatField()
            )
        )
        return {'labels': [r['previous'] for r in data], 'data': [r['rate'] for r in data]}
        
    def _get_pdays_analysis_data(self):
        results = self.queryset.annotate(
            pdays_group=Case(
                When(pdays=-1, then=Value('No contactado')),
                When(pdays__range=(0, 90), then=Value('0-90 días')),
                When(pdays__range=(91, 180), then=Value('91-180 días')),
                When(pdays__range=(181, 270), then=Value('181-270 días')),
                When(pdays__gt=270, then=Value('270+ días')),
                output_field=models.CharField()
            )
        ).values('pdays_group').annotate(count=Count('id')).order_by('pdays_group')
        return {'labels': [r['pdays_group'] for r in results], 'data': [r['count'] for r in results]}