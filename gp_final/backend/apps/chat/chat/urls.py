from django.urls import path
from .views import MessageHistoryView

urlpatterns = [
    path('<int:team_id>/messages/', MessageHistoryView.as_view(), name='message-history'),
]
