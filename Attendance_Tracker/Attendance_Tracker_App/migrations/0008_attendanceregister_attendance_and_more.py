# Generated by Django 4.0.4 on 2022-05-24 03:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Attendance_Tracker_App', '0007_remove_attendanceregister_attuser_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='attendanceregister',
            name='attendance',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='attendanceregister',
            name='entry_lateorearly',
            field=models.IntegerField(default=0, null=True),
        ),
        migrations.AddField(
            model_name='attendanceregister',
            name='exit_lateorearly',
            field=models.IntegerField(default=0, null=True),
        ),
        migrations.AddField(
            model_name='attendanceregister',
            name='totWorkinghours',
            field=models.FloatField(default=0, null=True),
        ),
    ]