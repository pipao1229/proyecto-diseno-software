# dashboard/forms.py

from django import forms

class DatasetUploadForm(forms.Form):
    file = forms.FileField(
        label='Selecciona un archivo CSV o Excel',
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.csv, .xlsx, .xls'})
    )