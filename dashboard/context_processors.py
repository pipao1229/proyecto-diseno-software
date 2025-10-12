# dashboard/context_processors.py

from .models import CampaignRecord

def global_context(request):
    """
    Agrega datos globales al contexto de todas las plantillas.
    """
    return {
        'total_records_count': CampaignRecord.objects.count(),
    }