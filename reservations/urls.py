from django.urls import path
from . import views

urlpatterns = [
    path('create-reservation/', views.create_reservation, name='create_reservation'),
]
