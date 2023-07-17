from flask import Blueprint, render_template, request, redirect, url_for, flash
import hashlib, random, time, math, pandas as pd
from . import db
from flask_login import login_user, login_required, current_user
from .models import users, phone_challenge, laptop_challenge, server_challenge, points, splunk_challenges
from datetime import date, datetime
from .utils import timeChange, pointsLogic, splunk_markup
from flask import Blueprint, render_template, request, redirect, url_for, flash, Markup
from dynamodb import getPoints, loadUser, initialiseLaptop, updateUser, resetChallenge, endRoom, initialisePhone, updateSplunk
import hashlib, random, time, webbrowser
passwords = []
with open('cyberA-Z.txt') as f:
    words = f.readlines()
    passwords = [x.strip().lower() for x in words]


# Diffie-Hellman Key Exchange start
N = 604931 
G = 30672

# List of potential a and b values
possibleValues = [503, 521, 541, 557, 563, 613, 631, 641, 653, 661]
    
# Need to select two random unique values from the list
possibleValuesLength = len(possibleValues) - 1
primeSelection1 = random.randint(0, possibleValuesLength)
prime1 = possibleValues[primeSelection1]

# Remove the first value from the list and decrease the length of the list by 1
possibleValues.pop(primeSelection1)
possibleValuesLength -= 1

# Select the second value from the list
primeSelection2 = random.randint(0, possibleValuesLength)
prime2 = possibleValues[primeSelection2]
    
a = prime1 #variable
b = prime2 #variable
A = pow(G,a) % N
B = pow(G,b) % N
secretKey = pow(B,a) % N
print("A: ", A)
print("B: ", B)
print("Secret Key: ", secretKey)

views = Blueprint('views', __name__)


@views.route('/laptop', methods=['GET', 'POST'])
def laptop():
    userData = loadUser(current_user.id)

    try:
        passkey = userData[0]['laptopPassword']
        print(passkey)
        challengeState = userData[0]['laptopState']
    except:
        passLen = len(passwords) - 1
        selection = random.randint(0, passLen)
        passkey = passwords[selection]
        startTime = datetime.now()
        challengeState = '1'
        hints = '0'
        initialiseLaptop(current_user.id, passkey, str(startTime), challengeState, hints)

    password = hashlib.md5(passkey.encode())
    response = None

    if int(challengeState) > 1:
        return redirect('/desktop')

    if request.method=='POST':
        if request.form['answer'] != passkey:
            response = 'wrong password, try again'
            flash(response)
        else:
            challengeState = 2
            userData=loadUser(current_user.id)
            startTime = userData[0]['laptopStart']
            hints = userData[0]['hints']
            points = userData[0]['points']
            newPoints = pointsLogic(startTime, hints, points)
            updateUser(current_user.id, 'laptopState', str(newPoints), str(challengeState))
            return redirect('/desktop')

    return render_template('laptop.html', password = password.hexdigest(), response = response)


@views.route('/desktop', methods=['GET', 'POST'])
def desktop():
    ip = "85.50.46.53"
    completed = 'false'
    userData = loadUser(current_user.id)
    state = int(userData[0]['laptopState'])
    if(state == 1):
        return redirect('/laptop')
    elif(state == 3):
        startTime = datetime.now()
    elif(state == 4):
        response = "That's the IP, but where does it go? " + ip
        completed = 'true'
        flash(response)
        return render_template('desktop.html', response = response, completed = completed)
    else:
        challengeState = '3'
        hints = '0'
        startTime = datetime.now()
        challenge = 'laptop'
        resetChallenge(current_user.id, challenge, challengeState, hints, startTime)
        

    response = None
    if request.method == 'POST':
        if request.form['answer'] != ip:
            response = 'not quite try again'
            flash(response)
            return render_template('desktop.html', response = response)
            
        else:
            userData=loadUser(current_user.id)
            response = "That's the IP, but where does it go? " + ip
            completed = 'true'
            if(state ==3):
                points = userData[0]['points']
                state = '4'
                hints = userData[0]['hints']
                newPoints = pointsLogic(str(startTime), hints, points)
                splunkState = '1'
                endRoom(current_user.id, 'laptop', state, splunkState, newPoints)
            flash(response)
            return render_template('desktop.html', response = response, completed = completed)

    return render_template('desktop.html', completed = completed)


@views.route('/phone', methods=['GET','POST'])
def phone():
    response = None
    userData = loadUser(current_user.id)
    challengeState=1
    try:
        secretKey = userData[0]['phoneKey']
        a=userData[0]['primeA']
        b=userData[0]['primeB']
        challengeState = userData[0]['phoneState']
        print("Secret Key: ", secretKey)
    except:
        possibleValuesLength = len(possibleValues) - 1
        primeSelection1 = random.randint(0, possibleValuesLength)
        prime1 = possibleValues[primeSelection1]
        possibleValues.pop(primeSelection1)
        possibleValuesLength -= 1
        primeSelection2 = random.randint(0, possibleValuesLength)
        prime2 = possibleValues[primeSelection2]
        startTime = datetime.now()
        a = prime1 #variable
        b = prime2 #variable
        A = pow(G,a) % N
        B = pow(G,b) % N
        secretKey = pow(B,a) % N
        print("A: ", A)
        print("B: ", B)
        print("Secret Key: ", secretKey)
        initialisePhone(current_user.id, secretKey, a, b, str(startTime), '1')
        
    
    if int(challengeState) >= 2:
        return redirect('/phoneHome')

    if request.method=='POST':
        secretKeyGuess=request.form.get('answer', type=int)
        if secretKeyGuess != secretKey:
            response = 'wrong password, try again'
            flash(response)
        else:
            userData=loadUser(current_user.id)
            points = userData[0]['points']
            state = '2'
            hints = userData[0]['hints']
            startTime = userData[0]['challengeStart']
            newPoints = pointsLogic(str(startTime), hints, points)
            updateUser(current_user.id, 'phoneState', str(newPoints), state)
            return redirect(url_for('views.phoneHome'))
    
    return render_template('phone.html',password = secretKey,a=a,b=b, response = response)
        

@views.route('/phoneHome',methods =['GET','POST'])
def phoneHome():

    userData = loadUser(current_user.id)
    challengeState = userData[0]['phoneState']
    
    hint = 'phoneHomeHint'
    if (challengeState == 1):
        return redirect('/phone')
    else: 
        startTime = datetime.now()
        hints = '0'
        resetChallenge(current_user.id, 'phone', challengeState, hints, str(startTime))

    aesState = 'false'

    if(int(challengeState) >= 3):
        aesState = 'true'
        hint = 'phoneHomeHint2'
    

    response = None
    # Doing this because of two forms on one view, checks which one was used
    if request.method =='POST':
        if "validater" in request.form:
            if request.form['validatePhoto'] != "U2FsdGVkX18099HHwV0FYWBJXXfd4JDKkrhsHwGeD64=":
                response = 'Incorrect Ciphertext'
                flash(response)
            else:
                # assign chall 2 points, steganography
                
                if(int(challengeState) == 2):
                    print('challengeState ' + challengeState)
                    userData = loadUser(current_user.id)
                    points = userData[0]['points']
                    state = '3'
                    hints = userData[0]['hints']
                    startTime = userData[0]['challengeStart']
                    newPoints = pointsLogic(str(startTime), hints, points)
                    updateUser(current_user.id, 'phoneState', str(newPoints), state)
                    aesState = 'true'
                    hint = 'phoneHomeHint2'
                response = 'Correct Ciphertext.' 
                flash(response)
        elif "aes" in request.form:
            if request.form['password'] != "check_user.php":
                response = 'Incorrect password'
                flash(response)
                print('fail')
            else:
                # assign chall 3 points, aes
                response = Markup("Correct password.<br>Access Splunk <a href ='http://52.1.222.178:8000' target='_blank'>here</a><br>Username: ctf<br>Password: EscapeEscap3")
                if(int(challengeState) == 3):
                    userData = loadUser(current_user.id)
                    points = userData[0]['points']
                    state = '4'
                    hints = userData[0]['hints']
                    startTime = userData[0]['challengeStart']
                    newPoints = pointsLogic(str(startTime), hints, points)
                    splunkState = '3'
                    endRoom(current_user.id, 'phone', state, splunkState, newPoints)
                flash(response)

    return render_template('phoneHome.html', aesState = aesState, hint = hint)     

@views.route('/server')
def server():
    return render_template('server.html')

@views.route('/login_wcg', methods = ['GET', 'POST'])
def login_wcg():
    flag = 'FLAG = http://cyberescape-env-1.eba-pxgmppwm.eu-west-2.elasticbeanstalk.com/static/robots.txt, view this page source in new browser tab for next challenge'
    redir = "false"
    challenge3 = 'false'
    challengeText = ""
    challengeText2 = ""
    name = request.cookies.get('user')
    challengeState = db.session.query(server_challenge.challengeState).filter_by(user_id = current_user.id).first()
    if(challengeState[0] == 1):
        return redirect('/wickedcybergames')
    elif(challengeState[0] == 3 and name == 'admin'):
        challengeText = ['admin permissions verified', 'please validate the flag']
        challengeText2 = ['http://cyberescape-env-1.eba-pxgmppwm.eu-west-2.elasticbeanstalk.com/static/cookie_admin.txt']
        challenge3 = 'true'
        response = 'verifying admin permissions'
        userChallenge = server_challenge.query.get_or_404(current_user.id)
        userChallenge.challengeState = 4
        db.session.commit()
        return render_template('login_wcg.html', flag = flag, redir = redir, challengeText = challengeText,  challengeText2 = challengeText2, challenge3 = challenge3)
    elif(challengeState[0] == 3):
        print(name)
        response = 'verify admin permissions... press enter to continue'
        challengeText = ['Admin not verified...','cookie user type None', 'Please verify admin state and refresh to continue']
        flash(response)
        redir = "true"
        return render_template('login_wcg.html', flag = flag, response = response, redir = redir, challengeText = challengeText, challenge3 = challenge3, challengeText2 = challengeText2)
    else:
        userChallenge = server_challenge.query.get_or_404(current_user.id)
        userChallenge.startTime = datetime.now()
        userChallenge.hints = 0
        db.session.commit()
    
    if request.method == 'POST':
        if request.form['flag_response'] == 'install-':
            response = 'flag found, verify admin permissions... press enter to continue'
            answer = request.form['flag_response']
            challengeText = ['Admin not verified...','Checking cookie state...','user type None...' , 'Error: Inspect cookie, user value should be admin', 'Please verify admin state and refresh']
            flash(response)
            flash("FLAG = " + answer)
            redir = "true"
            userChallenge = server_challenge.query.get_or_404(current_user.id)
            userPoints = points.query.get_or_404(current_user.id)
            newPoints = pointsLogic(server_challenge)
            userPoints.pointsTotal = newPoints #add new points total to DB
            userChallenge.startTime = datetime.now()
            userChallenge.hints = 0
            userChallenge.challengeState = 3
            db.session.commit()
            return render_template('login_wcg.html', flag = flag, response = response, answer = answer, redir = redir, challengeText = challengeText, challengeText2 = challengeText2, challenge3 = challenge3)
        elif request.form['flag_response'] == 'plugin':
            response = 'flag found, press enter to continue'
            challengeText = ['Flag: install-plugin', 'continue to splunk with flags', 'splunk link']
            flash(response)
            redir = 'true'
            userChallenge = server_challenge.query.get_or_404(current_user.id)
            userPoints = points.query.get_or_404(current_user.id)
            newPoints = pointsLogic(server_challenge)
            userPoints.pointsTotal = newPoints #add new points total to DB
            userChallenge.startTime = datetime.now()
            userChallenge.challengeState = 4
            splunkChallengeState = splunk_challenges.query.get_or_404(current_user.id)
            splunkChallengeState.challengeState = 5
            db.session.commit()
            return render_template('login_wcg.html', redir = redir, flag = flag, response = response, challenge3 = challenge3, challengeText = challengeText, challengeText2 = challengeText2)
        else: 
            response = 'incorrect flag, keep looking'
            answer = request.form['flag_response']
            print(answer)
            flash(response)
            flash(answer)
            return render_template('login_wcg.html', flag = flag, response = response, answer = answer, challengeText = challengeText, challengeText2 = challengeText2)

    return render_template('login_wcg.html', flag = flag, redir = redir, challenge3 = challenge3, challengeText = challengeText, challengeText2 = challengeText2)


@views.route('/wickedcybergames' , methods=['GET','POST'])
def wickedcybergames():
    challengeState = db.session.query(server_challenge.challengeState).filter_by(user_id = current_user.id).first()
    if(challengeState):
        if(challengeState[0] == 1):
            userChallenge = server_challenge.query.get_or_404(current_user.id)
            userChallenge.startTime = datetime.now()
            db.session.commit()
        elif(challengeState[0] == 2 | 3):
            return redirect('/login_wcg')
        elif(challengeState[0] == 4):
            return redirect('/login_wcg')
    else:
        new_server_challenge = server_challenge(user_id = current_user.id, challengeState = 1, startTime = datetime.now(), hints = 0)
        db.session.add(new_server_challenge)
        db.session.commit()

    response = None
    if request.method == 'POST':
        if request.form['username'] == 'admin':
            if request.form['password'] == 'IloveWickedGames2023':
                userChallenge = server_challenge.query.get_or_404(current_user.id)
                userPoints = points.query.get_or_404(current_user.id)
                newPoints = pointsLogic(server_challenge)
                userPoints.pointsTotal = newPoints #add new points total to DB
                userChallenge.startTime = datetime.now()
                userChallenge.hints = 0
                userChallenge.challengeState = 2
                db.session.commit()
                return redirect('/login_wcg')
            else: 
                response = 'wrong password'
        else: 
            response = 'wrong username'
            flash(response)
            return render_template('wickedcybergames.html', response = response)


    return render_template('wickedcybergames.html')

# @views.route('/intro')
# @login_required
# def intro():
#     user_points = db.session.query(points.pointsTotal).filter_by(id = current_user.id).first()
#     if user_points:
#         return redirect('/cyberescape')
#     return render_template('intro.html')

@views.route('/intro')
@login_required
def intro():
    print('current user is ' + current_user.id)
    user_points = getPoints(current_user.id)
    user_points = int(user_points)
    if user_points > 0:
        return redirect('/cyberescape')
    else:
        return render_template('intro.html')

@views.route('/winroom', methods=['GET', 'POST'])
def winroom():
    response = None
    if request.method=='POST':
        code1=request.form.get('code1',type=int)
        code2=request.form.get('code2',type=int)
        code3=request.form.get('code3',type=int)
        if(code1==63 and code2==34 and code3==11):
            response = Markup("Correct code<br>Congratulations!")
            flash(response)
            return render_template('winroom.html',flash_message="True")
        else:
            response = 'Incorrect code'
            flash(response)
        
    return render_template('winroom.html',flash_message="False")
@views.route('/splunk', methods = ['GET', 'POST'])
def splunkKey():
    userData = loadUser(current_user.id)
    splunkState = userData[0]['splunkState']
    response = None
    message = Markup('<div class="splunk_challenges">wrong answer, look again</div>')

    if(int(splunkState) == 0):
        getMarkUp = splunk_markup(0)
        response = Markup(getMarkUp)
    elif(int(splunkState) == 1):
        getMarkUp = splunk_markup(1)
        response = Markup(getMarkUp)
    elif(int(splunkState)== 2):
        getMarkUp = splunk_markup(2)
        response = Markup(getMarkUp)
    elif(int(splunkState) ==3):
        getMarkUp = splunk_markup(3)
        response = Markup(getMarkUp)
    elif(int(splunkState) == 4):
        getMarkUp =splunk_markup(4)
        response = Markup(getMarkUp)
    elif(int(splunkState) == 5):
        getMarkUp = splunk_markup(5)
        response = Markup(getMarkUp)
    elif(int(splunkState) == 6):
        getMarkUp = splunk_markup(6)
        response = Markup(getMarkUp)

    if request.method == 'POST':
        if "challenge_one" in request.form:
            if request.form['challenge_one'] != '17':
                
                return render_template('splunk.html', response = response, message = message)
            else:
                new_digits = '63'
                state = '2'
                key = 'key_one'
                updateSplunk(current_user.id, state, key, new_digits)
                getMarkUp = splunk_markup(2)
                response = Markup(getMarkUp)
        elif "challenge_two" in request.form:
            if request.form['challenge_two'] != '1=1--':
                print('wrong answer')
                return render_template('splunk.html', response = response, message = message)
            else:
                new_digits = '34'
                state = '4'
                key = 'key_two'
                updateSplunk(current_user.id, state, key, new_digits)
                getMarkUp = splunk_markup(4)
                response = Markup(getMarkUp)
                db.session.commit()
        elif "challenge_three" in request.form:
            if request.form['challenge_three'] != 'File-manager':
                return render_template('splunk.html', response = response, message = message)
            else:
                new_digits = '11'
                state = '6'
                key = 'key_three'
                updateSplunk(current_user.id, state, key, new_digits)
                getMarkUp = splunk_markup(6)
                response = Markup(getMarkUp)
                db.session.commit()

    
    return render_template('splunk.html', response = response)

@views.route('/leaderboard')
def leaderBoard():
    leaders = db.session.query(users.user_name, points.pointsTotal).join(points).order_by(points.pointsTotal.desc()).all()
    user = db.session.query(users.user_name).filter_by(id = current_user.id).first()
    userPoints = db.session.query(points.pointsTotal).filter_by(id = current_user.id).first()
    index = 0
    for index, item in enumerate(leaders):
        if user[0] == item[0]:
            leaderLength = round(len(leaders) / 2)
            del leaders[-leaderLength:]
            userName = user[0]
            userpoints = userPoints[0]
            return render_template('leaderboard.html', leaders=leaders, index = index, userName = userName, userpoints = userpoints)

@views.route('/')
def landing():
    if current_user.is_authenticated:
        return redirect(url_for('views.logged_in'))
    else:
        return render_template('index.html')

@views.route('/logged_in', methods = ['GET', 'POST'])
@login_required
def logged_in():
    if request.method == 'POST':
        if request.form['code'] == 'Submit':

            lecturerCode2 = request.form.get('student-code2')
            codeCheck = users.query.filter_by(lecturerId=lecturerCode2).first()

            if codeCheck == None:
                flash('Code does not exist.', category='error')
                lecturerCode2=None

            current_user.lecturerCode = lecturerCode2
            db.session.commit()

        if request.form['code'] == 'Leave':
            current_user.lecturerCode = None
            db.session.commit()
        

    return render_template('loggedhome.html',user_name=current_user.user_name)

@views.route('/Database_Result')
def results():
        return render_template('Database_Result.html', values=users.query.all())

@views.route('/resources')
def resources():
    return render_template('resources.html')
    