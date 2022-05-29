from django.urls import path

from . import views
urlpatterns=[
    path('', views.index, name="index"),
    path('contactMail', views.contactMail, name="contactMail"),
    path('addEmployee',views.addEmployee,name="addEmployee"),
    path('addAdmin',views.addAdmin,name="addAdmin"),
    path('takeAttendance',views.takeAttendance,name="takeAttendance"),
    path('getAttendance',views.getAttendance,name="getAttendance"),
    path('getDetails',views.getDetails,name="getDetails"), 
    path('adminSignin', views.adminSignin, name='adminSignin'),
    path('adminSignout', views.adminSignout, name='adminSignout'),
    path('adminIndex',views.adminIndex,name='adminIndex'),
    path('adminAttendanceView',views.adminAttendanceView,name='adminAttendanceView'),
    ]
