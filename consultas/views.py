# consultas/views.py

import csv
import pandas as pd
from io import StringIO, BytesIO
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse, JsonResponse, QueryDict
from django.contrib import messages

from dashboard.models import CampaignRecord
from .forms import CampaignFilterForm
from .services import FilterManager
from .models import SavedFilter

def data_explorer_view(request):
    """
    Esta vista ahora solo prepara el esqueleto de la página y el formulario de filtros.
    El llenado de datos se hará con JavaScript y la API.
    """
    form = CampaignFilterForm()
    saved_filters = SavedFilter.objects.all()
    
    context = {
        'form': form,
        'saved_filters': saved_filters,
    }
    return render(request, 'consultas/data_explorer.html', context)


def filter_data_api_view(request):
    """
    Vista de API que maneja las solicitudes AJAX, aplica los filtros,
    y devuelve los datos de la tabla en formato JSON.
    """
    queryset = CampaignRecord.objects.all()
    form = CampaignFilterForm(request.GET)
    
    if form.is_valid():
        filtered_queryset = FilterManager.apply_filters(queryset, form.cleaned_data)
    else:
        # Devolver un error si los parámetros de la URL son inválidos
        return JsonResponse({'error': 'Parámetros de filtro inválidos', 'details': form.errors}, status=400)

    sort_by = request.GET.get('sort_by', 'id')
    if sort_by in [f.name for f in CampaignRecord._meta.get_fields()]:
        filtered_queryset = filtered_queryset.order_by(sort_by)

    paginator = Paginator(filtered_queryset, 25)
    page_number = request.GET.get('page', 1)
    
    try:
        page_obj = paginator.page(page_number)
    except EmptyPage:
        # Si la página está fuera de rango, devuelve una página vacía en JSON
        return JsonResponse({'records': [], 'total_records': 0, 'total_pages': 0, 'current_page': page_number})

    records_data = list(page_obj.object_list.values(
        'id', 'age', 'job', 'marital', 'education', 'balance'
    ))

    data = {
        'records': records_data,
        'total_records': paginator.count,
        'total_pages': paginator.num_pages,
        'current_page': page_obj.number,
        'has_previous': page_obj.has_previous(),
        'has_next': page_obj.has_next(),
    }
    
    return JsonResponse(data)


def save_filter_view(request):
    if request.method == 'POST':
        filter_name = request.POST.get('filter_name')
        query_params = request.POST.get('query_params')

        if not filter_name:
            messages.error(request, "El nombre del filtro no puede estar vacío.")
        else:
            params_dict = QueryDict(query_params).dict()
            if 'csrfmiddlewaretoken' in params_dict:
                del params_dict['csrfmiddlewaretoken']

            SavedFilter.objects.create(name=filter_name, parameters=params_dict)
            messages.success(request, f"Filtro '{filter_name}' guardado con éxito.")
            
    return redirect(f"{request.META.get('HTTP_REFERER', '/data/')}?{query_params}")

def load_filter_view(request, filter_id):
    saved_filter = get_object_or_404(SavedFilter, pk=filter_id)
    query_string = QueryDict('', mutable=True)
    query_string.update(saved_filter.parameters)
    return redirect(f"/data/?{query_string.urlencode()}")

def export_data_view(request):
    export_format = request.GET.get('format', 'csv')
    
    queryset = CampaignRecord.objects.all()
    form = CampaignFilterForm(request.GET)
    if form.is_valid():
        filtered_queryset = FilterManager.apply_filters(queryset, form.cleaned_data)
    else:
        filtered_queryset = queryset
        
    sort_by = request.GET.get('sort_by', 'id')
    if sort_by:
        filtered_queryset = filtered_queryset.order_by(sort_by)

    data = list(filtered_queryset.values())
    
    if not data:
        messages.error(request, "No hay datos para exportar.")
        return redirect(f"{request.META.get('HTTP_REFERER', '/data/')}")

    if export_format == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="export_data.csv"'
        writer = csv.DictWriter(response, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
        return response

    elif export_format == 'excel':
        df = pd.DataFrame(data)
        buffer = BytesIO()
        df.to_excel(buffer, index=False, engine='openpyxl')
        buffer.seek(0)
        response = HttpResponse(buffer, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="export_data.xlsx"'
        return response
    
    return redirect('/data/')