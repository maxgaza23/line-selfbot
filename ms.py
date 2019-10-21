from linepy import LINE as MaxGie
from linepy import OEPoll
from datetime import datetime
from akad.ttypes import LiffViewRequest, LiffContext, LiffChatContext, Operation, Message

from threading import Thread
import json,  threading
import codecs
import time
import sys
import os
import requests

clientFileLocation = 'settings.json'
clientSettingsLoad = codecs.open(clientFileLocation, 'r', 'utf-8')
clientSettings = json.load(clientSettingsLoad)

app = "DESKTOPMAC\t5.11.1\tBOT-LOGIN\t12"
try:
    maxgie = MaxGie(settings['authToken'], appName=app)
except:
    maxgie = MaxGie(appName=app)
print ('##----- LOGIN CLIENT (Success) -----##')

oepoll = OEPoll(maxgie)
myMid = maxgie.profile.mid

def log(text):
    global maxgie
    print("[%s] [%s] : %s" % (str(datetime.now()), maxgie.profile.displayName, text))

def execute(op):
    if op.type == 25:
        print("[ 25 ] SEND MESSAGE")
        msg = op.message
        text = msg.text
        to = msg.to
        sender = msg._from
        if text is None:
            return
        if text.lower() == 'me':
            maxgie.sendContact(to, myMid)
            
    except Exception as e:
         log(e)
        
#===≠============================================================
while True:
    ops = oepoll.singleTrace(count=100)
    if ops != None:
        for op in ops:
            try:
                execute(op)
            except Exception as e:
                log(str(e))
            oepoll.setRevision(op.revision)