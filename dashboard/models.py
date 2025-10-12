# dashboard/models.py

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class CampaignRecord(models.Model):
    # Campos del cliente
    age = models.IntegerField(
        validators=[MinValueValidator(17), MaxValueValidator(98)],
        help_text="Edad del cliente"
    )
    job = models.CharField(max_length=50, help_text="Ocupación del cliente")
    marital = models.CharField(max_length=20, help_text="Estado civil")
    education = models.CharField(max_length=50, help_text="Nivel educativo")
    default = models.BooleanField(help_text="¿Crédito en demora?")
    balance = models.IntegerField(help_text="Balance promedio anual en euros")
    housing = models.BooleanField(help_text="¿Tiene préstamo hipotecario?")
    loan = models.BooleanField(help_text="¿Tiene préstamo personal?")

    # Campos de la campaña
    contact = models.CharField(max_length=20, help_text="Tipo de contacto")
    day = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(31)],
        help_text="Día del último contacto"
    )
    month = models.CharField(max_length=10, help_text="Mes del último contacto")
    duration = models.IntegerField(
        validators=[MinValueValidator(0)],
        help_text="Duración del último contacto en segundos"
    )
    campaign = models.IntegerField(
        validators=[MinValueValidator(1)],
        help_text="Número de contactos en esta campaña"
    )
    pdays = models.IntegerField(
        help_text="Días desde el último contacto previo (-1 si no fue contactado)"
    )
    previous = models.IntegerField(
        validators=[MinValueValidator(0)],
        help_text="Número de contactos previos a esta campaña"
    )
    poutcome = models.CharField(max_length=20, help_text="Resultado de la campaña previa")
    y = models.BooleanField(help_text="¿El cliente suscribió un depósito a plazo?")

    class Meta:
        verbose_name = "Registro de Campaña"
        verbose_name_plural = "Registros de Campañas"

    def __str__(self):
        return f"Cliente ID {self.id} - Edad: {self.age}, Ocupación: {self.job}"