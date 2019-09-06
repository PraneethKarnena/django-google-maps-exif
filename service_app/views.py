"""
This views.py contains business logic of all the pages.
"""

from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required


@require_http_methods(['GET'])
def home_view(request):
    """
    Return a simple Home template
    """
    return render(request, 'service/home.html')


@require_http_methods(['GET', 'POST'])
def registration_view(request):
    # If the user is already logged in, redirect to Dashboard
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('service_app:dashboard_page'))

    if request.method == 'GET':
        # GET request: render a sign up form
        return render(request, 'service/registration.html')

    else:
        # POST request: analyze fields and post-process accordingly
        try:
            email = request.POST['email']
            password = request.POST['password']
            confirm_password = request.POST['confirm_password']

            # Raise exception if passwords do not match
            if password != confirm_password:
                raise Exception('Passwords do not match!')

            # Check if the User already exists in the database
            # Redirect to Login and display relevant message
            user, created = User.objects.get_or_create(username=email, email=email)
            if created:
                user.set_password(password)
                user.save()
                messages.add_message(request, messages.SUCCESS, 'Success! Please login.')
            else:
                messages.add_message(request, messages.ERROR, 'User exists! Please login.')

            return HttpResponseRedirect(reverse('service_app:login_page'))


        except Exception as e:
            messages.add_message(request, messages.ERROR, str(e))
            return HttpResponseRedirect(reverse('service_app:registration_page'))


@require_http_methods(['GET', 'POST'])
def login_view(request):
    # If the user is already logged in, redirect to Dashboard
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('service_app:dashboard_page'))

    # GET request: render a Login form
    if request.method == 'GET':
        return render(request, 'service/login.html')

    else:
        # POST request: analyze fields and post-process accordingly
        try:
            email = request.POST['email']
            password = request.POST['password']

            # Try to authenticate the User
            user = authenticate(username=email, password=password)
            # User exists! Login the user and redirect to dashboard
            if user is not None:
                login(request, user)
                return HttpResponseRedirect(reverse('service_app:dashboard_page'))

            else:
                raise Exception('Invalid credentials or such user!')

        except Exception as e:
            messages.add_message(request, messages.ERROR, str(e))
            return HttpResponseRedirect(reverse('service_app:login_page'))


@require_http_methods(['GET', 'POST'])
@login_required
def dashboard_view(request):
    if request.method == 'GET':
        return render(request, 'service/dashboard.html')

    else:
        try:
            pass
        except Exception as e:
            messages.add_message(request, messages.ERROR, str(e))
            return HttpResponseRedirect(reverse('service_app:dashboard_page'))
