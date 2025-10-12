# consultas/services.py

class FilterManager:
    """
    Clase que encapsula la lógica para aplicar filtros a un QuerySet.
    Este es nuestro "GestorFiltros".
    """
    @staticmethod
    def apply_filters(queryset, params):
        """
        Aplica una serie de filtros al queryset base.
        :param queryset: El QuerySet inicial (ej. CampaignRecord.objects.all()).
        :param params: Un diccionario con los parámetros de filtro limpios (de un form).
        """
        filters = params.copy()

        # Filtrar por rango de edad
        age_min = filters.pop('age_min', None)
        if age_min is not None:
            queryset = queryset.filter(age__gte=age_min)

        age_max = filters.pop('age_max', None)
        if age_max is not None:
            queryset = queryset.filter(age__lte=age_max)

        # Filtrar por campos de opción múltiple (como 'job', 'marital', etc.)
        for field, values in filters.items():
            # Nos aseguramos de que haya valores seleccionados en los campos de opción múltiple
            if values and field != 'sort_by': # ignoramos el campo de ordenamiento
                lookup = f"{field}__in"
                queryset = queryset.filter(**{lookup: values})
        
        return queryset