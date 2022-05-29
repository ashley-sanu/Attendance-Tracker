from django.contrib import admin

# Register your models here.
from .models import AttendanceUser,AttendanceRegister

# Register your models here.
admin.site.register(AttendanceUser)
admin.site.register(AttendanceRegister)