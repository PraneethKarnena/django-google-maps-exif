from django.db import models
from django.contrib.auth.models import User


class ImageModel(models.Model):
    """
    Stores Images, and their EXIF data
    """
    image = models.ImageField(verbose_name='Image', help_text='Upload an Image')

    IMAGE_TYPE_CHOICES = (
        ('SRC', 'Source'),
        ('DST', 'Destination'),
        ('WPT', 'Waypoint'),
    )
    image_type = models.CharField(max_length=3, choices=IMAGE_TYPE_CHOICES, null=False, blank=False)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    place_name = models.TextField(null=True, blank=True, default='YET_TO_RETRIEVE')

    def __str__(self):
        return self.place_name


class JobModel(models.Model):
    """
    Image processing job model
    Process images to extract EXIF data
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    source_image = models.ForeignKey(ImageModel, null=True, blank=True, on_delete=models.CASCADE, \
        related_name='job_source_image')
    destination_image = models.ForeignKey(ImageModel, null=True, blank=True, on_delete=models.CASCADE, \
        related_name='job_destination_image')
    waypoint_images = models.ManyToManyField(ImageModel, related_name='job_waypoint_images')

    route_gps_coords = models.TextField(null=True, blank=True)
    total_distance = models.FloatField(null=True, blank=True)
    static_map = models.ForeignKey(ImageModel, on_delete=models.CASCADE, null=True, blank=True, \
        related_name='job_static_map')

    JOB_STATUS_CHOICES = (
        ('PRS', 'Processing'),
        ('COM', 'Complete'),
        ('ERR', 'Error'),
    )
    status = models.CharField(max_length=3, choices=JOB_STATUS_CHOICES, default='PRS')
    errors = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.user.username
