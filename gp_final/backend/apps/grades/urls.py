from django.urls import path

from . import views

urlpatterns = [
    path('', views.grades_api, name='grades_api'),
    path('create/', views.create_grade_api, name='create_grade_api'),
    path('<int:grade_id>/', views.grade_detail_api, name='grade_detail_api'),
    path('<int:grade_id>/approve/', views.approve_grade_api, name='approve_grade_api'),
    path('<int:grade_id>/reject/', views.reject_grade_api, name='reject_grade_api'),
]
