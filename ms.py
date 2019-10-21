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

def log(text):
    global maxgie
    print("[%s] [%s] : %s" % (str(datetime.now()), maxgie.profile.displayName, text))

def execute(op):
    global settings
    if op.type == 25:
        msg = op.message
        to = msg.to
        text = msg.text
        if text in None:
        if text.lower() == 'me':
            maxgie.sendContact(to, msg._from)
            
    except Exception as e:
        log(e)
        
app = "DESKTOPMAC\t5.11.1\tBOT-LOGIN\t12"
try:
    maxgie = MaxGie(settings['token'], appName=app)
except:
    maxgie = MaxGie(appName=app)
print ('##----- LOGIN CLIENT (Success) -----##')

oepoll = OEPoll(maxgie)
myMid = maxgie.profile.mid
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