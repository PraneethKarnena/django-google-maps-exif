from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home_page'), # route for Home page
    path('register/', views.registration_view, name='registration_page'), # route for Registration page
]
