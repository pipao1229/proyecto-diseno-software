# history/urls.py

from django.urls import path
from . import views

app_name = 'history'

urlpatterns = [
    path('', views.history_view, name='list'),
    path('export/', views.export_history_view, name='export'),
    path('log-event/', views.log_event_view, name='log_event'),
    path('log/clear-filters/', views.log_clear_filters_event, name='log_clear_filters'),
    path('clear/', views.clear_history_view, name='clear_history')
]