from django.urls import path
from . import views

urlpatterns = [
    path('',                     views.notification_list, name='notif-list'),
    path('unread-count/',        views.unread_count,      name='notif-unread-count'),
    path('mark-all-read/',       views.mark_all_read,     name='notif-mark-all-read'),
    path('<int:pk>/read/',       views.mark_one_read,     name='notif-mark-one-read'),
    path('<int:pk>/delete/',     views.delete_notification, name='notif-delete'),
]
