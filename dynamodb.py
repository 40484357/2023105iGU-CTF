import boto3
from boto3 import resource
from boto3.dynamodb.conditions import Attr, Key
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask import redirect

resource = resource(
    'dynamodb',
    aws_access_key_id = 'AKIA5FBZYB2GS6TYFVXG',
    aws_secret_access_key= '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',
    region_name = 'eu-west-2'
)



user_table = resource.Table('Users')

scores_table = resource.Table('GameScores')

def insertUser(email, password, user_name, lecturerCode, lecturerStatus):
    response = user_table.put_item(
        Item={
            'email': email,
            'password': password,
            'user_name': user_name,
            'lecturerCode': lecturerCode,
            'lecturerStatus': lecturerStatus
        }
    )
    return('success')


def getUser(email):
    response = user_table.query(
       KeyConditionExpression=Key('email').eq(email)
    )
    items = response['Items']


    if len(items) > 0:
        return True 
    else: 
        return False

def loadUser(email):
    response = user_table.query(
       KeyConditionExpression=Key('email').eq(email)
    )
    items = response['Items']
    

    if len(items) > 0:
        return items



def getPoints(email):
    try:
        response = user_table.get_item(
            Key={
                'email': email
            },
            ProjectionExpression='points'
        )
        items = response['Item']
        points = items['points']
        return(points)
    except: 
        initialisePoints(email)
        return('0')
    



def initialisePoints(email):
    response = user_table.update_item(
        Key = {
            'email': email
        },
        UpdateExpression='SET points= :s',
        ExpressionAttributeValues={
            ':s': '0'
        },
        ReturnValues='UPDATED_NEW'
    )
    print(response['Attributes'])

def initialiseGame(email, points, startGameTime, attempts):
    response = user_table.update_item(
        Key = {'email': email},
        UpdateExpression='SET points= :p, startGameTime= :t, splunkState= :s, CSI_attempts= :c',
        ExpressionAttributeValues={
            ':p': points,
            ':t': startGameTime,
            ':s': '0',
            ':c': attempts
        },
        ReturnValues='UPDATED_NEW'
    )
    print(response['Attributes'])

def bestScore(email, points, timePassed):
    response = user_table.update_item(
        Key = {'email': email},
        UpdateExpression = 'SET best_csi= :p, best_csi_time= :t',
        ExpressionAttributeValues = {
            ':p': points,
            ':t': timePassed
        }
    )

def checkUsername(username):
    response = user_table.scan(
        FilterExpression=Attr('user_name').eq(username)
    )
    items = response['Items']

    if[items]:
        return(True)
    else:
        return(False)
    
def checkLecturerCode(code):
    response = user_table.scan(
        FilterExpression = Attr('lecturerCode').eq(code)
    )
    print('code is ', code)
    items = response['Items']
    
    if len(items) > 0:
        return(True)
    else:
        return(False)
    
    

def initialiseLaptop(email, password, startTime, challengeState, hints, laptopSelect):
    response = user_table.update_item(
        Key = {'email': email},
        UpdateExpression='SET laptopPassword= :l, challengeStart= :t, laptopState= :s, hints= :h, laptopSelect= :r',
        ExpressionAttributeValues={
            ':l': password,
            ':t': startTime,
            ':s': challengeState,
            ':h': hints,
            ':r': laptopSelect
        },
        ReturnValues='UPDATED_NEW'
    )
    print(response['Attributes'])

def initialisePhone(email, secretKey, a, b, startTime, challengeState, stegSelect):
    response = user_table.update_item(
        Key={'email': email},
        UpdateExpression = 'SET phoneKey= :k, primeA= :a, primeB= :b, challengeStart= :t, phoneState= :s, hints= :h, stegSelect = :r',
        ExpressionAttributeValues={
            ':k': secretKey,
            ':a': a,
            ':b': b,
            ':t': startTime,
            ':s': challengeState,
            ':h': '0',
            ':r': stegSelect
        },
        ReturnValues='UPDATED_NEW'
    )
    print(response['Attributes'])

def initialiseCrypto(email, startTime, challengeState, hints):
    response = user_table.update_item(
        Key = {'email': email},
        UpdateExpression='SET challengeStart= :t, cryptoState= :s, hints= :h',
        ExpressionAttributeValues={
            ':t': startTime,
            ':s': challengeState,
            ':h': hints
        },
        ReturnValues='UPDATED_NEW'
    )

def updateUser(email, challenge, points, state):
    response = user_table.update_item(
        Key = {'email': email},
        UpdateExpression=f'SET points= :p, {challenge}= :c',
        ExpressionAttributeValues = {
            ':p': points,
            ':c': state
        },
        ReturnValues='UPDATED_NEW'
    )
    print('user updated')
    print(response['Attributes'])

def resetChallenge(email, challenge, state, hints, startTime):
    if challenge == 'laptop':
        response = user_table.update_item(
            Key={'email': email},
            UpdateExpression='SET laptopState= :s, challengeStart = :t, hints = :h',
            ExpressionAttributeValues={
                ':s': state,
                ':t': str(startTime),
                ':h': hints
            }
        )
    elif challenge == 'phone':
        response = user_table.update_item(
            Key={'email': email},
            UpdateExpression='SET phoneState= :s, challengeStart = :t, hints = :h',
            ExpressionAttributeValues={
                ':s': state,
                ':t': str(startTime),
                ':h': hints
            }
        )

def resetCSI(email):
    response = user_table.update_item(
        Key={'email': email},
        UpdateExpression = 'REMOVE cryptoState, hints, key_one, key_two, key_three, laptopPassword, laptopSelect, laptopState, phoneKey, points, primeA, primeB, splunkState, phoneState',

    )

def endRoom(email, challenge, state, splunkState, points):
    if challenge == 'laptop':
        response = user_table.update_item(
            Key={'email': email},
            UpdateExpression='SET laptopState= :l, hints = :h, points = :p, splunkState= :s',
            ExpressionAttributeValues={
                ':l': state,
                ':h': '0',
                ':p': points,
                ':s': splunkState
            },
            ReturnValues='UPDATED_NEW'
        )
        print(response['Attributes'])
    elif challenge == 'phone':
        response = user_table.update_item(
            Key={'email': email},
            UpdateExpression='SET phoneState= :l, hints = :h, points = :p, splunkState= :s',
            ExpressionAttributeValues={
                ':l': state,
                ':h': '0',
                ':p': points,
                ':s': splunkState
            },
            ReturnValues='UPDATED_NEW'
        )
        print(response['Attributes'])
    elif challenge == 'crypto':
        response = user_table.update_item(
            Key={'email': email},
            UpdateExpression='SET cryptoState= :l, hints = :h, points = :p, splunkState= :s',
            ExpressionAttributeValues={
                ':l': state,
                ':h': '0',
                ':p': points,
                ':s': splunkState
            },
            ReturnValues='UPDATED_NEW'
        )

def addHints(email, hints):
    response = user_table.update_item(
            Key={'email': email},
            UpdateExpression='SET hints = :h',
            ExpressionAttributeValues={
                ':h': hints
            },
            ReturnValues='UPDATED_NEW'
        )
    print(response['Attributes'])

def updateSplunk(email, state, key, digits):
    response = user_table.update_item(
            Key={'email': email},
            UpdateExpression=f'SET splunkState = :s, {key} = :k ',
            ExpressionAttributeValues={
                ':s': state,
                ':k': digits
            },
            ReturnValues='UPDATED_NEW'
        )
    print(response['Attributes'])

def newScore(user_name, game_name, points, classCode):
    response = scores_table.put_item(
        Item = {
            'user_name': user_name,
            'gamename': game_name,
            'points': points,
            'classCode': classCode
        }
    )
def removeOldScore(user_name, points):
    response = scores_table.delete_item(
        Key={'user_name': user_name, 'points': points}
    )




def getScores():
        response = scores_table.query(
            IndexName = 'gamename-points-index',
            KeyConditionExpression = Key('gamename').eq('overall'),
            ScanIndexForward = False

        )
        items = response['Items']
        return(items)

def getUserScores(user_name):
        response = scores_table.query(
            KeyConditionExpression = Key('user_name').eq(user_name),
            ScanIndexForward = False

        )
        items = response['Items']
        items = items[0]['points']
        return(items)





def updateUserDetails(email, newClass, newPass, newMail):
    if len(newPass) > 7:
        newPass = generate_password_hash(newPass, method='sha256')
        response = user_table.update_item(
            Key = {'email': email},
            UpdateExpression=f'SET  password = :P',
            ExpressionAttributeValues = {
            ':P': newPass
        },
        ReturnValues='UPDATED_NEW'
        )
        

    if newMail:
        if len(newMail) > 7:
            response = user_table.update_item(
                Key = {'email': email},
                UpdateExpression= f'SET email = :E',
                ExpressionAttributeValues = {
                ':E': newMail
            },
            )
        

    
    if len(newClass) > 3:
        response = user_table.update_item(
            Key = {'email': email},
            UpdateExpression= f'SET lecturerCode = :l',
            ExpressionAttributeValues = {
            ':l': newClass
        },
     )
        
    