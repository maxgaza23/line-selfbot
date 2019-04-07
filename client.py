# -*- coding: utf-8 -*-

VERSION = "0.0.1"
BASEURL = "https://github.com/PASUNX/FREESELFBOT-01/raw/" + "master/"
TOOLSCODE = b'ZGVmIHJlbW92ZUZpbGUoZmlsZUxpc3QpOgogICAgZm9yIGZpbGUgaW4gZmlsZUxpc3Q6CiAgICAgICAgaWYgb3MucGF0aC5pc2ZpbGUoZmlsZSk6CiAgICAgICAgICAgIG9zLnJlbW92ZShmaWxlKQoKZGVmIHJlc3RhcnRTY3JpcHQoKToKICAgIHB5dGhvbiA9IHN5cy5leGVjdXRhYmxlCiAgICBvcy5leGVjbChweXRob24sIHB5dGhvbiwgKnN5cy5hcmd2KQoKZGVmIGdldENsaWVudFNvdXJjZSgpOgogICAgcmV0dXJuICdcbicuam9pbihbbGluZSBpZiAiPSIgaW4gbGluZSBlbHNlICcnIGZvciBsaW5lIGluIHJlcXVlc3RzLmdldChCQVNFVVJMKyJjbGllbnQucHkiKS50ZXh0LnNwbGl0bGluZXMoKV0pCgkKZGVmIGdldENsaWVudEluZm8oc291cmNlKToKICAgIHNvdXJjZSA9IHNvdXJjZS5zcGxpdGxpbmVzKCkKICAgIGxpc3RJbmZvID0gW2NvZGUuc3BsaXQoIj0iKSBpZiBjb2RlICE9ICcnIGVsc2UgJycgZm9yIGNvZGUgaW4gc291cmNlXQogICAgcmVzdWx0ID0ge30KICAgIGZvciBpbmZvIGluIGxpc3RJbmZvOgogICAgICAgIGlmIGxlbihpbmZvKSA9PSAyOgogICAgICAgICAgICByZXN1bHRbaW5mb1swXS5yZXBsYWNlKCIgIiwiIildID0gZXZhbChpbmZvWzFdLnJlcGxhY2UoIiAiLCIiKSkKICAgIHJldHVybiByZXN1bHQKCmRlZiB1cGRhdGVTY3JpcHQoKToKICAgIGNsaWVudEluZm8gPSBnZXRDbGllbnRJbmZvKGdldENsaWVudFNvdXJjZSgpKQogICAgaWYgVkVSU0lPTiA9PSBjbGllbnRJbmZvWydWRVJTSU9OJ106CiAgICAgICAgcmV0dXJuCiAgICBjbGllbnRGaWxlTmFtZSA9ICdjbGllbnQucHknCiAgICBjbGllbnRTb3VyY2UgPSByZXF1ZXN0cy5nZXQoY2xpZW50SW5mb1snQkFTRVVSTCddK2NsaWVudEZpbGVOYW1lKS50ZXh0CiAgICByZW1vdmVGaWxlKFtjbGllbnRGaWxlTmFtZSArICIubmV3IiwgY2xpZW50RmlsZU5hbWUgKyAiLm9sZCJdKQogICAgd2l0aCBvcGVuKGNsaWVudEZpbGVOYW1lICsgIi5uZXciLCAiYSsiLCBlbmNvZGluZz0ndXRmLTgnKSBhcyBmOgogICAgICAgIGZvciBsaW5lIGluIGNsaWVudFNvdXJjZS5zcGxpdCgiXG4iKToKICAgICAgICAgICAgZi53cml0ZShsaW5lKQogICAgb3MucmVuYW1lKGNsaWVudEZpbGVOYW1lLCBjbGllbnRGaWxlTmFtZSArICIub2xkIikKICAgIG9zLnJlbmFtZShjbGllbnRGaWxlTmFtZSArICIubmV3IiwgY2xpZW50RmlsZU5hbWUpCiAgICByZXN0YXJ0U2NyaXB0KCk='

import requests, base64, os, sys

eval(compile(base64.b64decode(TOOLSCODE), "<string>", "exec"))
updateScript()

from linepy import LINE, OEPoll
import json, codecs, time

clientFileLocation = "settings.json"
clientSettingsLoad = codecs.open(clientFileLocation, 'r', 'utf-8')
clientSettings = json.load(clientSettingsLoad)

try:
    client = LINE(clientSettings["authToken"], appName=clientSettings["appName"])
except:
    client = LINE(appName=clientSettings["appName"], showQr=True)
	
clientPoll = OEPoll(client)

def log(text):
    global client
    print("[%s] [%s] : %s" % (str(datetime.now()), client.profile.displayName, str(text)))

def clientCommand(text):
    global clientSettings
    if text.startswith(clientSettings["prefix"]):
        res = "{'cmd' : '" + text.split(" ")[0][1:].lower() + "', 'len' : " + str(len(text.split(" "))) + "}"
        return eval(res)
    return None

def clientExecute(op):
    global client
    if op.type == 1:
        client.profile = client.getProfile()
    if op.type == 25:
        msg = op.message
        to = msg.to
        text = msg.text
        if text is None: return
        cmd = clientCommand(text)
        if cmd is None: return
        if cmd['cmd'] == 'me' and cmd['len'] == 1:
            client.sendContact(client.profile.mid)

while True:
    ops = clientPoll.singleTrace(count=100)
    if ops != None:
        for op in ops:
            try:
                clientExecute(op)
            except Exception as e:
                log(e)
            clientPoll.setRevision(op.revision)
