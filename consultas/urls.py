# consultas/urls.py

from django.urls import path
from . import views

app_name = 'consultas'

urlpatterns = [
    path('', views.data_explorer_view, name='data_explorer'),
    path('api/filter-data/', views.filter_data_api_view, name='filter_data_api'),
    path('save-filter/', views.save_filter_view, name='save_filter'),
    path('load-filter/<int:filter_id>/', views.load_filter_view, name='load_filter'),
    path('delete-filter/<int:filter_id>/', views.delete_filter_view, name='delete_filter'),
    path('export/', views.export_data_view, name='export_data'),
]