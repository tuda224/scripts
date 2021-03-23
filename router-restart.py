import subprocess
import requests
import xml.etree.ElementTree as xml
import hashlib
import time
from lxml import html

def writeLog(message):
    currentDate = time.strftime('%Y-%m-%d %H:%M:%S')
    with open('restart.log', 'a') as file:
        file.write(currentDate + ' ' + message + '\n')

def rebootRouter(user, password, ip):
    baseUrl = f'http://{ip}/'
    with requests.Session() as s:
        # get cookies
        response = s.get(baseUrl)

        # get login token
        tokenResponse = s.get(f'{baseUrl}function_module/login_module/login_page/logintoken_lua.lua')
        xmlRoot = xml.fromstring(tokenResponse.text)
        token = xmlRoot.text
        writeLog('got login token: ' + token)

        # login
        hashedPassword = hashlib.sha256((password+token).encode('UTF-8')).hexdigest()
        writeLog('hashedPassword: ' + hashedPassword)
        payload = {'Username': user, 'Password': hashedPassword, 'action': 'login'}
        authResponse = s.post(baseUrl, data=payload, cookies=response.cookies)
        doc = html.fromstring(authResponse.text)
        sessionTokenPositionStart = authResponse.text.find('_sessionTmpToken')
        sessionTokenPositionEnd = authResponse.text.find(';', sessionTokenPositionStart)
        sessionToken = authResponse.text[sessionTokenPositionStart:sessionTokenPositionEnd].replace(' ', '').split('=')[1].replace('\\x3', '').replace('"', '')
        element = doc.get_element_by_id('logUser')
        if element.text.replace('\n', '') == user:
            writeLog('successfully logged in')
        else:
            writeLog('unable to log in')
            return

        # reboot router
        restartPayload = {'IF_ACTION': 'Restart', 'Btn_restart': '', '_sessionTOKEN': sessionToken}
        restartResponse = s.post(f'{baseUrl}common_page/deviceManag_lua.lua?IF_ACTION=Restart&Btn_restart=&_sessionTOKEN={sessionToken}', cookies=response.cookies)
        writeLog(restartResponse.text)

        
user = ''
password = ''
ip = ''
rebootRouter(user, password, ip)