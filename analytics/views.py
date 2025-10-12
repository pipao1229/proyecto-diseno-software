# analytics/views.py

from django.shortcuts import render
from django.http import JsonResponse, HttpResponseBadRequest

from consultas.forms import CampaignFilterForm
from consultas.services import FilterManager
from dashboard.models import CampaignRecord
from .services import KpiManager

def analytics_dashboard_view(request):
    """
    Renderiza el esqueleto del dashboard de analytics.
    El contenido se carga dinámicamente vía AJAX.
    """
    form = CampaignFilterForm()
    # Pasamos el formulario al contexto para que se puedan renderizar las píldoras de filtros
    return render(request, 'analytics/analytics_dashboard.html', {'form': form})

def kpi_data_api_view(request):
    """
    Endpoint de API que calcula y devuelve todos los datos
    de KPIs y gráficos basados en los filtros de la URL.
    """
    # Usamos los mismos formularios y gestor de filtros que en la app `consultas`
    form = CampaignFilterForm(request.GET)

    if not form.is_valid():
        return HttpResponseBadRequest(f"Parámetros de filtro inválidos: {form.errors.as_json()}")
        
    # Aplicar filtros
    base_queryset = CampaignRecord.objects.all()
    filtered_queryset = FilterManager.apply_filters(base_queryset, form.cleaned_data)
    
    # Usar el KpiManager para calcular todo
    kpi_manager = KpiManager(filtered_queryset)
    data = kpi_manager.get_all_kpis()
    
    return JsonResponse(data)