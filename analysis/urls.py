# analysis/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.upload_and_analyze, name='upload_and_analyze'),
    path('datasets/', views.dataset_list, name='dataset_list'),              # List all datasets
    path('datasets/<slug:data_slug>/', views.dataset_detail, name='dataset_detail'),
]
