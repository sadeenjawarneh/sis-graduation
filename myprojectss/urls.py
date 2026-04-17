# myprojectss/urls.py
from django.contrib import admin
from django.urls import path
from main import views 

urlpatterns = [
    path('admin/', admin.site.urls),
    
    path("", views.index, name="index"), 
    path("student_dashboard/", views.student_dashboard, name="student_dashboard"),
    
    # السطر اللي ناقصك هو هاد:
    path("team/<int:team_id>/", views.team_page, name="team_page"), 
    
    path("create-team/", views.create_team, name="create_team"),
    path('join-team/', views.join_team, name='join_team'), # تأكد هل هو مفرد أم جمع؟
    path("send-join-request/<int:team_id>/", views.send_join_request, name="send_join_request"),
   # path("vote-member/<int:membership_id>/", views.vote_member, name="vote_member"),
    path("leave-team/", views.leave_team, name="leave_team"),
    
    # ورابط المشرفين اللي طلبتيه سابقاً:
     path("supervisors_list/", views.supervisors_list, name="request_supervisor"),
     path('handle-request/<int:membership_id>/<str:action>/', views.handle_membership_request, name='handle_membership_request'),
     path('send_message/<int:team_id>/', views.send_message, name='send_message'),
     path('get_messages/<int:team_id>/', views.get_messages, name='get_messages'),
     path('logout/', views.logout_user, name='logout_user'),
     path('cancel-request/<int:team_id>/', views.cancel_join_request, name='cancel_join_request'),
] 