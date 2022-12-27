#import required packages
from flask import Flask, render_template, redirect, flash, url_for, session, request, json, jsonify
from flask_sqlalchemy import SQLAlchemy
from encryptPass import *
from calcAttendance import *
from datetime import datetime

app = Flask(__name__)
app.app_context().push()

# app configurations
app.config['SECRET_KEY'] = 'HtyX6656'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///campus.db' # path to database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy(app)

#creating database models
class student(db.Model):
    # table to store the details of the student
    sid = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    fname = db.Column(db.String(100), nullable=False)
    lname = db.Column(db.String(100), nullable=False)
    sem = db.Column(db.Integer, nullable=False)
    dno = db.Column(db.Integer)
    email = db.Column(db.String(100))
    dob = db.Column(db.String(20))
    sec = db.Column(db.String(1))


class faculty(db.Model):
    # table to store the details of the faculty
    fid = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    fname = db.Column(db.String(100), nullable=False)
    lname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    dno = db.Column(db.Integer)
    doj = db.Column(db.String(20))
    dob = db.Column(db.String(20))

class courses(db.Model):
    # table to store the details of all the avilable courses
    cid = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    cname = db.Column(db.String(100), nullable=False)
    credit = db.Column(db.Integer)
    c_type = db.Column(db.String(50))

class attendance(db.Model):
    # table to store the attendance record of all the students
    sno = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sid = db.Column(db.String(10), nullable=False)
    cid = db.Column(db.String(10), nullable=False)
    status = db.Column(db.Integer)
    date_time = db.Column(db.String(200))
    

class student_login_details(db.Model):
    # table to store the login details of the student
    s_email = db.Column(db.String(100), primary_key=True, nullable=False)
    s_password = db.Column(db.String(400), nullable=False)

class teacher_login_details(db.Model):
    # table to store the login details of the teacher
    t_email = db.Column(db.String(100), primary_key=True, nullable=False)
    t_password = db.Column(db.String(400), nullable=False)

class department(db.Model):
    # table to store details of all the departments
    dno = db.Column(db.Integer, primary_key=True, nullable=False)
    dname = db.Column(db.String(100))
    hod = db.Column(db.String(100))

class handles(db.Model):
    fid = db.Column(db.String(10), primary_key=True, nullable=False)
    cid = db.Column(db.String(10), nullable=False)
    sec = db.Column(db.String(1), nullable = False)

class has_enrolled(db.Model):
    sno = db.Column(db.Integer, primary_key = True, nullable=False, autoincrement=True)
    sid = sid = db.Column(db.String(10), nullable=False)
    cid = db.Column(db.String(10), nullable=False)

db.create_all()

#login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['username'] = request.form.get('username') # get username from form
        password = encrypt(request.form.get('password')) # encrypt the password
        # check if the person logging in is a teacher or a student
        t = request.form.get('teacher') 
        s = request.form.get('student')

        if t == "1":
            #teacher login

            #authenticate teacher
            teacher = teacher_login_details.query.filter_by(t_email = session['username']).first()

            if teacher != None:
                #teacher exists
                if teacher.t_password == password:
                    #password is matching
                    return redirect('/')
                else:
                    flash('Wrong username or password.')
            else:
                flash('Teacher does not exist in the database.')

        if s == "1":
            #student login

            #authenticate student
            student = student_login_details.query.filter_by(s_email = session['username']).first()

            if student != None:
                #teacher exists
                if student.s_password == password:
                    #password is matching
                    return redirect('/') # redirect to homepage if login is successful
                else:
                    flash('Wrong username or password.')
            else:
                flash('Student does not exist in the database.')
            # return redirect('/')

        else:
            return render_template('login.html')
        
        
    return render_template('login.html')


# Logout
@app.route('/logout', methods=['GET', 'POST'])
def logout():
    try:
        session.pop('username')
    except:
        print('User not logged in')
    return redirect('login')


#admin page
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    
    if request.method == 'POST':
        t = request.form.get('my_val')
        if t == "1":
            #adding new student
            email = request.form.get("s_email")
            p = encrypt(request.form.get("s_pass"))

            # add student email and password to the student login details table
            new_student = student_login_details(s_email = email, s_password = p)
            flash('Added new student')

            #add new student to the student table
            lname = request.form.get('s_lname')
            fname = request.form.get('s_fname')
            sem = request.form.get('s_sem')
            dn = request.form.get('s_dept')
            dob = str(request.form.get('s_dob'))
            sec = request.form.get('s_sec')
            s = student(fname=fname, lname=lname, sem=sem, dno=dn, email=email, dob=dob, sec=sec)
            db.session.add(s)
            db.session.add(new_student)
            db.session.commit()
            
        if t == "0":
            #adding new teacher
            email = request.form.get("t_email")
            p = encrypt(request.form.get("t_pass"))
            new_teacher = teacher_login_details(t_email = email, t_password = p)

            fname = request.form.get('t_fname')
            lname = request.form.get('t_lname')
            dn = request.form.get('t_dept')
            sec = request.form.get('t_sec')
            dob = str(request.form.get('t_dob'))
            doj = str(request.form.get('t_doj'))
            t = faculty(fname=fname, lname=lname, dno=dn, dob=dob, doj=doj, email=email)
            flash('Added new teacher')
            try:
                db.session.add(t)
                db.session.add(new_teacher)
                db.session.commit()
            except:
                print('Could not add new record.')

    #add new teacher form details
    return render_template('admin.html')

#attendance for a sec students
@app.route('/ASec', methods=['GET', 'POST'])
def ASec():
    #query DB to get all the students from A sec
    s = []
    var = student.query.filter_by(sec = 'A').all()
    for st in var:
        f = st.fname
        l = st.lname
        name = f + " " + l
        s.append(name)
    
    #collect the attendance status
    if request.method == 'POST':
        form_data = request.form
        no_pres = 0
        no_abs = 0
        print(form_data)
        for ele in form_data:
            
            if form_data[ele] == "1":
                no_pres += 1
                
            else:
                no_abs += 1
            # query student to get the id of the student
            # lname = ele.split(' ')[1]
            lname = ele.split(' ')[0]
            var1 = student.query.filter_by(fname=lname).first()
            sid = var1.sid
            # query to get the course using faculty name
            print(session['username'])
            var2 = faculty.query.filter_by(email = session['username']).first()
            fid = var2.fid
            #get course id using fid from handles table
            print(fid)
            var3 = handles.query.filter_by(fid = fid).first()
            cid = var3.cid
            
            # create a new record for attendance
            new_att = attendance(sid=sid,cid=cid,status=form_data[ele],date_time=datetime.now())
            db.session.add(new_att)
            db.session.commit()
        # end of transaction
        
        flash("DOne")
        return redirect('/')

    return render_template('A_sec.html', students=s)

#attendance for b sec students
@app.route('/BSec', methods=['GET', 'POST'])
def BSec():
    #query DB to get all the students from A sec
    s = []
    var = student.query.filter_by(sec = 'B').all()
    for st in var:
        f = st.fname
        l = st.lname
        name = f + " " + l
        s.append(name)
    
    #collect the attendance status
    if request.method == 'POST':
        form_data = request.form
        no_pres = 0
        no_abs = 0
        print(form_data)
        for ele in form_data:
            
            if form_data[ele] == "1":
                no_pres += 1
                
            else:
                no_abs += 1
            # query student to get the id of the student
            # lname = ele.split(' ')[1]
            lname = ele.split(' ')[0]
            print(lname)
            try:
                var1 = student.query.filter_by(fname=lname).first()
                sid = var1.sid
                # query to get the course using faculty name
                print(session['username'])
                var2 = faculty.query.filter_by(email = session['username']).first()
                fid = var2.fid
                #get course id using fid from handles table
                print(fid)
                var3 = handles.query.filter_by(fid = fid).first()
                cid = var3.cid
            
            # create a new record for attendance
            
                new_att = attendance(sid=sid,cid=cid,status=form_data[ele],date_time=datetime.now())
                db.session.add(new_att)
                db.session.commit()
            except:
                print('Sorry!, Could not update attendance')
                # flash('Sorry!, Could not update attendance')
        # end of transaction
        
        flash("DOne")
        return redirect('/')
    return render_template('B_sec.html', students=s)


#attendance for c sec students
@app.route('/CSec', methods=['GET', 'POST'])
def CSec():
    #query DB to get all the students from A sec
    return render_template('C_sec.html', students=['111', '222', '333', '444', '555'])

# index page
@app.route('/', methods=['GET', 'POST'])
def index():
    login = False
    log_person = 0
    per = 0
    tors = "1"
    if 'username' in session:
        login = True
        #print(session['username'])
    else:
        return render_template('error.html')
    

    #get student course details and attendance percentage
    # do this only for student login
    
    if session['username'] in ['student1@gmail.com', 'student2@gmail.com', 'student3@gmail.com', 'student4@gmail.com', 'sherlock@gmail.com', 'irene@gmail.com', 'watson@gmail.com']:
        pres = 0
        per1 = 0
        tors = "0"
        total = 0
        total1 = 0
        pres1 = 0
        stud = student.query.filter_by(email = session['username']).first() # got student record from student table
        att_rows = attendance.query.filter_by(sid = stud.sid).all()
        for i in att_rows:
            # for dbms course
            if i.cid == "1":
                total += 1

                if i.status == 1:
                    pres += 1
        #print(pres, total)
        # for i in att_rows:
        #     # for cn course
        #     if i.cid == "3":
        #         total1 += 1

        #         if i.status == 1:
        #             pres1 += 1
        # print(stud)
        # print((pres, total))
        # if stud != None:
        #     print("Teacher")

        # if att_rows != None and stud != None:
        #     per1 = calculate(pres, total)
        #     # per2 = calculate(pres1, total1)
        #     per2 = 12
        per1 = calculate(pres, total)
        per2 = 9
        return render_template('dashboard.html', c_name1="DBMS", teacher=tors, c_name2="Computer Networks", percent1=float(per1), percent2 = float(12.5))
    return render_template('dashboard.html', c_name1="DBMS", teacher=tors, c_name2="Computer Networks")


# code to run the application
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')