from django.urls import path

from . import views

urlpatterns = [
    path('', views.defense_api, name='defense_api'),
    path('create/', views.create_defense_api, name='create_defense_api'),
]
