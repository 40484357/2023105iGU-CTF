from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from dynamodb import getUser, checkUsername, checkLecturerCode, insertUser, loadUser
from flask_login import login_user, login_required, logout_user, current_user
import random
auth = Blueprint('auth', __name__)

with open(r'usernames.txt') as l:
    words = l.readlines()
    usernames = [x.strip().lower() for x in words]

def selectUsername():
    usernameLen = len(usernames) -1
    selection = random.randint(0, usernameLen)
    username = usernames[selection]
    return username

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('views.logged_in'))
    else:
        if request.method == 'POST':
            email = request.form.get('email')
            password = request.form.get('password')

            user = loadUser(email)

            try:
                userPassword = user[0]['password']
                print('userpassword retrieved')
                if check_password_hash(userPassword, password):
                    flash('logged in successfully', category='success')
                    new_user = User(email=email, password=userPassword, user_name = user[0]['user_name'], lecturerCode = user[0]['lecturerCode'], lecturerStatus=user[0]['lecturerStatus'])
                    login_user(new_user, remember=True)
                    return redirect(url_for('views.logged_in'))
                else:
                    flash('incorrect password', category='error')
                    print('wrong password')
            except:
                flash('email does not exist', category='error')
        return render_template("login.html")

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('views.landing'))

# @auth.route('/sign-up', methods=['GET', 'POST'])
# def sign_up():
#     if current_user.is_authenticated:
#         return redirect(url_for('views.logged_in'))
#     else:
  
#         if request.method == 'POST':
        
#             if request.form['account-type'] == 'studentAccount':

#                 studentEmail = request.form.get('student-email')
#                 studentPassword = request.form.get('student-password')
#                 studentPassword2 = request.form.get('student-password2')
#                 lecturerCode = request.form.get('student-code')
#                 username = selectUsername()
#                 studentUser = users.query.filter_by(email=studentEmail).first()
#                 usernameCheck = users.query.filter_by(user_name = username).all()
#                 codeCheck = users.query.filter_by(lecturerId=lecturerCode).first()

#                 if studentUser:
#                     flash('email already exists.', category='error')
                
#                 elif len(studentEmail) < 8:
#                     flash('Email must be greater than 7 characters', category='error')
                
#                 elif len(studentPassword) < 7:
#                     flash('Password must be greater than 7 characters', category='error')
                
#                 elif studentPassword != studentPassword2:
#                     flash('Passwords don\'t match', category='error')
                    
#                 else:

#                     if  usernameCheck:
#                         number = usernameCheck.len + 1
#                         newUsername = username + number
#                         username = newUsername

#                     if codeCheck == None:
#                         flash('Code does not exist.', category='error')
#                         lecturerCode=None

#                     new_user = users(lecturerStatus = 0, email=studentEmail, password=generate_password_hash(studentPassword, method='sha256'), user_name = username, lecturerCode = lecturerCode)
#                     db.session.add(new_user)
#                     db.session.commit()
#                     flash('Account created', category='success')
#                     login_user(new_user, remember=True) 
#                     return redirect(url_for('views.logged_in'))

#             if request.form['account-type'] == 'lecturerAccount':
                
#                 lecturerEmail = request.form.get('lecturer-email')
#                 lecturerPassword = request.form.get('lecturer-password')
#                 lecturerPassword2 = request.form.get('lecturer-password2')
#                 username = selectUsername()
#                 lecturerUser = users.query.filter_by(email=lecturerEmail).first()
#                 usernameCheck = users.query.filter_by(user_name = username).all()
#                 lecturerId = random.randint(100000,999999)  
            
#                 if lecturerUser:
#                     flash('email already exists.', category='error')
                
#                 elif len(lecturerEmail) < 8:
#                     flash('Email must be greater than 7 characters', category='error')
                
#                 elif len(lecturerPassword) < 7:
#                     flash('Password must be greater than 7 characters', category='error')
                
#                 elif lecturerPassword != lecturerPassword2:
#                     flash('Passwords don\'t match', category='error')
                

#                 else:
#                     if  usernameCheck:
#                         number = usernameCheck.len + 1
#                         newUsername = username + number
#                         username = newUsername

#                     new_user = users(lecturerStatus = 1, lecturerId = lecturerId, email=lecturerEmail, password=generate_password_hash(lecturerPassword, method='sha256'), user_name = username, lecturerCode = lecturerId)
#                     db.session.add(new_user)
#                     db.session.commit()
#                     flash('Account created', category='success')
#                     login_user(new_user, remember=True) 
#                     return redirect(url_for('views.logged_in'))


#         return render_template("register.html")


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if current_user.is_authenticated:
        return redirect(url_for('views.logged_in'))
    else:
        if request.method == 'POST':
        
            if request.form['account-type'] == 'studentAccount':

                studentEmail = request.form.get('student-email')
                studentPassword = request.form.get('student-password')
                studentPassword2 = request.form.get('student-password2')
                lecturerCode = request.form.get('student-code')
                user_name = selectUsername()


                checkemail = getUser(studentEmail)
                checkCode = checkLecturerCode(lecturerCode)
                print(checkemail)
                

                if checkemail == True:
                    flash('email already exists.', category='error')
                    print('error checkemail')
                
                elif len(studentEmail) < 8:
                    flash('Email must be greater than 7 characters', category='error')
                    print('error email length')
                
                elif len(studentPassword) < 7:
                    flash('Password must be greater than 7 characters', category='error')
                    print('error password')
                
                elif studentPassword != studentPassword2:
                    flash('Passwords don\'t match', category='error')
                    print('error no match')
                elif checkCode == False:
                    flash('lecturer code does not exist', category='error')
                    print('error, code')
                    
                else:

                    checkUser = checkUsername(user_name)

                    if checkUser == True:
                        randInt = str(random.randint(100, 1000))
                        user_name = user_name + randInt
                    

                    new_user = User(email=studentEmail, password=generate_password_hash(studentPassword, method='sha256'), user_name = user_name, lecturerCode = lecturerCode, lecturerStatus=0)
                    createUser = insertUser(email=studentEmail, password=generate_password_hash(studentPassword, method='sha256'), user_name = user_name, lecturerCode = lecturerCode, lecturerStatus=0)
                    flash('Account created', category='success')
                    login_user(new_user, remember=True) 
                    return redirect(url_for('views.logged_in'))

            if request.form['account-type'] == 'lecturerAccount':
                
                lecturerEmail = request.form.get('lecturer-email')
                lecturerPassword = request.form.get('lecturer-password')
                lecturerPassword2 = request.form.get('lecturer-password2')
                lecturerId = random.randint(100000,999999)  

                checkemail = getUser(lecturerEmail)
                checkCode = checkLecturerCode(lecturerId)

                while checkCode == True:
                    lecturerId = lecturerId + 1
                    checkCode = checkLecturerCode(lecturerId)
            
                if checkemail == True:
                    flash('email already exists.', category='error')
                
                elif len(lecturerEmail) < 8:
                    flash('Email must be greater than 7 characters', category='error')
                
                elif len(lecturerPassword) < 7:
                    flash('Password must be greater than 7 characters', category='error')
                
                elif lecturerPassword != lecturerPassword2:
                    flash('Passwords don\'t match', category='error')
                

                else:
                    new_user = User(email=studentEmail, password=generate_password_hash(lecturerPassword, method='sha256'), user_name = lecturerId, lecturerCode = lecturerCode, lecturerStatus=1)
                    createUser = insertUser(email=studentEmail, password=generate_password_hash(lecturerPassword, method='sha256'), user_name = user_name, lecturerCode = lecturerCode, lecturerStatus=1)
                    flash('Account created', category='success')
                    login_user(new_user, remember=True) 
                    return redirect(url_for('views.logged_in'))
    return render_template("register.html")