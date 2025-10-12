# consultas/forms.py

from django import forms

class CampaignFilterForm(forms.Form):
    # Definimos los campos que se usarán para filtrar. `required=False` es clave.
    age_min = forms.IntegerField(label="Edad Mínima", required=False, min_value=17)
    age_max = forms.IntegerField(label="Edad Máxima", required=False, max_value=98)

    JOB_CHOICES = [
        ("admin.","Admin"), ("blue-collar","Blue-Collar"), ("entrepreneur","Entrepreneur"),
        ("housemaid","Housemaid"), ("management","Management"), ("retired","Retired"),
        ("self-employed","Self-Employed"), ("services","Services"), ("student","Student"),
        ("technician","Technician"), ("unemployed","Unemployed"), ("unknown","Unknown")
    ]
    job = forms.MultipleChoiceField(label="Ocupación", choices=JOB_CHOICES, required=False, widget=forms.SelectMultiple(attrs={'class': 'form-control', 'size': '5'}))
    
    MARITAL_CHOICES = [("married","Married"), ("divorced","Divorced"), ("single", "Single"), ("unknown","Unknown")]
    marital = forms.MultipleChoiceField(label="Estado Civil", choices=MARITAL_CHOICES, required=False)

    EDUCATION_CHOICES = [("primary","Primary"), ("secondary","Secondary"), ("tertiary", "Tertiary"), ("unknown","Unknown")]
    education = forms.MultipleChoiceField(label="Educación", choices=EDUCATION_CHOICES, required=False)
    
    # También añadimos un campo oculto para mantener el estado de ordenamiento
    sort_by = forms.CharField(widget=forms.HiddenInput(), required=False)