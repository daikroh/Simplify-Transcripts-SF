from django.urls import include, path
from .views import *


urlpatterns = [
    path('record-create/', RecordCreate.as_view()),
    path('records/', RecordList.as_view()),
    path('record/', RecordDetail.as_view()),
    path('record-update/', RecordUpdate.as_view()),
    path('record-delete/', RecordDelete.as_view()),
    path('agenda-item-create/', AgendaItemCreate.as_view()),
    path('agenda-items/', AgendaItemList.as_view()),
    path('agenda-item/', AgendaItemDetail.as_view()),
    path('agenda-item-update/', AgendaItemUpdate.as_view()),
    path('agenda-item-delete/', AgendaItemDelete.as_view())
]