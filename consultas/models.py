# consultas/models.py

from django.db import models
from django.contrib.auth.models import User # Importamos el modelo de usuario por defecto de Django

class SavedFilter(models.Model):
    # En el futuro, cada filtro pertenecerá a un usuario.
    # user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    name = models.CharField(max_length=100, help_text="Nombre descriptivo para el conjunto de filtros")
    parameters = models.JSONField(help_text="Parámetros del filtro guardados como un objeto JSON")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Filtro Guardado"
        verbose_name_plural = "Filtros Guardados"
        ordering = ['-created_at']

    def __str__(self):
        return self.name