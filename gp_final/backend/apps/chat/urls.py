from django.urls import path
from .views import MessageHistoryView, upload_chat_file

urlpatterns = [
    path('<int:team_id>/messages/', MessageHistoryView.as_view()),
    path('<int:team_id>/upload/', upload_chat_file),
    path('<int:team_id>/upload-voice/', upload_chat_file),
    path('<int:team_id>/upload-file/', upload_chat_file),
]