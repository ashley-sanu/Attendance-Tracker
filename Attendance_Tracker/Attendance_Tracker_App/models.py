from distutils.command.upload import upload
from statistics import mode
from django.db import models
import os
from django.contrib.auth.models import User

def entry_exit(hr,min,std):
    xhr=hr-std
    hrtomin=xhr*60
    return (hrtomin+min)
def totworkhrs(entryh,entrym,exith,exitm):
    toth=(exith-entryh)-1
    min=(60-entrym)+exitm
    tott=toth+((min)/float(60))
    return round(tott,2)
def ifattendance(lateentry,earlyexit,totworkhrs):
    #if the user enters late or exits early more than 2 hours or total working hours of the day is less than or equal to 4,the user is considered absent for the day
    if lateentry>=120 or earlyexit<=-120 or totworkhrs<=4:
        return 0
    #if the user enters late or exits early more than 30 minutes or total working hours of the day is less than or equal to 7,the user is considered half day present
    elif lateentry>=30 or earlyexit<=-30 or totworkhrs<=7:
        return 0.5
    #else the user is considered full day present
    else:
        return 1


#the image file uploaded by admin is stored with the employee's registration number as filename
def change_name_on_upload(instance,filename):
    ext="."+filename.split('.')[-1]
    path="images/" 
    newfilename=instance.regno+ext
    return os.path.join(path, newfilename)


#employees' data is stored as attendance user
class AttendanceUser(models.Model):
    name=models.CharField(max_length=20)
    regno=models.CharField(max_length=20)
    password=models.CharField(max_length=20)
    email=models.CharField(max_length=30)
    image=models.ImageField(upload_to=change_name_on_upload)

    def __str__(self):
        return f"{self.regno} : {self.name}"


class AttendanceRegister(models.Model):
    name=models.CharField(max_length=20,default=" ")
    regno=models.CharField(max_length=20,default=" ")
    year=models.IntegerField()
    month=models.IntegerField()
    day=models.IntegerField()
    entryTime=models.TimeField(null=True)
    exitTime=models.TimeField(null=True)

    entryLateorEarly=models.IntegerField(default=0,null=True)
    exitLateorEarly=models.IntegerField(default=0,null=True)
    totWorkinghours=models.FloatField(default=0,null=True)
    attendance=models.FloatField(default=0)


    def save(self, *args, **kwargs):
        change_in_entrytime=entry_exit(int(self.entryTime.hour),int(self.entryTime.minute),9)
        self.entryLateorEarly=change_in_entrytime
        if self.exitTime!=None:
            change_in_exittime=entry_exit(int(self.exitTime.hour),int(self.exitTime.minute),17)
            self.exitLateorEarly=change_in_exittime
            totalworkinghrs=totworkhrs(int(self.entryTime.hour),int(self.entryTime.minute),int(self.exitTime.hour),int(self.exitTime.minute))
            self.totWorkinghours=totalworkinghrs
            self.attendance=ifattendance(change_in_entrytime,change_in_exittime,totalworkinghrs)

        super(AttendanceRegister, self).save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.regno} : {self.name}"

