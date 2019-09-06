# Generated by Django 2.2.5 on 2019-09-06 02:04

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ImageModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(help_text='Upload an Image', upload_to='', verbose_name='Image')),
                ('image_type', models.CharField(choices=[('SRC', 'Source'), ('DST', 'Destination')], max_length=3)),
            ],
        ),
        migrations.CreateModel(
            name='JobModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('PRS', 'Processing'), ('COM', 'Complete'), ('ERR', 'Error')], default='PRS', max_length=3)),
                ('images', models.ManyToManyField(to='service_app.ImageModel')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
