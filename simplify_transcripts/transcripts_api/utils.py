from .models import Record, AgendaItem

### Contains helper functions for REST API
def direct_query(query):
    agenda_items = AgendaItem.objects.filter(summary__icontains=query)
    record_ids = agenda_items.values_list('record_id', flat=True).distinct()
    
    return Record.objects.filter(record_id__in=record_ids)

    