from django.contrib.postgres.search import TrigramSimilarity
from django.db.models import Q
from django.db.models.expressions import RawSQL
from .models import Record, AgendaItem
from .preprocessing import get_embedding, update_embeddings
from collections import defaultdict
from rest_framework.response import Response


### Contains helper functions for REST API
def combine_record_agenda(agenda_items):
    agenda_map = defaultdict(list)
    results = []

    for item in agenda_items:
        agenda_map[item.record.record_id].append(
            {
                "title": item.title,
                "start_time": item.start_time,
                "end_time": item.end_time,
                "summary": item.summary,
                "transcript": item.transcript,
            }
        )

    record_ids = list(agenda_map.keys())
    records = Record.objects.filter(record_id__in=record_ids)

    for record in records:
        results.append(
            {
                "record_id": record.record_id,
                "view_id": record.view_id,
                "published_date": record.published_date,
                "agenda_items": agenda_map[record.record_id],
            }
        )

    return results


def flatten_agenda_items_with_record_info(agenda_items):
    """
    Convert agenda items to flat structure with record info included
    """
    results = []
    
    for item in agenda_items:
        results.append({
            "agenda_id": str(item.agenda_id),
            "record_id": item.record.record_id,
            "title": item.title,
            "start_time": item.start_time,
            "end_time": item.end_time,
            "summary": item.summary,
            "transcript": item.transcript,
            "view_id": item.record.view_id,
            "published_date": item.record.published_date,
        })
    
    return results


def search(query):
    # update_embeddings()
    
    # Partial match with summary
    agenda_items = (
        AgendaItem.objects.select_related('record')
        .annotate(similarity=TrigramSimilarity("summary", query))
        .filter(similarity__gt=0.03)  # Similarity threshold
        .order_by("-similarity")    
    )

    if not agenda_items.exists():
        # Partial match with title
        agenda_items = (
            AgendaItem.objects.select_related('record')
            .annotate(similarity=TrigramSimilarity("title", query))
            .filter(similarity__gt=0.03)  # Similarity threshold
            .order_by("-similarity")
        )
        
    if not agenda_items.exists():
        query_embedding = get_embedding(query)

        agenda_items = AgendaItem.objects.select_related('record').annotate(
            similarity=RawSQL("embeddings <#> %s", (query_embedding,))
        ).order_by("-similarity")[:5]

    if not agenda_items.exists():
        agenda_items = AgendaItem.objects.select_related('record').filter(
            Q(title__icontains=query) | Q(summary__icontains=query)
        )

    # Return flat structure instead of nested
    results = flatten_agenda_items_with_record_info(agenda_items)
    return Response(results)


def record_list_of_agenda(record_id):
    # Fetch all agenda items for a given record
    agenda_items = AgendaItem.objects.filter(record_id__in=record_id).order_by(
        "start_time"
    )
    results = combine_record_agenda(agenda_items)
    return Response(results)