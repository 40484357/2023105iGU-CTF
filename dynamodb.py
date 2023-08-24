import boto3
from botocore.config import Config
from boto3 import resource
from boto3.dynamodb.conditions import Attr, Key
from botocore.config import Config
from datetime import datetime



boto3.resource('ebs', region_name = 'eu-west-2')

user_table = resource ('dynamodb').Table('Users')

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

def initialiseGame(email, points, startGameTime):
    response = user_table.update_item(
        Key = {'email': email},
        UpdateExpression='SET points= :p, startGameTime= :t, splunkState= :s',
        ExpressionAttributeValues={
            ':p': points,
            ':t': startGameTime,
            ':s': '0'
        },
        ReturnValues='UPDATED_NEW'
    )
    print(response['Attributes'])

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
        FilterExpression = Attr('lecturer_code').eq(code)
    )

    items = response['Items']
    if[items]:
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