import requests
import smtplib
import time
import json
import sys
import random
from datetime import datetime
from socket import gaierror
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# function to send email
# body is appended as plain text
def sendMail(subject, body):
    # setup connection
    smpt_server = ''
    sender = ''
    recipients = ''

    # setup mail itself
    message = MIMEMultipart()
    message["Subject"] = subject
    message["From"] = sender
    message["To"] = recipients
    message.attach(MIMEText(body, "plain"))

    # try sending mail
    try:
        with smtplib.SMTP(smpt_server) as server:
            server.sendmail(sender, recipients, message.as_string())
        print('Sent')
    except (gaierror, ConnectionRefusedError):
        print('Failed to connect to server: ConnectionRefused')
    except smtplib.SMTPServerDisconnected:
        print('Failed to connect to server: Disconnected')
    except smtplib.SMTPException as e:
        print('SMPT error: ' + str(e))

def sendError(body):
    text = f'Message is: {body}'
    callSlack("Error", "<!channel>\n" + text)

def sendHeartbeat():
    text = f'sent at: {datetime.utcnow()} (UTC)'
    callSlack("Heartbeat", text)

def callSlack(title, message):
    if __name__ == '__main__':
        url = ''
        slack_data = {
            "username": "NotificationBot",
            "icon_emoji": ":+1:",
            "attachments": [
                {
                    "color": "#9733EE",
                    "fields": [
                        {
                            "title": title,
                            "value": message,
                            "short": "false",
                        }
                    ]
                }
            ]
        }
        byte_length = str(sys.getsizeof(slack_data))
        headers = {'Content-Type': "application/json", 'Content-Length': byte_length}
        response = requests.post(url, data=json.dumps(slack_data), headers=headers)
        if response.status_code != 200:
            raise Exception(response.status_code, response.text)

# url to check if it's up
url = ''

# timing variable
starttime = time.time() # current time
sleepTimeInSeconds = 90
secondsPerDay = 24 * 60 * 60 # 24 hours * 60 minutes * 60 seconds
heartbeatLimit = secondsPerDay / sleepTimeInSeconds / 8 # every 3 hours a heartbeat should be sent
loopCount =  heartbeatLimit # init in a way that immediately a heartbeat is sent

# previous status code
oldStatusCode = 200

# loop to keep check alive
while True:
    if loopCount == heartbeatLimit:
        sendHeartbeat()
        loopCount = 0

    loopCount = loopCount + 1

    try:
        response = requests.get(url)
        # send mail only when it doesn't return a 200
        if response.status_code != 200 :
            if response.status_code != oldStatusCode :
                oldStatusCode = response.status_code
                sendError("Error on response for url [" + url + "] - code is [" + response.status_code + "]")
        else:
            oldStatusCode = response.status_code # will be 200 then
    except:
        # also send an email when something fails
        sendError("Couldn't reach url [" + url + "]")
    time.sleep(sleepTimeInSeconds)