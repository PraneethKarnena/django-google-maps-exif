from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.models import User


@require_http_methods(['GET'])
def home_view(request):
    """
    Return a simple Home template
    """
    return render(request, 'service/home.html')


@require_http_methods(['GET', 'POST'])
def registration_view(request):
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
