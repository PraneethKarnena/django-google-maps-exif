# Generated by Django 2.2.5 on 2019-09-06 17:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('service_app', '0003_auto_20190906_1648'),
    ]

    operations = [
        migrations.AlterField(
            model_name='imagemodel',
            name='image_type',
            field=models.CharField(choices=[('SRC', 'Source'), ('DST', 'Destination'), ('WPT', 'Waypoint')], max_length=3),
        ),
    ]
