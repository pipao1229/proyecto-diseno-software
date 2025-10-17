# consultas/views.py

import csv
from io import BytesIO
from urllib.parse import urlencode
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator, EmptyPage
from django.http import HttpResponse, JsonResponse, QueryDict
from django.contrib import messages
from datetime import datetime
from django.views.decorators.http import require_POST

# Importaciones de ReportLab para el PDF
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, PageBreak
from reportlab.lib.units import inch

from dashboard.models import CampaignRecord
from .forms import CampaignFilterForm
from .services import FilterManager
from .services import FilterManager
from .models import SavedFilter
from history.models import QueryHistory

def data_explorer_view(request):
    """Renderiza el esqueleto de la página."""
    form = CampaignFilterForm()
    saved_filters = SavedFilter.objects.all()
    context = { 'form': form, 'saved_filters': saved_filters }
    return render(request, 'consultas/data_explorer.html', context)


def filter_data_api_view(request):
    queryset = CampaignRecord.objects.all()
    form = CampaignFilterForm(request.GET)
    if not form.is_valid():
        return JsonResponse({'error': 'Parámetros inválidos', 'details': form.errors}, status=400)
    
    filtered_queryset = FilterManager.apply_filters(queryset, form.cleaned_data)
    sort_by = request.GET.get('sort_by', 'id')
    valid_sort_fields = [f.name for f in CampaignRecord._meta.get_fields()]
    if sort_by.strip('-') in valid_sort_fields:
        filtered_queryset = filtered_queryset.order_by(sort_by)

    paginator = Paginator(filtered_queryset, 25)
    page_number = request.GET.get('page', 1)
    try:
        page_obj = paginator.page(page_number)
    except EmptyPage:
        return JsonResponse({'records': [], 'total_records': 0, 'total_pages': 0, 'current_page': page_number})

    records_data = list(page_obj.object_list.values('id', 'age', 'job', 'marital', 'education', 'balance', 'contact', 'y'))
    return JsonResponse({
        'records': records_data, 'total_records': paginator.count, 'total_pages': paginator.num_pages,
        'current_page': page_obj.number, 'has_previous': page_obj.has_previous(), 'has_next': page_obj.has_next()
    })

def save_filter_view(request):
    if request.method == 'POST':
        filter_name = request.POST.get('filter_name')
        query_params_str = request.POST.get('query_params')

        if filter_name and query_params_str:
            params_dict = dict(QueryDict(query_params_str, mutable=True).lists())

            record_count = FilterManager.apply_filters(
                CampaignRecord.objects.all(), params_dict
            ).count()
            
            # Limpiamos arrays innecesarios para valores únicos
            for key in ['page', 'sort_by', 'age_min', 'age_max']:
                if key in params_dict and isinstance(params_dict[key], list):
                    params_dict[key] = params_dict[key][0]

            new_filter = SavedFilter.objects.create(name=filter_name, parameters=params_dict)
            
            QueryHistory.objects.create(
                description=f"Se guardó el filtro: '{filter_name}'",
                records_count=record_count, 
                filters_applied=params_dict,
                saved_filter_name=new_filter.name
            )
            messages.success(request, f"Filtro '{filter_name}' guardado.")
    
    referer_url = request.META.get('HTTP_REFERER', '/data/').split('?')[0]
    return redirect(f"{referer_url}?{query_params_str}")

def load_filter_view(request, filter_id):
    saved_filter = get_object_or_404(SavedFilter, pk=filter_id)
    params_dict = saved_filter.parameters

    record_count = FilterManager.apply_filters(
        CampaignRecord.objects.all(), params_dict
    ).count()

    QueryHistory.objects.create(
        description=f"Se cargó el filtro: '{saved_filter.name}'",
        records_count=record_count,
        filters_applied=saved_filter.parameters,
        saved_filter_name=saved_filter.name
    )

    # Construir la URL de forma manual y correcta usando urlencode
    # El argumento 'doseq=True' es clave para manejar listas
    query_string = urlencode(saved_filter.parameters, doseq=True)
    return redirect(f"/data/?{query_string}")

@require_POST
def delete_filter_view(request, filter_id):
    saved_filter = get_object_or_404(SavedFilter, pk=filter_id)
    filter_name = saved_filter.name
    saved_filter.delete()
    messages.info(request, f"Filtro '{filter_name}' eliminado.")
    
    # Redirige a la URL desde la que se vino, pero sin la acción de borrado
    referer_url = request.META.get('HTTP_REFERER', '/data/')
    return redirect(referer_url)


def _draw_pdf_table(buffer, title, data, headers):
    """Función auxiliar para dibujar una tabla en un documento PDF."""
    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter))
    elements = []

    # Crear la tabla con los datos
    table_data = [headers] + [[str(item.get(h, '')) for h in headers] for item in data]
    
    table = Table(table_data, repeatRows=1) # Repetir cabeceras en cada página
    
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#495057')), # Encabezado oscuro
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke), # Texto del encabezado
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#343a40')), # Fondo de filas
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.whitesmoke), # Texto de filas
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#6c757d')) # Rejilla
    ])
    table.setStyle(style)
    
    elements.append(table)
    
    def add_header_footer(canvas, doc):
        canvas.saveState()
        canvas.setFont('Helvetica', 9)
        # Título del documento
        canvas.drawString(inch, doc.height + 1.2 * inch, title)
        canvas.drawString(inch, doc.height + 1.0 * inch, f"Generado el: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        # Número de página en el pie
        canvas.drawString(doc.width / 2.0, 0.75 * inch, f"Página {doc.page}")
        canvas.restoreState()

    doc.build(elements, onFirstPage=add_header_footer, onLaterPages=add_header_footer)

def export_data_view(request):
    """Exporta los datos actualmente filtrados a CSV o PDF."""
    export_format = request.GET.get('format', 'csv')
    
    queryset = CampaignRecord.objects.all()
    form = CampaignFilterForm(request.GET)
    if form.is_valid():
        filtered_queryset = FilterManager.apply_filters(queryset, form.cleaned_data)
    else:
        filtered_queryset = queryset
        
    sort_by = request.GET.get('sort_by', 'id')
    # Validar el campo de ordenamiento
    valid_sort_fields = [f.name for f in CampaignRecord._meta.get_fields()]
    if sort_by.strip('-') in valid_sort_fields:
        filtered_queryset = filtered_queryset.order_by(sort_by)

    # Convertimos el QuerySet a una lista de diccionarios
    data = list(filtered_queryset.values())
    
    if not data:
        messages.error(request, "No hay datos para exportar con los filtros seleccionados.")
        return redirect(f"{request.META.get('HTTP_REFERER', '/data/')}")

    if export_format == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="export_data.csv"'
        
        writer = csv.DictWriter(response, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
        return response

    elif export_format == 'pdf':
        buffer = BytesIO()
        headers = list(data[0].keys())
        
        _draw_pdf_table(buffer, "Datos de Campañas - Reporte Filtrado", data, headers)
        
        buffer.seek(0)
        
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="reporte_datos.pdf"'
        return response
    
    return redirect('/data/')