from django.urls import path

from . import views

urlpatterns = [
    path('', views.proposals_api, name='proposals_api'),
    path('create/', views.create_proposal_api, name='create_proposal_api'),
    path('<int:proposal_id>/', views.proposal_detail_api, name='proposal_detail_api'),
    path('<int:proposal_id>/approve/', views.approve_proposal_api, name='approve_proposal_api'),
    path('<int:proposal_id>/reject/', views.reject_proposal_api, name='reject_proposal_api'),
]
