from django.urls import path
from django.contrib.auth.views import LogoutView

from . import views

urlpatterns = [
    path('', views.home_view, name='home_page'), # route for Home page
    path('register/', views.registration_view, name='registration_page'), # route for Registration page
    path('login/', views.login_view, name='login_page'), # route for Login page
    path('dashboard/', views.dashboard_view, name='dashboard_page'),
    path('logout/', LogoutView.as_view(), name='logout_page'),
]
