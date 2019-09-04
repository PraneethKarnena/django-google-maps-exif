from django.shortcuts import render
from django.views.decorators.http import require_http_methods


@require_http_methods(['GET'])
def home_view(request):
    """
    Logic for Home page
    Return a simple Home template
    """
    return render(request, 'service/home.html')
