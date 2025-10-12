# dashboard/urls.py

from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.upload_dataset_view, name='upload_dataset'),
    path('generate-error-report/', views.generate_error_report_pdf_view, name='generate_error_report'),
]