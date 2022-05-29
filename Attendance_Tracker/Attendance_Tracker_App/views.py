from email import message
from django.shortcuts import render,redirect
from .models import AttendanceUser,AttendanceRegister
from django.db.models import Count
from django.db.models import Avg
from django.contrib import messages
from django.contrib.auth.models import User
from Attendance_Tracker import settings
from django.contrib.auth import authenticate, login, logout
from sre_constants import SUCCESS
import cv2
from django.core.mail import EmailMessage, send_mail
import datetime
import numpy as np
import face_recognition
import os
from django.db.models import Q

#index page
def index(request):
    return render(request,"AttendanceTracker/index.html",{})

#to send query mail to the attendancetracker's mail address from index page
#a copy of the sent mail is also sent to the sender's mail
def contactMail(request):
    if request.method=='POST':
        subject=request.POST.get('subject')
        fromemail=request.POST.get('Email')
        msg=request.POST.get('Message')
        send_mail(subject,msg,fromemail,['attendancetrackerauth@gmail.com',fromemail])
        messages.success(request,"Query Mail sent!")
    return redirect('index')

# Used to recognize the employee's face and register attendance
def takeAttendance(request):
    if request.method=='POST':
        x=datetime.datetime.now()
        current_time = datetime.time(x.time().hour,x.time().minute,x.time().second)
        year=x.date().year
        month=x.date().month
        day=x.date().day

        #if there is already an entry for the current day (if the employee has already entered the workplace and has marked entry attendance), set exit time 
        if AttendanceRegister.objects.filter(year=year,month=month,day=day,regno=request.POST.get('regno')).exists():
            
            att=AttendanceRegister.objects.get(year=year,month=month,day=day,regno=request.POST.get('regno'))
            att.exitTime=current_time
            stri="Thank you "+att.name+"!"
            att.save()
            
        else:
            # if there is no entry yet for the current day(the employee has not entered the workplace yet) mark the entry attendance
            att=AttendanceRegister()
            att.name=request.POST.get('name')
            att.regno=request.POST.get('regno')
            att.year=year
            att.month=month
            att.day=day
            att.entryTime=current_time
            att.save()
            stri="Have a great day "+att.name+"!"
            
        messages.success(request, stri)
        return redirect('index')

    else:
        path = 'media\images'
        imgs=[]
        regnos=[]
        #the folder'media\images' contains images of all the registered employees 
        mylist=os.listdir(path)

        #read all images into a list 'imgs'
        #add the corresponding registration numbers(their file names) to a list 'regnos'
        for c1 in mylist:
            curimg=cv2.imread(f'{path}/{c1}')
            imgs.append(curimg)
            regnos.append(os.path.splitext(c1)[0]) #add [0]



        def findencodings(imgs):
            encodelist=[]
            for img in imgs:
                #convert image color from bgr to rgb
                img=cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
                #face encodings of the image is generated 
                #a face encoding is a set of 128 computer-generated measurements of a face
                encode=face_recognition.face_encodings(img)[0]
                #face encodings of the image is added to list 'encodelist'
                encodelist.append(encode)
            return encodelist



        #get the face encodings of all known images(stored employees' images)
        encodelistknown=findencodings(imgs)
        
        rnr=""
        #capture image from camera
        cap=cv2.VideoCapture(0)

        for i in range(1):
            SUCCESS,img=cap.read()
            imgs=cv2.resize(img,(0,0),None,0.25,0.25)
            imgs=cv2.cvtColor(imgs,cv2.COLOR_BGR2RGB)

            #find faces in the image
            facescurframe=face_recognition.face_locations(imgs)
            #get the encodings of the face
            encodescurframe=face_recognition.face_encodings(imgs,facescurframe)
           
            for encodeface,faceloc in zip(encodescurframe,facescurframe):
                #compare the face encodings of captured face and the list of stored employee images
                matches=face_recognition.compare_faces(encodelistknown,encodeface)
                #get the face distances from each image to the captured image
                facedis=face_recognition.face_distance(encodelistknown,encodeface)
                
                #get the index of the employee's image with least face distance(this is the most similar to the captured face)
                matchindex=np.argmin(facedis)

                if matches[matchindex]:
                    #get the registration number of the detected(most similar face) employee
                    rn=regnos[matchindex]
                    rnr=rn
                                    
                    #to view the webcam captured image in another window(optional-disabled as of now)
                    y1,x2,y2,x1=faceloc
                    y1,x2,y2,x1=y1*4,x2*4,y2*4,x1*4
                    cv2.rectangle(img,(x1,y1),(x2,y2),(0,255,0),2)
                    cv2.rectangle(img,(x1,y2-35),(x2,y2),(0,255,0),cv2.FILLED)
                    cv2.putText(img,rn,(x1+6,y2-6),cv2.FONT_HERSHEY_COMPLEX,1,(255,255,255),2)

            
            if AttendanceUser.objects.filter(regno=rnr.upper()).exists():
                obj=AttendanceUser.objects.get(regno=rnr.upper())
                return render(request,"AttendanceTracker/takeAttendance.html",{
                        "obj":obj,    })
            else:
                messages.success(request,"User not found! Try again")
                return redirect('index')
            
            #cv2.imshow('Webcam',img)
            #cv2.waitKey(1000)
            #cv2.destroyAllWindows()
            

#admin can add a new employee to the attendance tracker by filling out a form
#after the admin creates an employee's account,a mail is sent to the employee's mail address, specifiying his/her password
def addEmployee(request):
    if request.method=='POST':
        enteredemail=request.POST.get('email')
        enteredregno=request.POST.get('regno').upper()
        pass1=request.POST.get('pass1')
        pass2=request.POST.get('pass2')
        #get the extension or file format of the uploaded image
        ext=request.FILES['img1'].name.split('.')[-1]
        
        #invalid file format
        if ext!="jpg" and ext!="jpeg" and ext!="jfif" and ext!="pjpeg" and ext!="pjp" and ext!="png":
            messages.error(request, "Invalid file format! Try again.")
            return redirect('addEmployee')

        #if entered registration number is already registered
        if AttendanceUser.objects.filter(regno=enteredregno):
            messages.error(request, "User already exists! Try again.")
            return redirect('addEmployee')

        #if entered mail address is already registered    
        if AttendanceUser.objects.filter(email=enteredemail):
            messages.error(request, "Email Address already exists! Try again.")
            return redirect('addEmployee')

        #if typed passwords dont match
        if pass1 != pass2:
            messages.error(request, "Passwords didn't match! Try again.")
            return redirect('addEmployee')


        #create a new object for attendance user (new employee) and store all values
        emp=AttendanceUser()
        emp.name=request.POST.get('name')
        emp.regno=request.POST.get('regno').upper()
        emp.password=request.POST.get('pass1')
        emp.email=request.POST.get('email')
        emp.image=request.FILES['img1']
        emp.save()

        #send password to the employee via an email
        subject="Welcome to Attendance Tracker !"
        message = "Dear " + emp.name + ",\nWelcome to the Attendance Tracker! Your account has been created.\nHere's your password: "+emp.password+"\n\n\nThank you!\n\nAttendance Tracker\n"
        from_email = settings.EMAIL_HOST_USER
        to_list = [emp.email]
        send_mail(subject, message, from_email, to_list, fail_silently=True)

        messages.error(request,"New Employee Account has been created succesfully!")
        return redirect("adminIndex")

    else:
        return render(request,"Admintemplates/addEmployee.html",{})



#Admin can create more admin accounts
def addAdmin(request):
    if request.method == "POST":
        username = request.POST.get('name')
        pass1 = request.POST.get('pass1')
        pass2 = request.POST.get('pass2')
        
        #if another admin has the same username
        if User.objects.filter(username=username):
            messages.error(request, "Admin already exists!")
            return redirect('addAdmin')
        
        #if the entered passwords dont match
        if pass1 != pass2:
            messages.error(request, "Passwords don't match! Try again.")
            return redirect('addAdmin')

        #if length of entered password is less than 8
        if len(pass1)<8:
            messages.error(request, "Password should be atleast 8 characters! Try again.")
            return redirect('addAdmin')
        

        #create new user object (new admin)
        admin = User.objects.create_user(username,0,pass1)
        admin.username=username
        admin.is_active = True
        admin.is_staff = True
        admin.save()
        messages.success(request, "New Admin Account has been created succesfully!")
        
        return redirect("adminIndex")
    else:
        return render(request, "Admintemplates/addAdmin.html")
    

#admin can sign in to their account
def adminSignin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        pass1 = request.POST.get('pass1')
        
        #to authenticate the entered username and password
        user = authenticate(username=username, password=pass1)
        
        #if entered username and password are present in database and matches, login
        if user is not None:
            login(request, user)
            return redirect("adminIndex")
        else:
            messages.error(request, "Incorrect Credentials!")
            return redirect('adminSignin')
    
    return render(request, "Admintemplates/adminSignin.html")




    
def adminSignout(request):
    logout(request)
    return redirect('adminIndex')


#Index page of admin
def adminIndex(request):
    #if admin is signed in , display the index page
    if request.user.is_authenticated:
        return render(request,"Admintemplates/adminIndex.html",{"name":request.user.username})
    #if the admin is not signed in, ask the admin to sign in
    else:
        return render(request,"Admintemplates/adminSignin.html",{})

def get_action(num_earlyentry,num_lateentry,num_earlyexit,num_lateexit,avgLateentryby,avgEarlyentryby,avgLateexitby,avgEarlyexitby,avgWorkinghrs):
    if num_lateentry>=20 or num_earlyexit>=20 or avgLateentryby>=30 or avgEarlyexitby>=30 or avgWorkinghrs<=4:
        return "Disciplinary Action against the incumbent"
    elif num_lateentry>=15 or num_earlyexit>=15 or avgLateentryby>=15 or avgEarlyexitby>=15 or avgWorkinghrs<=6:
        return "Compulsory time management training"
    elif num_lateentry>=10 or num_earlyexit>=10 or avgLateentryby>=10 or avgEarlyexitby>=10 or avgWorkinghrs<=6.5:
        return "Oral preliminary warning and Suggest optional time management training"
    elif num_lateentry>=5 or num_earlyexit>=5 or avgLateentryby>=8 or avgEarlyexitby>=8 or avgWorkinghrs<=7.5:
        return "Initial Warning"
    else:
        return "-"
    
    


#Admin can view the attendance of the employees
def adminAttendanceView(request):
    if request.method=='POST':
        year=request.POST.get('year')
        month=request.POST.get('month')
        employees=AttendanceUser.objects.all()
        empcount=AttendanceUser.objects.all().count()
        Listofattendance=[]

        #to get the attendance summary of the whole year
        if(int(month)==13):
            totdays=365
            for obj in employees:
                reg=obj.regno
                name=AttendanceUser.objects.get(regno=reg).name 

                #count the number of days the employee was present full day
                presentdays=AttendanceRegister.objects.filter(regno=reg,year=year,attendance=1).count()

                #count the number of days the employee was present half day
                halfdays=AttendanceRegister.objects.filter(regno=reg,year=year,attendance=0.5).count()

                #attendance entries of days when employee entered the workplace at or after 9:00am
                entryobjs=AttendanceRegister.objects.filter(year=year,regno=reg,entryLateorEarly__gte=0)
               
                workhrsobjs=AttendanceRegister.objects.filter(regno=reg,year=year)
                avgWorkinghrs=0
                c0=0
                for ob in workhrsobjs:
                    c0=c0+1
                    avgWorkinghrs=avgWorkinghrs+ob.totWorkinghours
                avgWorkinghrs=avgWorkinghrs/totdays
                avgLateentry=0
                c=0
                for ob1 in entryobjs:
                    c=c+1
                    avgLateentry=avgLateentry+ob1.entryLateorEarly
                if(c>0):
                    avgLateentry=avgLateentry/totdays

                #attendance entries of days when employee left the workplace at or before 5:00 pm
                exitobjs=AttendanceRegister.objects.filter(year=year,regno=reg,exitLateorEarly__lte=0)
                avgEarlyexit=0
                c1=0
                for ob2 in exitobjs:
                    c1=c1+1
                    avgEarlyexit=avgEarlyexit+ob1.exitLateorEarly
                if(c1>0):
                    avgEarlyexit=-1*(avgEarlyexit/totdays)

                #number of days the employee was absent
                absentdays=totdays-presentdays-halfdays
                tempList=[name,reg,presentdays,halfdays,absentdays,round(avgLateentry,2),round(avgEarlyexit,2),round(avgWorkinghrs,2)]
                Listofattendance.append(tempList)
                
            
             # Listofattendance=mergesort(Listofattendance)
            return render(request,"Admintemplates/yearAttendanceData.html",{
            'employees':employees,
            'empcount':empcount,
            "list":Listofattendance,
            'year':year,
            })

        #if admin wants to get the attendance summary of a particular month
        else:            
            #number of days in a month calculation
            if ((int(month)<=7 and int(month)%2!=0) or (int(month)>7 and int(month)%2==0)):
                totdays=31
            elif int(month)==2:
                totdays=27
            else:
                totdays=30

            no_of_emp_entrylate_morethan10days=0
            emp_entrylate_morethan10days=[]
            no_of_emp_exitearly_morethan10days=0
            emp_exitearly_morethan10days=[]
            no_of_emp_avgworkinghrs_morethan8hrs=0
            emp_avgworkinghrs_morethan8hrs=[]
            no_of_emp_entryearly_morethan10days=0
            emp_entryearly_morethan10days=[]
            no_of_emp_exitlate_morethan10days=0
            emp_exitlate_morethan10days=[]
            for obj in employees:
                reg=obj.regno
                name=AttendanceUser.objects.get(regno=reg).name
                presentdays=AttendanceRegister.objects.filter(regno=reg,year=year,month=month,attendance=1).count()
                halfdays=AttendanceRegister.objects.filter(regno=reg,year=year,month=month,attendance=0.5).count()
                absentdays=totdays-presentdays-halfdays

                tempobjs=AttendanceRegister.objects.filter(year=year,month=month,regno=reg)
                no_of_days_earlyentry=0
                no_of_days_lateentry=0
                no_of_days_lateexit=0
                no_of_days_earlyexit=0
                
                avgLateentryby=0
                avgEarlyentryby=0
                avgEarlyexitby=0
                avgLateexitby=0
                avgWorkinghrs=0
                c0=0
                c1=0
                c2=0
                c3=0
                c4=0
                for ob in tempobjs:

                    #here,entering 5 or more minutes past 9 am is considered as late entry 
                    #here,leaving 5 or more minutes earlier than 5 pm is considered as early exit
                    #here,entering 5 or more minutes earlier than 9 am is considered as early entry 
                    #here,leaving 5 or more minutes past 5 pm is considered as late exit
                    if ob.entryLateorEarly>=5:
                        no_of_days_lateentry=no_of_days_lateentry+1
                    elif ob.entryLateorEarly<=-5:
                        no_of_days_earlyentry=no_of_days_earlyentry+1
                    if ob.exitLateorEarly<=-5:
                        no_of_days_earlyexit=no_of_days_earlyexit+1
                    elif ob.exitLateorEarly>=5:
                        no_of_days_lateexit=no_of_days_lateexit+1
                    if ob.entryLateorEarly>0:
                        avgLateentryby=avgLateentryby+ob.entryLateorEarly
                        c0=c0+1
                    elif ob.entryLateorEarly<0:
                        avgEarlyentryby=avgEarlyentryby+-1*(ob.entryLateorEarly)
                        c1=c1+1
                    if ob.exitLateorEarly>0:
                        avgLateexitby=avgLateexitby+ob.exitLateorEarly
                        c2=c2+1
                    elif ob.exitLateorEarly<0:
                        avgEarlyexitby=avgEarlyexitby+-1*(ob.exitLateorEarly)
                        c3=c3+1
                    if ob.totWorkinghours>0:
                        avgWorkinghrs=avgWorkinghrs+ob.totWorkinghours
                        c4=c4+1
                if c0>0:
                    avgLateentryby=avgLateentryby/totdays
                if c1>0:
                    avgEarlyentryby=avgEarlyentryby/totdays
                if c2>0:
                    avgLateexitby=avgLateexitby/totdays
                if c3>0:
                    avgEarlyexitby=avgEarlyexitby/totdays
                if c4>0:
                    avgWorkinghrs=avgWorkinghrs/totdays
                if no_of_days_earlyentry>=10:
                    no_of_emp_entryearly_morethan10days=no_of_emp_entryearly_morethan10days+1
                    emp_entryearly_morethan10days.append([reg,name])
                if no_of_days_lateentry>=10:
                    no_of_emp_entrylate_morethan10days=no_of_emp_entrylate_morethan10days+1
                    emp_entrylate_morethan10days.append([reg,name])
                if no_of_days_earlyexit>=10:
                    no_of_emp_exitearly_morethan10days=no_of_emp_exitearly_morethan10days+1
                    emp_exitearly_morethan10days.append([reg,name])
                if no_of_days_lateexit>=10:
                    no_of_emp_exitlate_morethan10days=no_of_emp_exitlate_morethan10days+1
                    emp_exitlate_morethan10days.append([reg,name])
                if avgWorkinghrs>8.0:
                    no_of_emp_avgworkinghrs_morethan8hrs=no_of_emp_avgworkinghrs_morethan8hrs+1
                    emp_avgworkinghrs_morethan8hrs.append([reg,name])
                



                action_recommended=get_action(no_of_days_earlyentry,no_of_days_lateentry,no_of_days_earlyexit,no_of_days_lateexit,avgLateentryby,avgEarlyentryby,avgLateexitby,avgEarlyexitby,avgWorkinghrs)
                tempList=[reg,name,presentdays,halfdays,absentdays,round(avgEarlyentryby,2),round(avgLateentryby,2),round(avgEarlyexitby,2),round(avgLateexitby,2),round(avgWorkinghrs,2),action_recommended]
                Listofattendance.append(tempList)
            
            return render(request,"Admintemplates/monthlyAttendanceData.html",{
                "year":year,
                "month":month,
                "list":Listofattendance,
                "no_of_emp_entrylate_morethan10days":no_of_emp_entrylate_morethan10days,
                "emp_entrylate_morethan10days":emp_entrylate_morethan10days,
                "no_of_emp_exitearly_morethan10days":no_of_emp_exitearly_morethan10days,
                "emp_exitearly_morethan10days":emp_exitearly_morethan10days,
                "no_of_emp_avgworkinghrs_morethan8hrs":no_of_emp_avgworkinghrs_morethan8hrs,
                "emp_avgworkinghrs_morethan8hrs":emp_avgworkinghrs_morethan8hrs,
                "no_of_emp_entryearly_morethan10days":no_of_emp_entryearly_morethan10days,
                "emp_entryearly_morethan10days":emp_entryearly_morethan10days,
                "no_of_emp_exitlate_morethan10days":no_of_emp_exitlate_morethan10days,
                "emp_exitlate_morethan10days":emp_exitlate_morethan10days,
                "empcount":empcount
            })


    else:
        return render(request,"Admintemplates/getDetailsadmin.html",{})




#detailed view of an employee's attendance of a month
def getAttendance(request):
    if request.method=='POST':
        #if an admin is trying to get the attendance details of an employee
        if request.POST.get('querytype')=="2":
            list1=request.POST.get('list')
            regno=list1[2:11]
            print(regno)
            
        
        #if an employee is trying to get his/her attendance details
        if request.POST.get('querytype')=="1":
            regno=request.POST.get('regno').upper()
            passw=request.POST.get('pass')
        if AttendanceUser.objects.filter(regno=regno).exists():
            obj=AttendanceUser.objects.get(regno=regno)
            if request.POST.get('querytype')=="1":
                if obj.password!=passw:
                    messages.error(request,"Incorrect Password! Try Again.")
                    return redirect('getDetails')

            year=request.POST.get('year')
            month=request.POST.get('month')
            name=obj.name

            if ((int(month)<=7 and int(month)%2!=0) or (int(month)>7 and int(month)%2==0)):
                numDays=31
            elif int(month)==2:
                numDays=27
            else:
                numDays=30
            
            list = []
            for i in range(1,numDays+1):
                list.append(i)
            
            #count number of days the employee is present full day in the month
            presentdays=AttendanceRegister.objects.filter(regno=regno,month=month,year=year,attendance=1).count()
            #count number of days the employee is present half day in the month
            halfdays=AttendanceRegister.objects.filter(regno=regno,month=month,year=year,attendance=0.5).count()
            #number of days the employee is absent in the month
            absentdays=numDays-presentdays-halfdays
            return render(request,"AttendanceTracker/printAttendance.html",{
                "name":name,
                "regno":regno,
                "year":year,
                "month":month,
                "list":list,
                "present":presentdays,
                "half":halfdays,
                "absent":absentdays,
                "numdays":numDays
            })
            
        else:
            messages.error(request,"Invalid Registration number! Try Again.")
            return redirect('getDetails')

    else:
        return render(request,"AttendanceTracker/getDetails.html",{})
def getDetails(request):
       return render(request,"AttendanceTracker/getDetails.html",{})