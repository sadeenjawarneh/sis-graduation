from django.urls import path
from . import views

urlpatterns = [
    # Availability slots
    path('slots/',            views.availability_slots, name='sv-slots'),
    path('slots/<int:pk>/',   views.delete_slot,        name='sv-slot-delete'),

    # Meetings
    path('meetings/',         views.meeting_list,  name='sv-meetings'),
    path('meetings/book/',    views.book_meeting,  name='sv-book-meeting'),

    # Supervision requests
    path('requests/',                     views.supervision_requests, name='sv-requests'),
    path('requests/<int:pk>/decide/',     views.decide_request,       name='sv-decide-request'),

    # Grading reports
    path('grading/',          views.grading_reports,  name='sv-grading'),
    path('grading/preview/',  views.grading_preview,  name='sv-grading-preview'),

    # Files
    path('files/',            views.file_list,   name='sv-files'),
    path('files/<int:pk>/',   views.delete_file, name='sv-file-delete'),

    # Notifications
    path('notifications/',                       views.notifications,          name='sv-notifications'),
    path('notifications/unread-count/',          views.notif_unread_count,     name='sv-notif-unread-count'),
    path('notifications/mark-all-read/',         views.notif_mark_all_read,    name='sv-notif-mark-all-read'),
    path('notifications/<int:pk>/read/',         views.mark_notification_read, name='sv-notif-read'),
    path('notifications/<int:pk>/',              views.delete_notification,    name='sv-notif-delete'),
]
