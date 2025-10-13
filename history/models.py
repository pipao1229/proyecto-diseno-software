# history/models.py

from django.db import models
from consultas.models import SavedFilter # Podemos enlazar a filtros si se desea en el futuro

class QueryHistory(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Fecha y Hora")
    description = models.CharField(max_length=255, verbose_name="Descripción")
    records_count = models.IntegerField(verbose_name="Registros Afectados")
    filters_applied = models.JSONField(null=True, blank=True, verbose_name="Filtros Aplicados (JSON)")
    
    # Este campo no es un ForeignKey real, solo almacena el nombre por simplicidad en Fase 1.
    saved_filter_name = models.CharField(max_length=100, null=True, blank=True, verbose_name="Nombre del Filtro Guardado")
    
    class Meta:
        verbose_name = "Historial de Consulta"
        verbose_name_plural = "Historial de Consultas"
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.description} a las {self.timestamp.strftime('%Y-%m-%d %H:%M')}"