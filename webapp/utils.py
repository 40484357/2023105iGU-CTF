from datetime import date, datetime
from flask_login import current_user, UserMixin
from dynamodb import loadUser


def timeChange(startTime):
    currTime = datetime.now()
    convertedTime  = datetime.strptime(startTime, '%Y-%m-%d %H:%M:%S.%f')
    timePassed = currTime - convertedTime
    timePassedS = timePassed.seconds
    print('timepassed ' + str(timePassed))
    return timePassedS



def pointsLogic(time, hints, points):
    
    basePoints = 50
    #timeTaken = timeChange(userTime)
    timeTaken = timeChange(time)
    penalty = 0
    
    if(timeTaken > 300 and timeTaken < 1200):
         penalty += 10
    elif (timeTaken > 1200):
        penalty += 20
    if(int(hints) == 1):
            penalty += 10
    elif(int(hints) >= 2):
        penalty += 20

    basePoints -= penalty

    newPoints = int(points) + basePoints
    return(newPoints)


def splunk_markup(key):
    key_0 = '<div class = "splunk_instructions"><div class="locked">You have not unlocked the necessary flags to complete Splunk challenges, return to the evidence and obtain the flags required</div></div>'
    key_1 ='<div class="splunk_instructions"><div class="link">Follow this link to access the splunk server: <a href="http://52.1.222.178:8000" target="_blank">http://52.1.222.178:8000</a></div><div class="username">Username: ctf</div><div class="password">Password: EscapeEscap3</div><div class="setUp"><p>To set up your splunk follow these instructions</p><ul class="splunk_points"><li>Once logged in click search & report</li><li>Enter: source="ctf_dataset.log"</li><li>Change "last 24 hours" to "All time" on search bar</li><li>Use the flag from the previous question to search and answer the question</li><li>With the correct answer you will unlock a set of digits</li><li>Use these three sets of digits to escape the room</li></ul></div></div>'
    challenge_1 = '<div class="splunk_challenges"><h2>Splunk Challenges</h2><div class="splunk_challenge"><form action="" method="post" class="splunk_form"> <label for="challenge_one">1. How many log entries are there for the malicious actor\'s IP address?</label><input type="text" name="challenge_one" id="challenge_one"><input type = "submit" name = "challange_1" value = "Validate"></form><div></div></div>'
    challenge_1_c = '<div class="splunk_challenges"><h2>Splunk Challenges</h2><div class="splunk_challenge"><div>1. How many log entries are there for the malicious actor\'s IP address?</div><div>Answer:  '
    challenge_2 = '<div class="splunk_challenge"><form action="" method="post" class="splunk_form"><label for="challenge_two">2. '
    challenge_2_c = '<div class="splunk_challenge"><div>2. '
    challenge_3 = '<div class="splunk_challenge"><form action="" method="post" class="splunk_form"> <label for="challenge_three">3. Which plug-in was installed and activated by the malicious actor?</label><input type="text" name="challenge_three" id="challenge_three"><input type = "submit" name = "challange_2" value = "Validate"></form></div>'
    challenge_3_c = '<div class="splunk_challenge"><div>3. Which plug-in was installed and activated by the malicious actor?</div><div>Answer: File-manager</div><div class="digits">Key: 11</div></div>'

    userData = loadUser(current_user.id)
    try:
        digitOne = userData[0]['key_one']
    except:
        digitOne = '0'
    try: 
        digitTwo = userData[0]['key_two']
    except:
        digitTwo = '0'
    try: 
        digitThree = userData[0]['key_three']
    except:
        digitThree = '0'

    if key == 0:
        return key_0
    elif key == 1:
        key_1 += challenge_1
        return key_1
    elif key == 2:

        digits = digitOne
        laptopSelect = int(userData[0]['laptopSelect'])
        answer = base65Set[laptopSelect]['answer']
        answerString = answer + '</div><div class="digits">Key: ' + digits + '</div></div></div>'
        key_1 += challenge_1_c 
        key_1 += answerString
        return key_1
    elif key == 3:
        if int(digitOne)> 1:
            digits = digitOne
            laptopSelect = int(userData[0]['laptopSelect'])
            answer = base65Set[laptopSelect]['answer']
            answerString = answer + '</div><div class="digits">Key: ' + digits + '</div></div>'
            phoneSelect = int(userData[0]['stegSelect'])
            question = stegSet[phoneSelect]['splunkChallenge']
            questionString = question + '</label><input type="text" name="challenge_two" id="challenge_two" placeholder="pass = \' or"><input type = "submit" name = "challange_2" value = "Validate"></form></div></div>'
            key_1 += challenge_1_c
            key_1 += answerString
            key_1 += challenge_2
            key_1 += questionString
            return key_1
        else:
            phoneSelect = int(userData[0]['stegSelect'])
            question = stegSet[phoneSelect]['splunkChallenge']
            questionString = question + '</label><input type="text" name="challenge_two" id="challenge_two" placeholder="pass = \' or"><input type = "submit" name = "challange_2" value = "Validate"></form></div></div>'
            key_1 += challenge_1
            key_1 += challenge_2
            key_1 += questionString
            return key_1
    elif key == 4:
        if int(digitOne) > 1:
            laptopSelect = int(userData[0]['laptopSelect'])
            answer = base65Set[laptopSelect]['answer']
            answerString = answer + '</div><div class="digits">Key: ' + digitOne + '</div></div>'
            phoneSelect = int(userData[0]['stegSelect'])
            question = stegSet[phoneSelect]['splunkChallenge']
            answerTwo = stegSet[phoneSelect]['answer']
            answerTwoString = question + '</div><div>Answer: ' + answerTwo + '</div><div class="digits">Key: ' + digitTwo
            key_1 += challenge_1_c
            key_1 += answerString
            key_1 += challenge_2_c
            key_1 += answerTwoString
            return key_1
        else: 
            phoneSelect = int(userData[0]['stegSelect'])
            question = stegSet[phoneSelect]['splunkChallenge']
            answerTwo = stegSet[phoneSelect]['answer']
            answerTwoString = question + '</div><div>Answer: ' + answerTwo + '</div><div class="digits">Key: ' + digitTwo
            key_1 += challenge_1
            key_1 += challenge_2_c
            key_1 += answerTwoString
            return key_1
    elif key == 5:
        if int(digitOne) > 1 and int(digitTwo) > 1:
            laptopSelect = int(userData[0]['laptopSelect'])
            answer = base65Set[laptopSelect]['answer']
            answerString = answer + '</div><div class="digits">Key: ' + digitOne + '</div></div>'
            phoneSelect = int(userData[0]['stegSelect'])
            question = stegSet[phoneSelect]['splunkChallenge']
            answerTwo = stegSet[phoneSelect]['answer']
            answerTwoString = question + '</div><div>Answer: ' + answerTwo + '</div><div class="digits">Key: ' + digitTwo
            key_1 += challenge_1_c
            key_1 += answerString
            key_1 += challenge_2_c
            key_1 += answerTwoString
            key_1 += challenge_3
            return key_1
        elif int(digitOne) > 1:
            digits = digitOne
            laptopSelect = int(userData[0]['laptopSelect'])
            answer = base65Set[laptopSelect]['answer']
            answerString = answer + '</div><div class="digits">Key: ' + digits + '</div></div>'
            phoneSelect = int(userData[0]['stegSelect'])
            question = stegSet[phoneSelect]['splunkChallenge']
            questionString = question + '</label><input type="text" name="challenge_two" id="challenge_two" placeholder="pass = \' or"><input type = "submit" name = "challange_2" value = "Validate"></form></div>'
            key_1 += challenge_1_c
            key_1 += answerString
            key_1 += challenge_2
            key_1 += questionString
            key_1 += challenge_3
            return key_1
        elif int(digitTwo) > 1:
            phoneSelect = int(userData[0]['stegSelect'])
            question = stegSet[phoneSelect]['splunkChallenge']
            answerTwo = stegSet[phoneSelect]['answer']
            answerTwoString = question + '</div><div>Answer: ' + answerTwo + '</div><div class="digits">Key: ' + digitTwo
            key_1 += challenge_1
            key_1 += challenge_2_c
            key_1 += answerTwoString
            key_1 += challenge_3
            return key_1
    elif key == 6:
        if int(digitOne) > 1 and int(digitTwo) > 1:
            laptopSelect = int(userData[0]['laptopSelect'])
            answer = base65Set[laptopSelect]['answer']
            answerString = answer + '</div><div class="digits">Key: ' + digitOne + '</div></div>'
            phoneSelect = int(userData[0]['stegSelect'])
            question = stegSet[phoneSelect]['splunkChallenge']
            answerTwo = stegSet[phoneSelect]['answer']
            answerTwoString = question + '</div><div>Answer: ' + answerTwo + '</div><div class="digits">Key: ' + digitTwo
            key_1 += challenge_1_c
            key_1 += answerString
            key_1 += challenge_2_c
            key_1 += answerTwoString
            key_1 += challenge_3_c
            return key_1
        elif int(digitOne) > 1:
            digits = digitOne
            laptopSelect = int(userData[0]['laptopSelect'])
            answer = base65Set[laptopSelect]['answer']
            answerString = answer + '</div><div class="digits">Key: ' + digits + '</div></div>'
            phoneSelect = int(userData[0]['stegSelect'])
            question = stegSet[phoneSelect]['splunkChallenge']
            questionString = question + '</label><input type="text" name="challenge_two" id="challenge_two" placeholder="pass = \' or"><input type = "submit" name = "challange_2" value = "Validate"></form></div>'
            key_1 += challenge_1_c
            key_1 += answerString
            key_1 += challenge_2
            key_1 += questionString
            key_1 += challenge_3_c
            return key_1
        elif int(digitTwo) > 1:
            phoneSelect = int(userData[0]['stegSelect'])
            question = stegSet[phoneSelect]['splunkChallenge']
            answerTwo = stegSet[phoneSelect]['answer']
            answerTwoString = question + '</div><div>Answer: ' + answerTwo + '</div><div class="digits">Key: ' + digitTwo
            key_1 += challenge_1
            key_1 += challenge_2_c
            key_1 += answerTwoString
            key_1 += challenge_3_c
            return key_1
        

class User(UserMixin):
    def __init__(self, email, user_name, password, lecturerCode, lecturerStatus):
        self.id = email
        self.user_name = user_name
        self.password = password
        self.lecturerCode = lecturerCode
        self.lecturerStatus = lecturerStatus

base65Set=[
    {
        'code': 'UlNBIGVuY3J5cHRpb24gKG5hbWVkIGFmdGVyIHRoZSBpbml0aWFscyBvZiBpdHMgY3JlYXRvcnMgUml2ZXN0LCBTaGFtaXIsIGFuZCBBZGxlbWFuKSBpcyB0aGUgbW9zdCB3aWRlbHkgdXNlZCBhc3ltbWV0cmljIGNyeXB0b2dyYXBoeSBhbGdvcml0aG0uIEJhc2VkIG9uIG1hdGhlbWF0aWNhbCBhbmQgYXJpdGhtZXRpYyBwcmluY2lwbGVzIG9mIHByaW1lIG51bWJlcnMsIGl0IHVzZXMgbGFyZ2UgbnVtYmVycywgYSBwdWJsaWMga2V5IGFuZCBhIHByaXZhdGUga2V5LCB0byBzZWN1cmUgZGF0YSBleGNoYW5nZXMgb24gdGhlIEludGVybmV0LiA8PEZsYWc8PDlkYjUwZGVhMmM2YzNkNGU5N2FhM2FlYzVkZTE2OTBkMTFiMTEwNmY+Pg0K',
        'IP': '85.50.46.53',
        'answer': '17'
    },
    {
        'code': 'SWYgUlNBLTIwNDggd2VyZSB0byBiZSBjcmFja2VkLCB2aXJ0dWFsbHkgYWxsIG9mIHRoZSBJbnRlcm5ldCB3b3VsZCBiZSB1bnRydXN0d29ydGh5LiBDdXJyZW50bHksIG1vc3Qgb2YgdGhlIGRpZ2l0YWwgY2VydGlmaWNhdGVzIHVzZWQgb24gdGhlIEludGVybmV0IGhhdmUgMiwwNDgtYml0IFJTQSBwdWJsaWMga2V5cywgc28gdGhlc2UgY291bGQgYmUgY29tcHJvbWlzZWQgaWYgYnJva2VuLg0KPDxGbGFnPDwzZjhhMTAzNjVmMGFhNDVkZjljZGYyNDkyNDMxNjlhOTdlMjg1NDljPj4NCg==',
        'IP': '78.54.12.66',
        'answer': '14'
    },
    {
        'code': 'TklTVCBkZWZpbmUgQ3liZXJzZWN1cml0eSBhcyBQcmV2ZW50aW9uIG9mIGRhbWFnZSB0bywgcHJvdGVjdGlvbiBvZiwgYW5kIHJlc3RvcmF0aW9uIG9mIGNvbXB1dGVycywgZWxlY3Ryb25pYyBjb21tdW5pY2F0aW9ucyBzeXN0ZW1zLCBlbGVjdHJvbmljIGNvbW11bmljYXRpb25zIHNlcnZpY2VzLCB3aXJlIGNvbW11bmljYXRpb24sIGFuZCBlbGVjdHJvbmljIGNvbW11bmljYXRpb24sIGluY2x1ZGluZyBpbmZvcm1hdGlvbiBjb250YWluZWQgdGhlcmVpbiwgdG8gZW5zdXJlIGl0cyBhdmFpbGFiaWxpdHksIGludGVncml0eSwgYXV0aGVudGljYXRpb24sIGNvbmZpZGVudGlhbGl0eSwgYW5kIG5vbi1yZXB1ZGlhdGlvbi4gPDxGbGFnPDw1NTJkMDMxYTQzMmJjMWUxYjZjYTQ4N2I5ZDczNDRmN2VjNWVmZDk1Pj4NCg==',
        'IP': '68.49.17.11',
        'answer': '10'
    },
    {
        'code': 'U3BsdW5rIGlzIGFuIGFkdmFuY2VkIGFuZCBzY2FsYWJsZSBmb3JtIG9mIHNvZnR3YXJlIHRoYXQgaW5kZXhlcyBhbmQgc2VhcmNoZXMgZm9yIGxvZyBmaWxlcyB3aXRoaW4gYSBzeXN0ZW0gYW5kIGFuYWx5emVzIGRhdGEgZm9yIG9wZXJhdGlvbmFsIGludGVsbGlnZW5jZS4gVGhlIHNvZnR3YXJlIGlzIHJlc3BvbnNpYmxlIGZvciBzcGx1bmtpbmcgZGF0YSwgd2hpY2ggbWVhbnMgaXQgY29ycmVsYXRlcywgY2FwdHVyZXMsIGFuZCBpbmRleGVzIHJlYWwtdGltZSBkYXRhLCBmcm9tIHdoaWNoIGl0IGNyZWF0ZXMgYWxlcnRzLCBkYXNoYm9hcmRzLCBncmFwaHMsIHJlcG9ydHMsIGFuZCB2aXN1YWxpemF0aW9ucy4gVGhpcyBoZWxwcyBvcmdhbml6YXRpb25zIHJlY29nbml6ZSBjb21tb24gZGF0YSBwYXR0ZXJucywgZGlhZ25vc2UgcG90ZW50aWFsIHByb2JsZW1zLCBhcHBseSBpbnRlbGxpZ2VuY2UgdG8gYnVzaW5lc3Mgb3BlcmF0aW9ucywgYW5kIHByb2R1Y2UgbWV0cmljcy4gPDxGbGFnPDxlYTg0NGQyMjVkMjI2NzQ3YjViNDQ5MzIxOWNhNDM0YjZkYWE0ZDE4Pj4NCg0K',
        'IP': '31.16.19.41',
        'answer': '9'
    },
    {
        'code': 'QWR2YW5jZWQgRW5jcnlwdGlvbiBTdGFuZGFyZCwgaXMgYSBzeW1tZXRyaWMgdHlwZSBvZiBlbmNyeXB0aW9uLCBhcyBpdCB1c2VzIHRoZSBzYW1lIGtleSB0byBib3RoIGVuY3J5cHQgYW5kIGRlY3J5cHQgZGF0YS4gSXQgaXMgYSBibG9jayBjaXBoZXIgdGhhdCB1c2VzIHRoZSBTUE4gKHN1YnN0aXR1dGlvbiBwZXJtdXRhdGlvbiBuZXR3b3JrKSBhbGdvcml0aG0sIGFwcGx5aW5nIG11bHRpcGxlIHJvdW5kcyB0byBlbmNyeXB0IGRhdGEuIFZpcnR1YWwgUHJpdmF0ZSBOZXR3b3JrcywgbW9iaWxlIGFwcGxpY2F0aW9ucywgcGFzc3dvcmQgbWFuYWdlcnMsIHdpcmVsZXNzIG5ldHdvcmtzLCBhbmQgZXZlbiB2aWRlbyBnYW1lcyB1c2UgQUVTIGVuY3J5cHRpb24uIDw8RmxhZzw8QmU5MjNmOTFkOTg2Y2I4M2I5YzM3OTZkZGU4NGRjNWQ1ZTA4NDE1Mz4+DQoNCg0K',
        'IP': '55.45.20.74',
        'answer': '11'
    }
]

def selectfrom():
    selection = base65Set[0]['IP']
    print(selection)

stegSet=[
    {
        'image': '/static/forensicimage1.png',
        'stegHash': 'U2FsdGVkX18099HHwV0FYWBJXXfd4JDKkrhsHwGeD64=',
        'passphrase': 'ellipticcurve',
        'hash': 'check_user.php',
        'splunkChallenge': 'using flag check_user.php, what is the input ip address 85.50.46.53 used in the password field for sql injection (status_code=200)?',
        'answer': 'or 1=1-'
    },
    {
        'image': '/static/forensicimage2.png',
        'stegHash': 'U2FsdGVkX18kH6hnY7hTQRevY8ym+nWBOaUX/wxlYC0=',
        'passphrase': 'ellipticcurve',
        'hash': 'get.php?file',
        'splunkChallenge': '(using flag - "get.php?file") which file has the ip address 78.54.12.66 successfully read through Local File Inclusion attempt (status_code=200)?',
        'answer': '/etc/passwd'
    },
    {
        'image': '/static/forensicimage3.png',
        'stegHash': 'U2FsdGVkX18kH6hnY7hTQUwpm+BzKNfdwAGxLg12a54=',
        'passphrase': 'ellipticcurve',
        'hash': 'cgi-bin',
        'splunkChallenge': '(using flag - cgi-bin) what is the system binary that ip address 68.49.17.11 has used to execute the payload "echo;id" with successful status_code=200?',
        'answer': '/bin/sh'
    },
    {
        'image': '/static/forensicimage4.png',
        'stegHash': 'U2FsdGVkX18kH6hnY7hTQTB0T6u+oNS022XDT/vBaiQ=',
        'passphrase': 'ellipticcurve',
        'hash': 'wshell0x.php',
        'splunkChallenge': '(using flag wshell0x.php) what is the password used by the ip address 31.16.19.41 with status_code=200?',
        'answer': 'pass1234!'
    },
    {
        'image': '/static/forensicimage5.png',
        'stegHash': 'U2FsdGVkX18kH6hnY7hTQUdUNJCeR/SOREsGgmjZCuLasc8853KIZG/Sh/vYuY1t',
        'passphrase': 'ellipticcurve',
        'hash': 'blood`1234567890',
        'splunkChallenge': '(using flag "blood`1234567890") what is the password that ip address 55.45.20.74 has used in the login function with successful status_code=200?',
        'answer': 'password12345'
    }
]

