# dashboard/views.py

import io
from datetime import datetime
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db import connection
from django.contrib import messages

# Importaciones para la generación de PDF
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch

from .forms import DatasetUploadForm
from .models import CampaignRecord
from .services.csv_importer import CsvDataImporter
from history.models import QueryHistory


def upload_dataset_view(request):
    if 'upload_errors' in request.session:
        del request.session['upload_errors']
    if 'error_report_filename' in request.session:
        del request.session['error_report_filename']

    context = {'form': DatasetUploadForm()}
    
    if request.method == 'POST':
        form = DatasetUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['file']
            
            importer = CsvDataImporter(uploaded_file)
            importer.process_file()
            valid_records, errors = importer.get_results()

            success = False

            if valid_records and not errors:
                try:
                    with connection.cursor() as cursor:
                        table_name_campaign = CampaignRecord._meta.db_table
                        table_name_history = QueryHistory._meta.db_table
                        cursor.execute(f'TRUNCATE TABLE "{table_name_campaign}" RESTART IDENTITY CASCADE;')
                        cursor.execute(f'TRUNCATE TABLE "{table_name_history}" RESTART IDENTITY CASCADE;')

                    CampaignRecord.objects.bulk_create(valid_records, batch_size=1000)
                    
                    context['success_message'] = f"¡Éxito! Se cargaron y validaron {len(valid_records)} registros. Los datos y el historial anterior han sido reiniciados."
                    success = True # Solo se convierte en True si todo sale bien
                except Exception as e:
                    errors.append(f"Error crítico al interactuar con la base de datos: {str(e)}")
            
            if errors:
                request.session['upload_errors'] = errors
                request.session['error_report_filename'] = uploaded_file.name

            context['errors'] = errors
            context['records_loaded'] = len(valid_records) if success else 0
            
            if not success and valid_records:
                 context['records_with_errors'] = len(errors) + len(valid_records)
            else:
                 context['records_with_errors'] = len(errors)

            return render(request, 'dashboard/upload_result.html', context)
    
    return render(request, 'dashboard/upload_dataset.html', context)


def generate_error_report_pdf_view(request):
    """
    Genera un reporte en PDF con los errores de validación
    almacenados en la sesión.
    """
    errors = request.session.get('upload_errors', [])
    filename = request.session.get('error_report_filename', 'archivo_desconocido')

    if not errors:
        messages.error(request, 'No hay errores para generar un reporte.')
        return redirect('dashboard:upload_dataset')

    # Crea un buffer en memoria para el archivo PDF
    buffer = io.BytesIO()

    # Crea el objeto PDF, usando el buffer como su "archivo".
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # --- Estructura del PDF ---
    p.setFont("Helvetica-Bold", 16)
    p.drawCentredString(width / 2.0, height - 1 * inch, "Reporte de Errores de Validación")

    p.setFont("Helvetica", 11)
    p.drawString(0.75 * inch, height - 1.5 * inch, f"Archivo: {filename}")
    p.drawString(0.75 * inch, height - 1.7 * inch, f"Fecha de Generación: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

    p.setFont("Helvetica-Bold", 12)
    p.drawString(0.75 * inch, height - 2.2 * inch, "Resumen:")
    
    p.setFont("Helvetica", 11)
    p.drawString(1 * inch, height - 2.4 * inch, f"Total de filas con errores encontradas: {len(errors)}")

    # Preparamos para escribir la lista de errores
    text = p.beginText()
    text.setTextOrigin(0.75 * inch, height - 3 * inch)
    text.setFont("Courier", 9)
    
    # Escribimos los detalles de los errores
    text.textLine("--- Log de Errores Detallado ---")
    text.textLine("") # Espacio

    for error in errors:
        # Control simple de paginación
        if text.getY() < 1 * inch:
            p.drawText(text)
            p.showPage() # Finaliza la página actual
            text = p.beginText()
            text.setTextOrigin(0.75 * inch, height - 1 * inch)
            text.setFont("Courier", 9)

        text.textLine(f"- {error}")
    
    p.drawText(text)

    # Cierra el objeto PDF y lo guarda
    p.showPage()
    p.save()

    # Regresa el cursor del buffer al inicio para poder leerlo
    buffer.seek(0)
    
    # Crea la respuesta HTTP con el tipo de contenido para PDF
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reporte_de_errores.pdf"'

    return response