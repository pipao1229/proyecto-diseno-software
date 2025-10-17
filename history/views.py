# history/views.py

from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
import json
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.utils.dateparse import parse_datetime
from django.db.models import Avg
import csv
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db import models
from .models import QueryHistory
from consultas.models import SavedFilter

def history_view(request):
    """
    Muestra el historial completo de consultas y estadísticas de uso.
    """
    history_log = QueryHistory.objects.all()
    
    # Calcular Estadísticas de Uso 
    total_queries = QueryHistory.objects.count()
    saved_filters_count = SavedFilter.objects.count()
    avg_records_per_query = QueryHistory.objects.aggregate(avg=models.Avg('records_count'))['avg'] or 0
    
    # Tomamos la consulta más reciente del historial
    recent_query = QueryHistory.objects.first()

    context = {
        'history_log': history_log,
        'total_queries': total_queries,
        'saved_filters_count': saved_filters_count,
        'avg_records_per_query': int(avg_records_per_query),
        'recent_query': recent_query,
    }
    return render(request, 'history/history_list.html', context)

def export_history_view(request):
    """
    Exporta el historial de consultas a un archivo CSV.
    """
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="historial_consultas.csv"'

    writer = csv.writer(response)
    # Encabezados mejorados
    writer.writerow(['Fecha', 'Hora', 'Descripción', 'Registros', 'Filtros Aplicados'])

    # Dar formato a la fecha/hora en la vista para una mejor presentación
    history_log = QueryHistory.objects.all().order_by('-timestamp')
    for record in history_log:
        writer.writerow([
            record.timestamp.strftime('%Y-%m-%d'),
            record.timestamp.strftime('%H:%M:%S'),
            record.description,
            record.records_count,
            record.filters_applied or 'N/A'
        ])

    return response

@csrf_exempt
@require_POST
def log_event_view(request):
    try:
        data = json.loads(request.body)
        description = data.get('description', 'Evento sin descripción')

        if description == "Filtros limpiados":
            QueryHistory.objects.create(
                description="Filtros limpiados",
                # No pasamos records_count ni filtros, ya que es una acción de reseteo
                records_count=0, 
                filters_applied=None
            )
        # En el futuro se pueden añadir más tipos de eventos aquí
        
        return JsonResponse({'status': 'ok'})
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@require_POST
def log_clear_filters_event(request):
    try:
        data = json.loads(request.body)
        QueryHistory.objects.create(
            description="Filtros limpiados",
            records_count=data.get('record_count', 0),
            filters_applied=data.get('filters_applied', {})
        )
        return JsonResponse({'status': 'ok'})
    except Exception:
        return JsonResponse({'status': 'error'}, status=400)
    
@require_POST
def clear_history_view(request):
    QueryHistory.objects.all().delete()
    messages.success(request, "El historial de consultas ha sido limpiado.")
    return redirect('history:list')