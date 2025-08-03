from django.shortcuts import render
from .models import Record, AgendaItem
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import RecordSerializer, AgendaItemSerializer
from .utils import *

"""
API endpoints for Records
"""
class RecordCreate(generics.CreateAPIView):
    # API endpoint that allows creation of a new record
    queryset = Record.objects.all()
    serializer_class = RecordSerializer

class RecordList(generics.ListAPIView):
    # API endpoint that allows listing of a record
    queryset = Record.objects.all()
    serializer_class = RecordSerializer

class RecordDetail(APIView):
    def get(self, request):
        record_id = request.query_params.get('record_id')

        if not record_id:
            return Response({'error': 'Missing record_id in query parameters'}, status=status.HTTP_400_BAD_REQUEST)

        queryset = Record.objects.filter(record_id=record_id)

        if not queryset.exists():
            return Response({'error': 'Record not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = RecordSerializer(queryset, many=True)
        return Response(serializer.data)

"""
API endpoints for Agenda
"""
class AgendaItemCreate(generics.CreateAPIView):
    # API endpoint that allows creation of a new agenda item
    queryset = AgendaItem.objects.all()
    serializer_class = AgendaItemSerializer

class AgendaItemList(generics.ListAPIView):
    # API endpoint that allows listing of an agenda item
    queryset = AgendaItem.objects.all()
    serializer_class = AgendaItemSerializer

class AgendaItemDetail(APIView):
    def get(self, request):
        agenda_id = request.query_params.get('agenda_id')

        if not agenda_id:
            return Response({'error': 'Missing agenda_id in query parameters'}, status=status.HTTP_400_BAD_REQUEST)

        queryset = AgendaItem.objects.filter(agenda_id=agenda_id)

        if not queryset.exists():
            return Response({'error': 'Agenda item not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = AgendaItemSerializer(queryset, many=True)
        return Response(serializer.data)

"""
API endpoints for Search
"""
class DirectSearch(APIView):
    def get(self, request):
        query = request.query_params.get('q')

        if not query:
            return Response({'error': 'Missing q in query parameters'}, status=status.HTTP_400_BAD_REQUEST)

        queryset = direct_query(query)
        # agenda_items = AgendaItem.objects.filter(summary__icontains=query)

        serializer = RecordSerializer(queryset, many=True)
        # serializer = AgendaItemSerializer(agenda_items, many=True)
        return Response(serializer.data)