from webapp import create_app
from flask import render_template, redirect, url_for, request, Markup
from flask_login import login_user, login_required, current_user
import atexit, json
from datetime import date, datetime
from apscheduler.schedulers.background import BackgroundScheduler
from webapp.utils import timeChange
from dynamodb import getPoints, initialiseGame, loadUser, addHints

application = create_app()

constructKeyValidator = '<div id="keyValidator" onClick="goToKey()"><svg width="229" height="337" viewBox="0 0 229 337" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M1 1H228V336H1V1Z" fill="#A57939"/><path d="M38.8335 32.6017H190.167V133.734H38.8335V32.6017ZM38.8335 228.546H190.167V298.071H38.8335V228.546Z" fill="#6A462F"/><path d="M1 1H228V336H1V1Z" stroke="black" stroke-width="2" stroke-miterlimit="10" stroke-linejoin="round"/><path d="M196.472 184.3C205.179 184.3 212.236 178.64 212.236 171.657C212.236 164.675 205.179 159.014 196.472 159.014C187.766 159.014 180.708 164.675 180.708 171.657C180.708 178.64 187.766 184.3 196.472 184.3Z" fill="black"/><path d="M199.625 203.265H193.319C191.647 203.265 190.043 202.611 188.861 201.448C187.678 200.284 187.014 198.707 187.014 197.061V158.902C187.014 157.257 187.678 155.679 188.861 154.516C190.043 153.352 191.647 152.698 193.319 152.698H199.625C201.297 152.698 202.901 153.352 204.083 154.516C205.266 155.679 205.93 157.257 205.93 158.902V197.055C205.93 198.7 205.266 200.278 204.083 201.442C202.901 202.605 201.297 203.265 199.625 203.265Z" fill="black"/><path d="M38.8335 32.6017H190.167V133.734H38.8335V32.6017ZM38.8335 228.546H190.167V298.071H38.8335V228.546Z" stroke="black" stroke-width="2" stroke-miterlimit="10" stroke-linejoin="round"/></svg>'

# @application.route('/cyberescape')
# @login_required
# def landing():
#     user_points = db.session.query(points.pointsTotal).filter_by(id = current_user.id).first()
#     startGameTime = db.session.query(points.startGameTime).filter_by(id = current_user.id).first()
#     laptopChallenge = db.session.query(laptop_challenge.challengeState).filter_by(user_id = current_user.id).first()
#     phoneChallenge = db.session.query(phone_challenge.challengeState).filter_by(user_id = current_user.id).first()
#     serverChallenge = db.session.query(server_challenge.challengeState).filter_by(user_id = current_user.id).first()
#     if user_points:
#         userPoints = user_points[0]
#         startTime = startGameTime[0]
#         timePassed = timeChange(startTime)
#         timeLeft = 86400 - timePassed
#         userTimeChange = points.query.get_or_404(current_user.id)
#         userTimeChange.timeLeft = timeLeft
#         db.session.commit()
#     else:
#         userPoints = 100
#         timeLeft = 86400
#         new_user_points = points(id = current_user.id, pointsTotal = 0, startGameTime = datetime.now())
#         new_splunk_state = splunk_challenges(user_id = current_user.id, challengeState = 0, key_one = 0, key_two = 0, key_three = 0 )
#         db.session.add(new_splunk_state)
#         db.session.add(new_user_points)
#         db.session.commit()

#     if(laptopChallenge and phoneChallenge and serverChallenge):
#         if(laptopChallenge[0] == 4 and phoneChallenge[0] == 3 and serverChallenge[0] == 4):
#             keyValidator = Markup(constructKeyValidator)
#             return render_template('cyberescape.html', user=current_user, userPoints = userPoints, userTime = timeLeft, keyValidator = keyValidator)
    
#     return render_template('cyberescape.html', user = current_user, userPoints = userPoints, userTime = timeLeft)

@application.route('/cyberescape')
@login_required
def landing():
    user_points = getPoints(current_user.id)
    if int(user_points) <= 0:
        userPoints= 100
        initialiseGame(current_user.id, str(userPoints), str(datetime.now()))
        timeLeft = 86400
    else:
        userData = loadUser(current_user.id)
        userPoints = user_points
        timePassed = timeChange(userData[0]['startGameTime'])
        print('timepassed' + str(timePassed))
        timeLeft = 86400 - timePassed
        print(timeLeft)
    return render_template('cyberescape.html', user = current_user, userPoints = userPoints, userTime = timeLeft)


@application.route('/hints')
def hints():
    challengeHints = {
            "hint1" : {
                "name" : "laptopHint",
                "hint": "I am a common hash algorithm prone to collisions."
            },
            "hint2" : {
                "name" : "desktopHint",
                "hint" : "I am in a base with 2^^6"
            },
            "hint3" : {
                "name" : "phoneHint",
                "hint" : "I am used for secure key-exchange"
            },
            "hint4" : {
                "name" : "phoneHomeHint",
                "hint" : "The hint lies in the image"
            },
            "hint5" : {
                "name" : "phoneHomeHint2",
                "hint" : "I am an Advanced Encryption Standard"
            },
            "hint6" : {
                "name" : "serverHint",
                "hint" : "we are Base64 and vigenere ciphers"
            }
    }

    return challengeHints

@application.route('/updateHints/<string:challenge>', methods = ['GET', 'POST'])
def updateHints(challenge):
    if challenge == 'laptopHint' or challenge == 'desktopHint':
        addHints(current_user.id, '1')
    elif challenge == 'phoneHint' or challenge == 'phoneHomeHint' or challenge == 'phoneHomeHint2':
        addHints(current_user.id, '1')
    elif challenge == 'serverHint':
        addHints(current_user.id, '1')
    return 'success', 202


if __name__ == '__main__':
    application.run(debug=True)

   