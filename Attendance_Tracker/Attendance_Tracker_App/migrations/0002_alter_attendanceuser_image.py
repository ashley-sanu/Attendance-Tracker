# Generated by Django 4.0.4 on 2022-05-22 12:05

import Attendance_Tracker_App.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Attendance_Tracker_App', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attendanceuser',
            name='image',
            field=models.ImageField(upload_to=Attendance_Tracker_App.models.change_name_on_upload),
        ),
    ]