# dashboard/services/csv_importer.py

import pandas as pd
from django.core.exceptions import ValidationError
from .base_importer import BaseDataImporter
from dashboard.models import CampaignRecord

class CsvDataImporter(BaseDataImporter):
    """
    Fábrica concreta para procesar archivos CSV.
    Ahora configurada para usar punto y coma (;) como separador.
    """
    REQUIRED_COLUMNS = [
        'age', 'job', 'marital', 'education', 'default', 'balance', 'housing', 'loan', 
        'contact', 'day', 'month', 'duration', 'campaign', 'pdays', 'previous', 'poutcome', 'y'
    ]

    def process_file(self):
        try:
            # ¡LA SOLUCIÓN! Le decimos a Pandas que el separador es un punto y coma.
            df = pd.read_csv(self.file, sep=';') 
        except Exception as e:
            self.errors.append(f"Error de formato de archivo. No se pudo leer el CSV: {str(e)}")
            return
        
        missing_cols = [col for col in self.REQUIRED_COLUMNS if col not in df.columns]
        if missing_cols:
            self.errors.append(f"Faltan las siguientes columnas obligatorias: {', '.join(missing_cols)}")
            return

        for index, row in df.iterrows():
            try:
                record = self._create_record_from_row(row)
                self.valid_records.append(record)
            except ValidationError as e:
                self.errors.append(f"Fila {index + 2}: {', '.join(e.messages)}")
    
    def _create_record_from_row(self, row):
        """
        Este es el "Factory Method" en acción. Valida los datos de una fila
        y, si son correctos, crea una instancia de CampaignRecord.
        """
        errors = {}

        def to_bool(value, field_name):
            val_str = str(value).strip().lower()
            if val_str == 'yes': return True
            if val_str == 'no': return False
            errors[field_name] = f"El valor '{value}' es inválido, debe ser 'yes' o 'no'."
            return None

        # Listas de validación actualizadas para coincidir con tu diccionario de datos
        job_choices = ["admin.","blue-collar","entrepreneur","housemaid","management","retired","self-employed","services","student","technician","unemployed","unknown"]
        marital_choices = ["married","divorced","single", "unknown"]
        education_choices = ["primary","secondary","tertiary", "unknown"]
        contact_choices = ["unknown","telephone","cellular"]
        poutcome_choices = ["failure","other","success","unknown"]
        month_choices = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]

        # Validaciones campo por campo
        try:
            age = int(row['age'])
            if not (17 <= age <= 98): errors['age'] = f"La edad ({age}) debe estar entre 17 y 98."
        except (ValueError, TypeError): errors['age'] = "La edad debe ser un número entero."
        
        job = str(row['job']).lower()
        if job not in job_choices: errors['job'] = f"'{row['job']}' no es una ocupación válida."

        marital = str(row['marital']).lower()
        if marital not in marital_choices: errors['marital'] = f"'{row['marital']}' no es un estado civil válido."
        
        education = str(row['education']).lower()
        if education not in education_choices: errors['education'] = f"'{row['education']}' no es un nivel de educación válido."

        try: balance = int(row['balance'])
        except (ValueError, TypeError): errors['balance'] = "El balance debe ser un número entero."

        contact = str(row['contact']).lower()
        if contact not in contact_choices: errors['contact'] = f"'{row['contact']}' no es un tipo de contacto válido."

        try:
            day = int(row['day'])
            if not (1 <= day <= 31): errors['day'] = "El día debe estar entre 1 y 31."
        except (ValueError, TypeError): errors['day'] = "El día debe ser un número entero."
        
        month = str(row['month']).lower()
        if month not in month_choices: errors['month'] = f"'{row['month']}' no es un mes válido."
        
        try:
            duration = int(row['duration'])
            if not (0 <= duration <= 5000): errors['duration'] = "La duración debe estar entre 0 y 5000."
        except (ValueError, TypeError): errors['duration'] = "La duración debe ser un número entero."
        
        try:
            campaign = int(row['campaign'])
            if not (1 <= campaign <= 99): errors['campaign'] = "El número de campaña debe ser entre 1 y 99."
        except (ValueError, TypeError): errors['campaign'] = "Campaña debe ser un número entero."
        
        try:
            pdays = int(row['pdays'])
            if not (-1 <= pdays <= 999): errors['pdays'] = "Pdays debe ser un número entero entre -1 y 999."
        except (ValueError, TypeError): errors['pdays'] = "Pdays debe ser un número entero."
        
        try:
            previous = int(row['previous'])
            if not (0 <= previous <= 300): errors['previous'] = "Previous debe ser un número entero entre 0 y 300."
        except (ValueError, TypeError): errors['previous'] = "Previous debe ser un número entero."
        
        poutcome = str(row['poutcome']).lower()
        if poutcome not in poutcome_choices: errors['poutcome'] = f"'{row['poutcome']}' no es un resultado válido."
        
        # Campos booleanos
        default_val = to_bool(row.get('default'), 'default')
        housing_val = to_bool(row.get('housing'), 'housing')
        loan_val = to_bool(row.get('loan'), 'loan')
        y_val = to_bool(row.get('y'), 'y')

        if errors:
            raise ValidationError([f"{field}: {msg}" for field, msg in errors.items()])
            
        return CampaignRecord(
            age=int(age), job=job, marital=marital, education=education, 
            default=default_val, balance=int(balance), housing=housing_val, loan=loan_val, contact=contact, day=int(day), 
            month=month, duration=int(duration), campaign=int(campaign), pdays=int(pdays), 
            previous=int(previous), poutcome=poutcome, y=y_val
        )