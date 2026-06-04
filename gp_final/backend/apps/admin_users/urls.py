from django.urls import path

from . import views

urlpatterns = [
    path('', views.students_api, name='students_api'),
    path('create/', views.create_student_api, name='create_student_api'),
    path('<int:student_id>/', views.student_detail_api, name='student_detail_api'),
]
