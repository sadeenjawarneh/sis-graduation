from django.urls import path
from . import views

urlpatterns = [
    path('',                 views.list_files,  name='file-list'),
    path('<int:pk>/delete/', views.delete_file, name='file-delete'),
]
