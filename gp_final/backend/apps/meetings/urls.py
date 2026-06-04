from django.urls import path
from . import views

urlpatterns = [
    path('',             views.meeting_list,    name='meeting-list'),
    path('book/',        views.book_meeting,    name='meeting-book'),
    path('slots/',       views.availability_slots, name='slot-list-create'),
    path('slots/<int:pk>/', views.delete_slot,  name='slot-delete'),
]
