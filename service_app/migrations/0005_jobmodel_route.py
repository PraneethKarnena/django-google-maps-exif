# Generated by Django 2.2.5 on 2019-09-06 18:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('service_app', '0004_auto_20190906_1718'),
    ]

    operations = [
        migrations.AddField(
            model_name='jobmodel',
            name='route',
            field=models.TextField(blank=True, null=True),
        ),
    ]