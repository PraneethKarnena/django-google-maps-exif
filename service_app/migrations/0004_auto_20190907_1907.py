# Generated by Django 2.2.5 on 2019-09-07 19:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('service_app', '0003_auto_20190907_1725'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jobmodel',
            name='total_distance',
            field=models.FloatField(blank=True, default='Calculating...', null=True),
        ),
    ]