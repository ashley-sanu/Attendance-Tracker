from django import template
from Attendance_Tracker_App import models
from django.utils.deconstruct import deconstructible
from Attendance_Tracker_App.models import AttendanceRegister

register = template.Library()
@register.simple_tag
def get_obj(d,m,y,r,attr):
    obj1=AttendanceRegister.objects.filter(month=m,year=y,day=d,regno=r)
    if obj1.exists():
        ret_value=getattr(AttendanceRegister.objects.get(month=m,year=y,day=d,regno=r),attr)
        if(attr=="attendance"):
            if ret_value==1:
                return "Present"
            elif ret_value==0.5:
                return "Half Day"
            else:
                return "Absent"
        elif(attr=="entryLateorEarly"):
            if ret_value<=0:
                return 0
        elif(attr=="exitLateorEarly"):
            if ret_value>=0:
                return 0
            else:
                ret_value=-1*ret_value
        if((attr=="entryLateorEarly" or attr=="exitLateorEarly") and (ret_value>=60 or ret_value<=-60)):
            hr=ret_value//60
            mins=ret_value-(hr*60)
            ret_string=str(hr)+" hours "+str(mins)+" minutes"
            return ret_string
        if(attr=="entryLateorEarly" or attr=="exitLateorEarly"):
            return str(ret_value)+" minutes"


        elif(attr=="totWorkinghours"):
            import math
            val=math.modf(ret_value)
            hrs=int(val[1])
            mins=round(val[0]*60,2)
            return str(hrs)+" hours "+str(mins)+" minutes "
        return ret_value
    else:
        if(attr=="attendance"):
            return "Absent"
        return ""




@register.simple_tag
def get_month(n):
    if(n=="1"):
        return "January"
    if(n=="2"): 
        return "February"
    if(n=="3"):
        return "March"
    if(n=="4"):
        return "April"
    if(n=="5"):
        return "May"
    if(n=="6"):
        return "June"
    if(n=="7"):
        return "July"
    if(n=="8"):
        return "August"
    if(n=="9"):
        return "September"
    if(n=="10"):
        return "October"
    if(n=="11"):
        return "November"
    if(n=="12"):
        return "December"
    

