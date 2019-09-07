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

    def __str__(self):
        return f'{str(self.image)} - {self.image_type}'


class JobModel(models.Model):
    """
    Image processing job model
    Process images to extract EXIF data
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    images = models.ManyToManyField(ImageModel, related_name='jobs')

    JOB_STATUS_CHOICES = (
        ('PRS', 'Processing'),
        ('COM', 'Complete'),
        ('ERR', 'Error'),
    )
    status = models.CharField(max_length=3, choices=JOB_STATUS_CHOICES, default='PRS')
    route = models.TextField(null=True, blank=True)
    total_distance = models.FloatField(null=True, blank=True)
    static_map = models.ForeignKey(ImageModel, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f'{str(self.user)} - {self.status}'
