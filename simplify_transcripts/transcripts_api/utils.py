from django.db.models import Q
from .models import Record, AgendaItem
from collections import defaultdict
from rest_framework.response import Response

### Contains helper functions for REST API
def combine_record_agenda(agenda_items):
    agenda_map = defaultdict(list)
    results = []

    for item in agenda_items:
        agenda_map[item.record.record_id].append({
            'title': item.title,
            'summary': item.summary,
            'start_time': item.start_time,
            'end_time': item.end_time
        })

    record_ids = list(agenda_map.keys())
    records = Record.objects.filter(record_id__in=record_ids)

    for record in records:
        results.append({
            'record_id': record.record_id,
            'view_id': record.view_id,
            'published_date': record.published_date,
            'agenda_items': agenda_map[record.record_id]
        })
    
    return results

def direct_query(query):
    # Get agenda items matching the query
    agenda_items = AgendaItem.objects.filter(Q(title__icontains=query) | Q(summary__icontains=query)).select_related('record')
    results = combine_record_agenda(agenda_items)
    return Response(results)

def record_list_of_agenda(record_id):
    # Fetch all agenda items for a given record
    agenda_items = AgendaItem.objects.filter(record_id__in=record_id).order_by('start_time')
    results = combine_record_agenda(agenda_items)
    return Response(results)