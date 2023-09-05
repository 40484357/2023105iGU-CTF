from flask import Blueprint, render_template, request, redirect, url_for, flash
import hashlib, random, time, math, pandas as pd
from flask_login import login_user, login_required, current_user
from datetime import date, datetime
from .utils import timeChange, pointsLogic, splunk_markup, base65Set, stegSet
from flask import Blueprint, render_template, request, redirect, url_for, flash, Markup
from dynamodb import getPoints, loadUser, initialiseLaptop, updateUser, resetChallenge, endRoom, initialisePhone, updateSplunk, initialiseCrypto, getScores, updateUserDetails
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

# List of passwords for web challenge
ccPasswords = ["'pass1234' or 1=1--","'pass1234' or 1=1","'pass1234' or 1=1 #","'pass1234' or true--","'pass1234' or true-- +","'pass1234' OR ‘’ = ‘","'pass1234' OR 'x'='x","'pass1234' or '1'='1'/*",
             "'pass1234' OR 1=1 LIMIT 1--","'pass1234' or 1=1 LIMIT 1#","'pass1234' or true LIMIT 1--","'pass1234' or true LIMIT 1#"]

# Creating a dictionary of wallet addresses and their corresponding flags
walletAddressDict = {
    "aW5zdGFsbC1wbHVnaW4=" : "install-plugin",
    "InBocD98Ig==" : "\"php?|\"",
    "ImV0Yy9wYXNzd2Qi" : "\"etc/passwd\"",
    "Ii9ldGMvcGFzc3dkIg==" : "\"/etc/passwd\"",
    "Ki50eHQ=" : "*.txt"
}

# Can use this to get the randomly selected address, keep the pair to validate later
walletAddressPair = random.choice(list(walletAddressDict.items()))
walletAddress = walletAddressPair[0]
print(walletAddress)

# Truncate the address with an elipsis to hide it in web challenge 2
hiddenWalletAddress = walletAddress[:4]+"..."+walletAddress[-4:]

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
        laptopSelect = random.randint(0, 4)
        initialiseLaptop(current_user.id, passkey, str(startTime), challengeState, hints, laptopSelect)

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
            startTime = userData[0]['challengeStart']
            hints = userData[0]['hints']
            points = userData[0]['points']
            newPoints = pointsLogic(startTime, hints, points)
            updateUser(current_user.id, 'laptopState', str(newPoints), str(challengeState))
            return redirect('/desktop')

    return render_template('laptop.html', password = password.hexdigest(), response = response)


@views.route('/desktop', methods=['GET', 'POST'])
def desktop():
    completed = 'false'
    userData = loadUser(current_user.id)
    challengeSelection = int(userData[0]['laptopSelect'])
    ip = base65Set[challengeSelection]['IP']
    code = base65Set[challengeSelection]['code']
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

    return render_template('desktop.html', completed = completed, code=code)


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
        stegSelect = random.randint(0, 4)
        a = prime1 #variable
        b = prime2 #variable
        A = pow(G,a) % N
        B = pow(G,b) % N
        secretKey = pow(B,a) % N
        print("A: ", A)
        print("B: ", B)
        print("Secret Key: ", secretKey)
        initialisePhone(current_user.id, secretKey, a, b, str(startTime), '1', stegSelect)
        
    
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
    challengeSelection = int(userData[0]['stegSelect'])
    stegImageRoute = stegSet[challengeSelection]['image']
    stegHash = stegSet[challengeSelection]['stegHash']
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
            if request.form['validatePhoto'] != stegHash:
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
            if request.form['password'] != stegSet[challengeSelection]['hash']:
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

    return render_template('phoneHome.html', aesState = aesState, hint = hint, stegImageRoute = stegImageRoute)     

@views.route('/server')
def server():
    return render_template('server.html')

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
        challengeSelection = int(userData[0]['laptopSelect'])
        answer = base65Set[challengeSelection]['answer']
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
            challengeSelection = int(userData[0]['laptopSelect'])
            answerSelect = base65Set[challengeSelection]['answer']
            if request.form['challenge_one'] != answerSelect:
                return render_template('splunk.html', response = response, message = message)
            else:
                new_digits = '63'
                if int(splunkState) < 2:
                    state =2
                else: 
                    state = splunkState
                    print('state is ' + state)
                key = 'key_one'
                updateSplunk(current_user.id, state, key, new_digits)
                getMarkUp = splunk_markup(int(state))
                response = Markup(getMarkUp)

        elif "challenge_two" in request.form:
            challengeSelection = int(userData[0]['stegSelect'])
            answerSelect = stegSet[challengeSelection]['answer']
            if request.form['challenge_two'] != answerSelect:
                print('wrong answer')
                return render_template('splunk.html', response = response, message = message)
            else:
                new_digits = '34'
                if int(splunkState)<4:
                    state = 4
                else:
                    state = int(splunkState)
                key = 'key_two'
                updateSplunk(current_user.id, state, key, new_digits)
                getMarkUp = splunk_markup(state)
                response = Markup(getMarkUp)       
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
               

    
    return render_template('splunk.html', response = response)

# @views.route('/leaderboard')
# def leaderBoard():
#     leaders = db.session.query(users.user_name, points.pointsTotal).join(points).order_by(points.pointsTotal.desc()).all()
#     user = db.session.query(users.user_name).filter_by(id = current_user.id).first()
#     userPoints = db.session.query(points.pointsTotal).filter_by(id = current_user.id).first()
#     index = 0
#     for index, item in enumerate(leaders):
#         if user[0] == item[0]:
#             leaderLength = round(len(leaders) / 2)
#             del leaders[-leaderLength:]
#             userName = user[0]
#             userpoints = userPoints[0]
#             return render_template('leaderboard.html', leaders=leaders, index = index, userName = userName, userpoints = userpoints)

@views.route('/')
def landing():
    if current_user.is_authenticated:
        return redirect(url_for('views.logged_in'))
    else:
        return render_template('home.html')

        

    return render_template('loggedhome.html',user_name=current_user.user_name)

@views.route('/Database_Result')
def results():
        return render_template('Database_Result.html', values=users.query.all())

@views.route('/resources')
def resources():
    return render_template('resources.html')

# Web challenge 1
@views.route('/cryptocartel' , methods=['GET','POST'])
def cryptocartel():
    response = None
    userData = loadUser(current_user.id)
    challengeState = '1'
    try: 
        challengeState = userData[0]['cryptoState']
    except:
        startTime = datetime.now()
        initialiseCrypto(current_user.id, str(startTime), challengeState, '0')
    
    if int(challengeState) == 2:
        return redirect('/cryptocartel/loggedin')
    elif int(challengeState) == 3:
        return redirect('/cryptocartel/loggedin/txn')
    if request.method=='POST':
        # Check if user enters admin + any of the passwords
        if request.form['ccUsername'] == "admin" and request.form['ccPassword'] in ccPasswords:
            challengeState = 2
            userData = loadUser(current_user.id)
            startTime = userData[0]['challengeStart']
            hints = userData[0]['hints']
            points = userData[0]['points']
            newPoints = pointsLogic(startTime, hints, points)
            updateUser(current_user.id, 'cryptoState', str(newPoints), str(challengeState))
            return redirect('/cryptocartel/loggedin')
        else:
            response = 'Incorrect username or password, please try again.'
            flash(response)
    return render_template('web_chall.html')  

# Web challenge 2
@views.route('/cryptocartel/loggedin' , methods=['GET','POST'])
def cryptocartel_loggedin():
    response = None
    userData = loadUser(current_user.id)
    state = int(userData[0]['cryptoState'])

    if(state == 1):
        return redirect('/cryptocartel')
    elif(state == 3):
        return redirect('/cryptocartel/loggedin/txn')
    else:
        hints = '0'
        startTime = datetime.now()
        initialiseCrypto(current_user.id, str(startTime), state, hints)

    if request.method =='POST':
        if "script" in request.form:
            if(request.form['ccScript'] == "<img src=x oneerror=alert(document.cookie)>"):
                response = "Session ID = tcbd7x3q8k1690833065130"
                flash(response)
                return render_template('web_chall_2.html',hiddenWalletAddress = hiddenWalletAddress)
        elif "session" in request.form:
            if(request.form['ccSession']== "tcbd7x3q8k1690833065130"):
                userData = loadUser(current_user.id)
                challengeState = 3
                startTime = userData[0]['challengeStart']
                hints = userData[0]['hints']
                points = userData[0]['points']
                newPoints = pointsLogic(startTime, hints, points)
                updateUser(current_user.id, 'cryptoState', str(newPoints), str(challengeState))
                return redirect('/cryptocartel/loggedin/txn')
    return render_template('web_chall_2.html',hiddenWalletAddress = hiddenWalletAddress)

#These routes can be changed, couldn't really think of better names
# The wallet address will be the random part of the challenge.
# Web challenge 3
@views.route('/cryptocartel/loggedin/txn' , methods=['GET','POST'])
def cryptocartel_loggedin_txn():
    response = None
    userData = loadUser(current_user.id)
    state = int(userData[0]['cryptoState'])
    if(state == 1):
        return redirect('/cryptocartel')
    elif(state == 2):
        return redirect('/cryptocartel/loggedin')
    else:
        hints = '0'
        startTime = datetime.now()
        initialiseCrypto(current_user.id, str(startTime), state, hints)
    if request.method =='POST':
        if(request.form['ccTxn']==walletAddressPair[1]):
            response = Markup("Well done. Now use this flag in <a href ='/splunk' target='_blank'>Splunk</a>.")
            flash(response)
            if (state == 3):
                userData = loadUser(current_user.id)
                challengeState = 4
                startTime = userData[0]['challengeStart']
                hints = userData[0]['hints']
                points = userData[0]['points']
                newPoints = pointsLogic(startTime, hints, points)
                endRoom(current_user.id, 'crypto', str(challengeState), '5', newPoints)
            return render_template('web_chall_3.html', walletAddress = walletAddress, hiddenWalletAddress = hiddenWalletAddress)
        else:
            response = "Thank you for the feedback."
            flash(response)
            return render_template('web_chall_3.html', walletAddress = walletAddress, hiddenWalletAddress = hiddenWalletAddress)
    return render_template('web_chall_3.html', walletAddress = walletAddress, hiddenWalletAddress = hiddenWalletAddress)

@views.route('/logged_in', defaults={'selection': 'global'}, methods = ['GET','POST'])
@views.route('/logged_in/<string:selection>', methods = ['GET','POST'])
def logged_in(selection):
    userData = loadUser(current_user.id)
    username = userData[0]['user_name']
    scores = getScores()
    userclass = userData[0]['lecturerCode']
    classScores =[]
    classrank = 'n/a'
    globalrank = 'n/a'
    rank = 'n/a'
    try:
        CSI_attempts = userData[0]['CSI_attempts']
    except:
        CSI_attempts = 0
    try:
        best_csi = userData[0]['best_csi']
        best_csi_time = userData[0]['best_csi_time=']
    except:
        best_csi = 'n/a'
        best_csi_time = 'n/a'
    for x, value in enumerate(scores):
            print(value['user_name'])
            if value['user_name'] == username:
                points = value['points']
                globalrank = x + 1
                rank = x+1
            else:
                try:
                    points = userData[0]['points']
                except: 
                    points = 0
    for x in scores:
            if userclass == x['classCode']:
                classScores.append(x)
    
    for x, value in enumerate(classScores):
        if value['user_name'] == username:
                points = value['points']
                classrank = x + 1
        else:
                classrank = 'n/a'
                try:
                    points = userData[0]['points']
                except: 
                    points = 0

    if selection == 'Class':
        scores = classScores
        for x, value in enumerate(scores):
             if value['user_name'] == username:
                points = value['points']
                rank = classrank
            
    if request.method == 'POST':
        newClass = request.form.get('class')
        newClass2 = request.form.get('class2')
        newPass = request.form.get('password')
        newPass2 = request.form.get('password2')
        newMail = request.form.get('email')
        newMail2 = request.form.get('email2')
        if newClass == newClass2 or str(newPass) == str(newPass2) or str(newMail) == str(newMail2):
            updateUserDetails(current_user.id, newClass, newPass, newMail)
            if len(newPass) > 7 or len(newMail)>7:
                return redirect('/logout')

    return render_template('new-login-screen.html', username = username, scores = scores, rank = rank, globalrank = globalrank, classrank = classrank, points = points, CSI_attempts = CSI_attempts, best_csi = best_csi, best_csi_time = best_csi_time)