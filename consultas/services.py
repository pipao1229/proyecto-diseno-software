# consultas/services.py
from dashboard.models import CampaignRecord

class FilterManager:
    """
    Clase que encapsula la lógica para aplicar filtros a un QuerySet.
    """
    @staticmethod
    def apply_filters(queryset, params):
        # Hacemos una copia para no modificar el diccionario original
        filters = params.copy()

        # Filtro de Resultado ('y')
        # Buscamos el valor, lo eliminamos del diccionario y lo aplicamos si existe.
        y_value = filters.pop('y', None)
        if y_value:
            # Como puede llegar como lista (['yes']) o string ('yes'), nos aseguramos de tomar el primer elemento
            y_value_str = y_value[0] if isinstance(y_value, list) else y_value
            bool_value = y_value_str.lower() == 'yes'
            queryset = queryset.filter(y=bool_value)

        # Filtro de Edad (numérico)
        age_min = filters.pop('age_min', None)
        if age_min:
             # Similar a 'y', puede venir en una lista
             age_min_val = age_min[0] if isinstance(age_min, list) else age_min
             if str(age_min_val).isdigit(): # Validamos que sea un número
                 queryset = queryset.filter(age__gte=int(age_min_val))

        age_max = filters.pop('age_max', None)
        if age_max:
             age_max_val = age_max[0] if isinstance(age_max, list) else age_max
             if str(age_max_val).isdigit():
                 queryset = queryset.filter(age__lte=int(age_max_val))

        # Filtros de Múltiples Valores (Píldoras)
        # Lo que queda en 'filters' ya no contiene 'y', 'age_min', ni 'age_max'
        for field, values in filters.items():
            if values and field != 'sort_by' and field != 'page':
                lookup = f"{field}__in"
                queryset = queryset.filter(**{lookup: values})
        
        return queryset