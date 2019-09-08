"""
This views.py contains business logic of all the pages.
"""

import os
import threading
from tempfile import TemporaryFile

from PIL import Image
from PIL.ExifTags import TAGS

import googlemaps
import requests

from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.core.files import File

from . import models


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
        jobs = models.JobModel.objects.filter(user=request.user)
        pending_jobs = models.JobModel.objects.filter(status='PRS').count()
        show_timer = False
        if pending_jobs > 0:
            show_timer = True

        return render(request, 'service/dashboard.html', {'jobs': jobs, 'show_timer': show_timer})

    else:
        try:

            # Save the images, job and start processing asynchronously
            job = models.JobModel.objects.create(user=request.user)

            source_image = models.ImageModel.objects.create(
                image=request.FILES['source_image'],
                image_type='SRC',
            )
            job.source_image = source_image

            destination_image = models.ImageModel.objects.create(
                image=request.FILES['destination_image'],
                image_type='DST',
            )
            job.destination_image = destination_image

            # if there are any Waypoints
            waypoint_images = request.FILES.getlist('waypoint_images')
            if waypoint_images:
                for waypoint_image in waypoint_images:
                    _ = job.waypoint_images.create(
                        image=waypoint_image,
                        image_type='WPT',
                    )

            job.save()
            t = threading.Thread(target=job_wrapper, args=[job])
            t.start()

            success_msg = 'Your request has been received. Refresh this page for any updates!'
            messages.add_message(request, messages.SUCCESS, success_msg)
            return HttpResponseRedirect(reverse('service_app:dashboard_page'))

        except Exception as e:
            messages.add_message(request, messages.ERROR, str(e))
            return HttpResponseRedirect(reverse('service_app:dashboard_page'))


def job_wrapper(job):
    try:
        process_images(job)
        calculate_shortest_path(job)
        generate_static_map(job)

    except Exception as e:
        print('error: ', str(e))

        # If any exception occurs, terminate the process
        # write error message to database
        job.status = 'ERR'
        job.errors = f'{job.errors} {str(e)}.'
        job.save()

    finally:
        return



def generate_static_map(job):
    GOOGLE_MAPS_ST_KEY = os.environ.get('GOOGLE_MAPS_ST_KEY')
    GOOGLE_MAPS_ST_BASE_URL = 'https://maps.googleapis.com/maps/api/staticmap'
    MAP_SIZE = '500x400'
    PATH = job.path_coords

    API_URL = f'{GOOGLE_MAPS_ST_BASE_URL}?size={MAP_SIZE}&path={PATH}&key={GOOGLE_MAPS_ST_KEY}'

    path_coords = job.path_coords.split('|')
    for i in range(len(path_coords)):
        API_URL = f'{API_URL}&markers=label:{i}|{path_coords[i]}'

    # static_map = models.ImageModel.objects.create(
    #     image=r.content,
    #     image_type='STA'
    # )
    f = models.ImageModel()
    with TemporaryFile() as tf:
        r = requests.get(API_URL)
        tf.write(r.content)
        tf.seek(0)
        f.image.save(f'{job.id}.png', File(tf))
    f.image_type = 'STA'
    f.save()
    job.static_map = f
    job.status = 'COM'
    job.save()




# calculate the shortest path
def calculate_shortest_path(job):
    source_latitude = job.source_image.latitude
    source_longitude = job.source_image.longitude

    destination_latitude = job.destination_image.latitude
    destination_longitude = job.destination_image.longitude

    waypoints = job.waypoint_images.all()
    wp = []
    if waypoints:
        for waypoint in waypoints:
            wp.append(f'{waypoint.latitude},{waypoint.longitude}')

    GOOGLE_MAPS_DR_KEY = os.environ.get('GOOGLE_MAPS_DR_KEY')
    gmaps = googlemaps.Client(key=GOOGLE_MAPS_DR_KEY)
    directions_result = gmaps.directions(
        f'{source_latitude},{source_longitude}',
        f'{destination_latitude},{destination_longitude}',
        waypoints=wp,
        optimize_waypoints=True,
    )

    path_coords = ''
    for coord in directions_result[0]['legs']:
        lat = coord['start_location']['lat']
        lng = coord['start_location']['lng']
        path_coords = f'{path_coords}|{lat},{lng}'
    lat = directions_result[0]['legs'][len(directions_result[0]['legs'])-1]['end_location']['lat']
    lng = directions_result[0]['legs'][len(directions_result[0]['legs'])-1]['end_location']['lng']
    path_coords = f'{path_coords}|{lat},{lng}'

    job.total_distance = directions_result[0]['legs'][0]['distance']['text']
    job.path_coords = path_coords.replace('|', '', 1)
    job.save()


# calls several other methods
def process_images(job):
    source_image = job.source_image
    latitude, longitude = get_lat_long(source_image.image.name)
    source_image.longitude = longitude
    source_image.latitude = latitude
    place_name = do_reverse_geocoding(latitude, longitude)
    source_image.place_name = place_name
    source_image.save()

    destination_image = job.destination_image
    latitude, longitude = get_lat_long(destination_image.image.name)
    destination_image.longitude = longitude
    destination_image.latitude = latitude
    place_name = do_reverse_geocoding(latitude, longitude)
    destination_image.place_name = place_name
    destination_image.save()

    waypoints = job.waypoint_images.all()
    if waypoints:
        for waypoint in waypoints:
            latitude, longitude = get_lat_long(waypoint.image.name)
            waypoint.latitude = latitude
            waypoint.longitude = longitude
            place_name = do_reverse_geocoding(latitude, longitude)
            waypoint.place_name = place_name
            waypoint.save()


# get place name from coordinates
def do_reverse_geocoding(latitude, longitude):
    GOOGLE_MAPS_RG_KEY = os.environ.get('GOOGLE_MAPS_RG_KEY')
    gmaps = googlemaps.Client(key=GOOGLE_MAPS_RG_KEY)
    reverse_geocode_result = gmaps.reverse_geocode((latitude, longitude))[0]['formatted_address']
    return reverse_geocode_result

# Return latitude and longitude from an image
def get_lat_long(image_path):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
    image_path = f'{MEDIA_ROOT}/{image_path}'
    image = Image.open(image_path)
    exif_data = image._getexif()

    gps_info = {}
    for key, value in exif_data.items():

        if TAGS.get(key) == 'GPSInfo':
            gps_info[TAGS.get(key)] = value
            break

    # normalize GPS info
    normalized_data = normalize_gps_info(gps_info)
    latitude = convert_rational64u(normalized_data['latitude']['dms'], normalized_data['latitude']['ref'])
    longitude = convert_rational64u(normalized_data['longitude']['dms'], normalized_data['longitude']['ref'])

    return latitude, longitude


def normalize_gps_info(gps_info):
    latitude = {'ref': gps_info['GPSInfo'][1], 'dms': gps_info['GPSInfo'][2]}
    longitude = {'ref': gps_info['GPSInfo'][3], 'dms': gps_info['GPSInfo'][4]}

    return {'latitude': latitude, 'longitude': longitude}


# convert rational64u to degrees and minutes
def convert_rational64u(dms, ref):
    degrees = dms[0][0] / dms[0][1]
    minutes = dms[1][0] / dms[1][1] / 60.0
    seconds = dms[2][0] / dms[2][1] / 3600.0

    if ref in ['S', 'W']:
        degrees = -degrees
        minutes = -minutes
        seconds = -seconds

    return round(degrees + minutes + seconds, 5)
