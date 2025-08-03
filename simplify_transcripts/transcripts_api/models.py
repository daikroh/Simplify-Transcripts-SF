from django.db import models
from pgvector.django import VectorField


class Record(models.Model):
    record_id = models.IntegerField(primary_key=True)
    view_id = models.IntegerField()
    published_date = models.DateTimeField()

    def __str__(self):
        return self.record_id


class AgendaItem(models.Model):
    agenda_id = models.UUIDField(primary_key=True)
    record = models.ForeignKey(
        Record, on_delete=models.CASCADE, related_name="agenda_items"
    )
    title = models.CharField(max_length=256)
    start_time = models.IntegerField()
    end_time = models.IntegerField()
    summary = models.TextField()
    transcript = models.TextField()

    def __str__(self):
        return self.title
