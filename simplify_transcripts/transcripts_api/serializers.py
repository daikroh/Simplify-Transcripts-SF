from rest_framework import serializers
from .models import Record, AgendaItem


class RecordSerializer(serializers.ModelSerializer):

    class Meta:
        model = Record
        fields = ["record_id", "view_id", "published_date"]


class AgendaItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = AgendaItem
        fields = [
            "agenda_id",
            "record_id",
            "title",
            "start_time",
            "end_time",
            "summary",
            "transcript",
            "embeddings",
        ]


class RecordCombinedSerializer(serializers.ModelSerializer):
    agenda_items = AgendaItemSerializer(many=True, read_only=True)

    class Meta:
        model = Record
        fields = ["record_id", "view_id", "published_date", "agenda_items"]
