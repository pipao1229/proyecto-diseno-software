# consultas/urls.py

from django.urls import path
from . import views

app_name = 'consultas'

urlpatterns = [
    # La vista principal que renderiza el esqueleto de la página
    path('', views.data_explorer_view, name='data_explorer'),
    
    # --- NUEVA URL PARA LA API ---
    # Esta URL solo devolverá datos en formato JSON
    path('api/filter-data/', views.filter_data_api_view, name='filter_data_api'),
    
    # Las URLs que ya teníamos para guardar/cargar filtros
    path('save-filter/', views.save_filter_view, name='save_filter'),
    path('load-filter/<int:filter_id>/', views.load_filter_view, name='load_filter'),
    path('export/', views.export_data_view, name='export_data'),
]