from django.urls import path
from . import views

urlpatterns = [
    path('',               views.list_requests,  name='request-list'),
    path('create/',        views.create_request, name='request-create'),
    path('<int:pk>/decide/', views.decide_request, name='request-decide'),
]
