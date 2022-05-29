# Attendance-Tracker
Attendance Tracker is an Attendance Management System using Face recognition built with Django and Python.
It is used to register the attendance of users using face recognition and to view the attendance report and summary by employees and admins.

## Table of Contents
- [Technologies](#technologies)
- [Requirements](#requirements)
- [Installation](#installation)
- [Features](#features)
- [Detailed Description of the features](#detailed-description-of-the-features)
- [Applications](#applications)
- [Features that can be added in the future](#features-that-can-be-added-in-the-future)

## Technologies
This project is made using the following technologies:
- Python 3.10.4
- Django 4.0.4
- Mysql

## Requirements
- Python 3.3+
- Django 3.2+

## Installation

- Update pip
`python -m pip install --upgrade pip`
- Set-up a new virtual environment
`python -m venv venv`
`venv\Scripts\activate`
- Install cmake
`pip install cmake`
- Install dlib 
`pip install dlib`
- Install face-recognition
`pip install face-recognition`
- Install numpy
`pip install numpy`
- Install opencv-python
`pip install opencv-python`

### Run the project
Go to the project directory
`python manage.py runserver`

Open http://127.0.0.1:8000/ with your browser to view

## Features
- Users can record their attendance using face recognition
- Employees can get their attendance report by signing in using registration number and password
- Admins can sign in using their username and password and signout
- Admins can view employees' attendance report and summary
- Admins can create a new employee account and send the account password to the employee's email address
- Admins can add new admins

## Detailed Description of the features
- Admin can add an employee by creating an employee account giving the employee's details and an image, which is used for face detection when the user tries to mark attendance. Once a new employee is added, an email is sent from the attendance tracker's email address to the employee's email address containing his/her password. This password is used by the employee to view his/her attendance. 
- On entering or leaving the workplace, the user clicks on the 'ENTRY/EXIT' button on the home page, the webcam opens and the image of the person standing infront of the camera is captured. The face encodings of the captured image is compared with the face encodings of the images of users stored in the database and the user image with least face distance is taken as the match. User is asked to confirm the detected face and user details. As the user confirms, the entry or exit of the user with time stamp is recorded into the database.
- The entry time and exit time is compared to the woking hours of the company (here, I have assumed 9 am - 5 pm as the working hours) and the difference is stored in database as fields 'entryLateorEarly' (is negative if the user enters earlier than 9 am and positive if late) and 'exitLateorEarly'(is negative if the user leaves earlier than 5pm and positive if late) in minutes.Net daily working hours of the user is also calculated using entry and exit time.
- A user is considered late if he/she enters or leaves 5 minutes past 9 am or 5 pm and early if 5 minutes earlier. 
- A user is marked absent if the user enters late or exits early more than 2 hours or total working hours of the day is less than or equal to 4
- A user is marked half day present if the user enters late or exits early more than 30 minutes or total working hours of the day is less than or equal to 7
- Average late entry time, early exit time, early entry time, late exit time, working hours is calculated for a month.
- Based on the number of days the user enters late in a month and exits early in a month and the average early exit and average late entry time of the month and the average working hours of the month, the admin is provided with the recommended action to take against the incumbent.
- Employees can go to 'View Your Attendance' in the navbar and view the attendance report and summary after entering registration number and password.
- Admins can view employees' attendance report and summary and view the detailed report of each user's attendance by clicking the 'View Details' in the summary page. Admin can also get a recommended action for each employee, which is generated according to the human resource management policies of the company(here I have taken a few typical recommendations), based on the analysis of their attendance record.
- In the monthly report, the admin can get the employees who Entered Late for more than 10 days, Entered early for more than 10 days, Exited Late for more than 10 days, Exited early for more than 10 days.
- Admin can add a new admin.


A gmail account has been created for the purpose of this project. 
- Email address : attendancetrackerauth@gmail.com
- Password : attendancetracker

2 admins are currently added
- Superuser : 
Username - Admin1
Password - admin1password
- Username - Admin2
Password - admin2password

11 Attendance users are currently added to the database.
Attendance records for 2022 May is added to the Attendance Register database.
To view attendance as an employee,
1. Go to 'View your attendance'
2. Enter any one of the registration numbers of users and password as 'ashleysanu'(for eg, you can enter registration number as 20BCE1343 and password as 'ashleysanu') and select any month (select May to get summary of entered values) and any year(select 2022 to get summary of entered values)

To view attendance as an admin,
1. Login to any admin account( eg, username as Admin1, password as admin1password)
2. go to Admin login and click 'View employee attendance'.
3. Select any month and year or a whole year (select 2022 May or 2022 Whole year to get summary of entered values)

### Applications
Attendance tracker can be used in companies where managers or higher level employees, who are considered as admins, monitor and manage attendance record of employees under their juridsiction. Employees while entering and leaving the workspace record their attendance. The employees and the manager or higher level employee can get the attendance report.


### Features that can be added in future 
- A company has different categories and departments of employees with different entry and exit time policies. So expanding this project to incorporate different categories of employees and attendance analysis based on their different entry and exit time is to be added.
- Different departments have different admins in a company.This project can be modified to integrate a hierarchical model of employees and managers where there are several managers or admins and the groups of employees under each admin's jurisdiction is different. The admin can get the attendance report of employees who are under his/her jurisdiction only.
- Admins can also be employees of the company.
- Leave sanctioning mechanism can be included in the web app, where according to the company policies,the employees can apply for leave and admins can grant the leave application through the web app.
