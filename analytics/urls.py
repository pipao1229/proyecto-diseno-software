# analytics/urls.py

from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    # Vista que renderiza el esqueleto de la página de analytics
    path('', views.analytics_dashboard_view, name='dashboard'),
    
    # Endpoint de API que devolverá todos los datos de los KPIs y gráficos
    path('api/kpi-data/', views.kpi_data_api_view, name='kpi_data_api'),
]