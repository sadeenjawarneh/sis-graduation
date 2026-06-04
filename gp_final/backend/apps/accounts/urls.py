from django.urls import path
from . import views

urlpatterns = [
    path('register/',        views.register,        name='auth-register'),
    path('login/',           views.login,           name='auth-login'),
    path('logout/',          views.logout,          name='auth-logout'),
    path('profile/',         views.profile,         name='auth-profile'),
    path('change-password/', views.change_password, name='auth-change-password'),
    path('supervisors/',          views.supervisor_list,   name='auth-supervisors'),
    path('supervisors/<int:pk>/', views.supervisor_detail, name='auth-supervisor-detail'),
    path('students/',             views.student_list,      name='auth-students'),
]
