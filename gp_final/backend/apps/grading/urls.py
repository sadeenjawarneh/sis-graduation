from django.urls import path
from . import views

urlpatterns = [
    path('',          views.list_reports,  name='grading-list'),
    path('create/',   views.create_report, name='grading-create'),
    path('preview/',  views.grade_preview, name='grading-preview'),
]
