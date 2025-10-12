# campaign_analyzer/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('dashboard.urls')),      # La página principal será para cargar datos
    path('data/', include('consultas.urls')), # El explorador de datos estará en /data/
]

# Servir archivos de medios solo en modo de desarrollo (DEBUG=True)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)