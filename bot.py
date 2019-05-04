from linepy import LINE as CLIENT
from linepy import OEPoll
from datetime import datetime
from akad.ttypes import LiffViewRequest, LiffContext, LiffChatContext, Operation, Message
from youtube_dl import YoutubeDL
import subprocess, youtube_dl, humanize, traceback
import subprocess as cmd
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
if "startTime" not in clientSettings:
    clientSettings["startTime"] = time.time()
if "mimic" not in clientSettings:
    clientSettings["mimic"] = {}
if "spamGroupProtect" not in clientSettings:
    clientSettings["spamGroupProtect"] = {}
clientStartTime = clientSettings["startTime"]

try:
    client = CLIENT(clientSettings["authToken"], appName=clientSettings["appName"], showQr=True)
except:
    client = CLIENT(appName=clientSettings["appName"], showQr=True)
print ('##----- LOGIN CLIENT (Success) -----##')

clientMid = client.profile.mid
clientPoll = OEPoll(client)
clientErrorOrNewPatch = []

set={'bc':{}}

clientHelpMessage = """---------- Help Message ----------
ชื่อผู้ใช้งาน : {dp}
เวลาทำงาน : {rt}
ไอดี : {mid}

---------- Taguser Commands ----------
- {p}profile (@) โปรไฟล์ Flex
- {p}contact (@) ข้อมูลติดต่อ
- {p}mid (@) ดู mid ผู้ใช้
- {p}name (@) ดู ชื่อ ผู้ใช้
- {p}bio (@) ดู สเตตัส ผู้ใช้
- {p}pict (@) ดู รูปโปรไฟล์ ผู้ใช้
- {p}cover (@) ดู รูปปก ผู้ใช้

---------- General Commands ----------
- {p}optest ทดสอบความเร็วในการทำงาน
- {p}speed ทดสอบความเร็วในการรับข้อมูล
- {p}runtime ดูเวลาทำงาน
- {p}reader ดูบัญชีที่อ่านข้อความ
- {p}tagall แท็กสมาชิกทั้งหมด
- {p}cvp รูปโปรไฟล์ YouTube

---------- Account Commands ----------
- {p}error ดูข้อผิดพลาดจากระบบ
- {p}mimic ดูรายชื่อลอกเลียนแบบ
- {p}mimic:add (@) เพิ่มลอกเลียนแบบ
- {p}mimic:del (@) ลบลอกเลียนแบบ
- {p}freboot บังคับเริ่มระบบใหม่
- {p}reboot เริ่มระบบใหม่
- {p}logout ออกจากระบบ
"""

if "reader" not in clientSettings:
    clientSettings["reader"] = {}
    clientSettings["reader"]["readRom"] = {}

def log(text):
    global client
    print("[%s] [%s] : %s" % (str(datetime.now()), client.profile.displayName, text))

def getProfile():
    global client
    client.profile = client.getProfile()
    if "profile" not in clientSettings:
        clientSettings["profile"] = {}
    clientSettings["profile"]["displayName"] = client.profile.displayName
    clientSettings["profile"]["statusMessage"] = client.profile.statusMessage
    clientSettings["profile"]["pictureStatus"] = client.profile.pictureStatus
    coverId = client.getProfileDetail()["result"]["objectId"]
    clientSettings["profile"]["coverId"] = coverId
    return client.profile

def commandMidContact(to, mid, cmd):
    if cmd in ["name","mid","contact","bio","pict","cover"]:
        if cmd == "mid":
            return client.sendMessage(to, mid)
        if cmd == "contact":
            return client.sendContact(to, mid)
        if cmd == "name":
            return client.sendMessage(to, client.getContact(mid).displayName)
        if cmd == "bio":
            return client.sendMessage(to, client.getContact(mid).statusMessage)
        if cmd == "pict":
            return client.sendImageWithURL(to, 'http://dl.profile.line-cdn.net/' + client.getContact(mid).pictureStatus)
        if cmd == "cover":
            return client.sendImageWithURL(to, client.getProfileCoverURL(mid))
    return
        
def removeCmd(cmd, text):
    key = clientSettings["prefix"]
    if clientSettings["prefix"] == False: key = ''  
    rmv = len(key + cmd) + 1
    return text[rmv:]

def commandAddOrDel(to, mid, cmd):
    global clientSettings
    if cmd in ["on","off"]:
        if cmd == "on":
            text = 'เพิ่ม {} เข้ารายชื่อที่ลอกเลียนแบบแล้ว'
            if mid not in clientSettings['mimic'][to]:
                clientSettings['mimic'][to][mid] = True
            else:
                text = '{} อยู่ในบัญชีที่ลอกเลียนแบบอยู่แล้ว'
            return client.sendMessage(to, text.format(client.getContact(mid).displayName))
        if cmd == "off":
            text = 'ลบ {} ออกจากรายชื่อที่ลอกเลียนแบบแล้ว'
            if mid in clientSettings['mimic'][to]:
                del clientSettings['mimic'][to][mid]
            else:
                text = '{} ไม่ได้อยู่ในบัญชีที่ลอกเลียนแบบ'
            return client.sendMessage(to, text.format(client.getContact(mid).displayName))
    return

def youtubeMp4(to, link):
    subprocess.getoutput('youtube-dl --format mp4 --output TeamMax.mp4 {}'.format(link))
    try:
        client.sendVideo(to, "TeamMax.mp4")
        time.sleep(2)
        os.remove('TeamMax.mp4')
    except:pass

def changeVideoAndPictureProfile(pict, vids):
    try:
        files = {'file': open(vids, 'rb')}
        obs_params = client.genOBSParams({'oid': clientMid, 'ver': '2.0', 'type': 'video', 'cat': 'vp.mp4'})
        data = {'params': obs_params}
        r_vp = client.server.postContent('{}/talk/vp/upload.nhn'.format(str(client.server.LINE_OBS_DOMAIN)), data=data, files=files)
        if r_vp.status_code != 201:
            return "Failed update profile"
        client.updateProfilePicture(pict, 'vp')
        return "Success update profile"
    except Exception as e:
        raise Exception("Error change video and picture profile {}".format(str(e)))
        os.remove("FadhilvanHalen.mp4")

def getCommand(text):
    global clientSettings
    if text.startswith(clientSettings["prefix"]):
        return text.split(" ")[0][1:].lower()
    return "False"

def oneOnList(text):
    global clientSettings
    if text.startswith(clientSettings["prefix"]):
        if len(text.split(" ")) == 1:
            return True
    return False

def settingsCommand(text):
    setTo = None if len(text.split(" ")) != 2 else 'on' if text.split(" ")[1] == 'on' else 'off' if text.split(" ")[1] == 'off' else None
    return setTo
	
def settingsCommand2(text):
    setTo = text.split(":")
    if len(setTo) == 1: return None
    setTo = setTo[1]
    if setTo == "add":
        return "on"
    elif setTo == "del":
        return "off"
    return None
	
def saveSettings():
    global clientSettings
    try:
        f=codecs.open(clientFileLocation,'w','utf-8')
        json.dump(clientSettings, f, sort_keys=True, indent=4, ensure_ascii=False)
    except Exception as e:
        log(str(e))
	
def Flex(to, data):
    view = client.issueLiffView(LiffViewRequest("1616062718-gRzkqKmm",LiffContext(chat=LiffChatContext(chatMid=to))))
    headers = {'content-type': 'application/json', "Authorization": "Bearer %s" % view.accessToken, "X-Requested-With": "jp.naver.line.android", "Connection": "keep-alive"}
    data = {"messages": [data]}
    post = requests.post("https://api.line.me/message/v3/share", headers=headers,data=json.dumps(data))

def sendFlex(to, text):
    data = {
    "type": "flex",
    "altText": text,
    "contents": {
    "type": "bubble",
    "styles": {
    "body": {
    "backgroundColor": '#663300'
    }
    },
    "body": {
    "type": "box",
    "layout": "vertical",
    "contents": [
    {
    "type": "text",
    "text": text,
    "color": "#ffffff",
    "gravity": "center",
    "wrap": True,
    "size": "sm"
    }
    ]
    }
    }
    }
    Flex(to,data)

def mentionMembers(to, mids=[], result=''):
    parsed_len = len(mids)//20+1
    mention = '@freeclient\n'
    no = 0
    for point in range(parsed_len):
        mentionees = []
        for mid in mids[point*20:(point+1)*20]:
            no += 1
            result += '%i. %s' % (no, mention)
            slen = len(result) - 12
            elen = len(result) + 3
            mentionees.append({'S': str(slen), 'E': str(elen - 4), 'M': mid})
        if result:
            if result.endswith('\n'): result = result[:-1]
            client.sendMessage(to, result, {'MENTION': json.dumps({'MENTIONEES': mentionees})}, 0)
        result = ''

def reflex(to, text):
    gl = client.talk.getRecentMessagesV2(to,text)
    for msg in gl:
       if 'ALT_TEXT' in msg.contentMetadata:
          if 'true' in msg.contentMetadata['FLEX_JSON']:
              re = msg.contentMetadata['FLEX_JSON'].replace('true','True')
              client.sendMessage(to, str(re))
       else:
          pass

def getRuntime():
    totalTime = time.time() - clientStartTime
    mins, secs = divmod(totalTime, 60)
    hours, mins = divmod(mins, 60)
    days, hours = divmod(hours, 24)
    resTime = ""
    if days != 00:
         resTime += "%2d วัน " % (days)
    if hours != 00:
        resTime += "%2d ชั่วโมง " % (hours)
    if mins != 00:
        resTime += "%2d นาที " % (mins)
    resTime += "%2d วินาที" % (secs)
    return resTime
	
OPTEST = {}
MimicTEMP = []
	
def execute(op):
    global clientSettings
    global OPTEST
    global clientErrorOrNewPath
    if op.type == 1:
        return getProfile()
    if op.type == 22:
        client.leaveRoom(op.param1)
    if op.type == 25:
        print("[ 25 ] SEND MESSAGE")
        msg = op.message
        text = msg.text
        to = msg.to
        msg_id = msg.id
        sender = msg._from
        if text is None:
            return
        if msg.id in MimicTEMP:
            MimicTEMP.remove(msg.id)
            return
        if msg.id in OPTEST:
            totalTime = time.time() - OPTEST[msg.id]
            del OPTEST[msg.id]
            client.sendMessage(to, "Pong! ({} ms)\n{} วินาที".format(str(totalTime*1000).split(".")[0], totalTime))
        cmd = getCommand(text)
        ononlist = oneOnList(text)
        if cmd == "False":
            clientSettings["reader"]["readRom"][to] = {}
            return
        fullCmd = (clientSettings["prefix"]+cmd)
        if cmd == "help" and ononlist:
            client.sendMessage(to, clientHelpMessage.format(p=clientSettings["prefix"],dp=client.profile.displayName,mid=client.profile.mid[:len(client.profile.mid)-20]+"*"*7, rt=getRuntime()))
        if cmd.startswith('exec\n'):
             try:
                 time.sleep(0.9)
                 exec(msg.text[6:])
             except Exception as error:
                 sendFlex(to, str("ERROR : %s" % (error)))
        if cmd.startswith('sh'):
          text = msg.text.split(' ')
          keyword = msg.text.replace(text[0] + ' ','')
          sendFlex(to, subprocess.getoutput(keyword))
        if cmd == "optest" and ononlist:
            for x in range(5):
                OPTEST[client.sendMessage(to, ".").id] = time.time()
        if cmd in ["mimic:add","mimic:del","mimic"]:
            if to not in clientSettings['mimic']:
                clientSettings['mimic'][to] = {}
            if settingsCommand2(cmd) == None and cmd == "mimic":
                midsList = [client.getContact(mid).displayName for mid in clientSettings['mimic'][to]]
                if midsList == []:
                    return client.sendMessage(to, 'ไม่มีรายชื่อที่ลอกเลียนแบบ')
                text = "รายชื่อบัญชีที่เลียนแบบ:\n"
                for x in midsList: text+="- {}".format(x)
                return client.sendMessage(to, text)
            cmd = settingsCommand2(cmd)
            if cmd is not None:
                midsList = []
                if "MENTION" in msg.contentMetadata:
                    key = eval(msg.contentMetadata["MENTION"])
                    for x in [i["M"] for i in key["MENTIONEES"]]:
                        midsList.append(x)
                for mid in midsList:
                    if len(mid) == len(clientMid):
                        commandAddOrDel(to, mid, cmd)
                return
        if cmd == "runtime" and ononlist:
            client.sendMessage(to, getRuntime())
        if cmd == "speed" or cmd == "sp" and ononlist:
            startTime = time.time()
            pingMessage = getProfile()
            totalTime = time.time() - startTime
            client.sendMessage(to, "Pong! ({} ms)\n{} วินาที".format(str(totalTime*1000).split(".")[0], totalTime))
        if cmd in ["name","contact","mid","pict","cover","bio"]:
            if len(msg.text.split(" ")) == 1:
                return commandMidContact(to, clientMid, cmd)
            else:
                if msg.text.split(" ")[1] == "@":
                    if msg.toType == 0:
                        commandMidContact(to, to, cmd)
            midsList = []
            if "MENTION" in msg.contentMetadata:
                key = eval(msg.contentMetadata["MENTION"])
                for x in [i["M"] for i in key["MENTIONEES"]]:
                    midsList.append(x)
            for x in msg.text.split(" "):
                if len(x) == len(clientMid):
                    midsList.append(x)
            if fullCmd in midsList:
                midsList.remove(fullCmd)
            for mid in midsList:
                if len(mid) == len(clientMid):
                    commandMidContact(to, mid, cmd)
            return
        if cmd == "reader" and ononlist:
            if to not in clientSettings["reader"]["readRom"]:
                clientSettings["reader"]["readRom"][to] = {}
            readerMids = [i for i in clientSettings["reader"]["readRom"][to]]
            if readerMids == []:
                return client.sendMessage(to, 'ไม่มีบัญชีที่อ่านข้อความ')
            return mentionMembers(to, readerMids, 'บัญชีที่อ่านข้อความ:\n')
        if cmd == 'tagall' and ononlist:
            membersMidsList = []
            if msg.toType == 1:
                room = client.getCompactRoom(to)
                membersMidsList = [member.mid for member in room.members]
            elif msg.toType == 2:
                group = client.getCompactGroup(to)
                membersMidsList = [member.mid for member in group.members]
            else:
                return membersMidsList.append(to)
            if membersMidsList:
                if clientMid in membersMidsList: membersMidsList.remove(clientMid)
                if membersMidsList == []:
                    return client.sendMessage(to, "ไม่มีสมาชิกในกลุ่มหรือห้องแชท")
                return mentionMembers(to, membersMidsList)
        if cmd in ["profile"]:
            profileList = []
            if len(msg.text.split(" ")) == 1:
                profile = getProfile()
                profileList = [profile]
            else:
                if msg.text.split(" ")[1] == "@":
                    if msg.toType == 0:
                        profileList.append(client.getContact(msg.to))
            if "MENTION" in msg.contentMetadata:
                key = eval(msg.contentMetadata["MENTION"])
                for x in [i["M"] for i in key["MENTIONEES"]]:
                    profileList.append(client.getContact(x))
            if profileList == []:
                for x in msg.text.split(" "):
                    if len(x) == len(clientMid):
                        profileList.append(client.getContact(x))
            if fullCmd in profileList: profileList.remove(fullCmd)
            for profile in profileList:
                if len(profile.mid) == len(clientMid):
                    if profile.pictureStatus: profilePicURL = "https://profile.line-scdn.net/" + profile.pictureStatus
                    else: profilePicURL = 'https://i.pinimg.com/originals/68/13/f4/6813f4d2c6b39c32502f76dbb053d073.jpg'
                    if profile.displayName: displayName = profile.displayName
                    else: displayName = "Unknow"
                    statusMessage = profile.statusMessage if profile.statusMessage != "" else " "
                    profileCoverURL ='https://i.pinimg.com/originals/68/13/f4/6813f4d2c6b39c32502f76dbb053d073.jpg'
                    statusMessageContents = {"type": "text","text": statusMessage,"wrap": True,"size": "xs","color": "#000000","weight": "bold","align": "center","flex": 1}
                    flexContents = {"type": "bubble","hero": {"type": "image","url": profileCoverURL,"size": "full","aspectRatio": "16:9","aspectMode": "cover","action": {"type": "uri","uri": "https://linecorp.com"}},"body": {"type": "box","layout": "vertical","spacing": "md","contents": [{"type": "box","layout": "vertical","spacing": "sm","contents": [{"type": "image","url": profilePicURL,"aspectMode": "cover","size": "xl"},{"type": "text","text": displayName,"wrap": True,"size": "lg","color": "#000000","weight": "bold","align": "center","flex": 0},statusMessageContents]}]}}
                    data = {"type": "flex", "altText": displayName, "contents":flexContents}
                    Flex(to, data)
            return
        if cmd.startswith('getflex'):
                        maxzee = msg.text.split(' ')
                        num = msg.text.replace(maxzee[0] + ' ','')
                        reflex(to, str(num))
        if cmd == "set" and ononlist:
        	line.sendaad(to,)
        if cmd == "error" and ononlist:
            text = "ข้อผิดพลาดที่บันทึก:"
            if clientErrorOrNewPatch == []:
                return client.sendMessage(to, "ไม่มีข้อผิดพลาดหรือไม่พบข้อผิดพลาดที่ถูกบันทึก")
            for e in clientErrorOrNewPatch:
                text+="\n- {}".format(e)
            text+="\n\nรายงานข้อผิดพลาดได้ที่:\nline://ti/p/~{spcontact}"
            client.sendMessage(to, text.format(spcontact="zaro_backbot."))
        if cmd.startswith('youtube'):
                            sep = text.split(" ")
                            search = text.replace(sep[0] + " ","")
                            r = requests.get("https://www.googleapis.com/youtube/v3/search?part=snippet&maxResults=10&q={}&type=video&key=AIzaSyAF-_5PLCt8DwhYc7LBskesUnsm1gFHSP8".format(str(search)))
                            data = json.loads(r.text)["items"]
                            Flex(to,{"type":"flex","altText": "ผลการค้นหาจาก Youtube","contents":{"type":"carousel","contents":[{"type":"bubble","direction":"ltr","header":{"type":"box","layout":"vertical","contents":[
{"type":"text","text":'{}'.format(str(data[0]['snippet']['channelTitle'])),"size":"md","weight":"bold","color":"#FF0000"}]},"hero":{"type":"image","url":'https://i.ytimg.com/vi/{}/hqdefault.jpg'.format(data[0]['id']['videoId']),"size":"full","aspectRatio":"20:13","aspectMode":"cover","action":{"type":"uri","uri":'https://www.youtube.com/watch?v='+data[0]['id']['videoId']}},"body":{"type":"box","layout":"vertical","contents":[{"type":"text","text":'{}'.format(str(data[0]['snippet']['title'])),"size":"md","align":"start","weight":"bold","color":"#000000","wrap":True}]},"footer":{"type":"box","layout":"vertical","spacing":"md","contents":[{"type":"box","layout":"horizontal","spacing":"md","contents":[{"type":"button","action":{"type":"uri","label":"ดูวิดีโอ","uri":'https://www.youtube.com/watch?v='+data[0]['id']['videoId']},"color":"#FF0000","style":"primary"},{"type":"button","action":{"type":"uri","label":"ลิงค์วีดีโอ","uri":"line://app/1644992891-KOnapywG?type=text&text=https://www.youtube.com/watch?v="+data[0]['id']['videoId']},"color":"#FF0000","style":"secondary"}]}]}},{"type":"bubble","direction":"ltr","header":{"type":"box","layout":"vertical","contents":[
{"type":"text","text":'{}'.format(str(data[1]['snippet']['channelTitle'])),"size":"md","weight":"bold","color":"#FF0000"}]},"hero":{"type":"image","url":'https://i.ytimg.com/vi/{}/hqdefault.jpg'.format(data[1]['id']['videoId']),"size":"full","aspectRatio":"20:13","aspectMode":"cover","action":{"type":"uri","uri":'https://www.youtube.com/watch?v='+data[1]['id']['videoId']}},"body":{"type":"box","layout":"vertical","contents":[{"type":"text","text":'{}'.format(str(data[1]['snippet']['title'])),"size":"md","align":"start","weight":"bold","color":"#000000","wrap":True}]},"footer":{"type":"box","layout":"vertical","spacing":"md","contents":[{"type":"box","layout":"horizontal","spacing":"md","contents":[{"type":"button","action":{"type":"uri","label":"ดูวิดีโอ","uri":'https://www.youtube.com/watch?v='+data[1]['id']['videoId']},"color":"#FF0000","style":"primary"},{"type":"button","action":{"type":"uri","label":"ลิงค์วีดีโอ","uri":"line://app/1644992891-KOnapywG?type=text&text=https://www.youtube.com/watch?v="+data[1]['id']['videoId']},"color":"#FF0000","style":"secondary"}]}]}},{"type":"bubble","direction":"ltr","header":{"type":"box","layout":"vertical","contents":[
{"type":"text","text":'{}'.format(str(data[2]['snippet']['channelTitle'])),"size":"md","weight":"bold","color":"#FF0000"}]},"hero":{"type":"image","url":'https://i.ytimg.com/vi/{}/hqdefault.jpg'.format(data[2]['id']['videoId']),"size":"full","aspectRatio":"20:13","aspectMode":"cover","action":{"type":"uri","uri":'https://www.youtube.com/watch?v='+data[2]['id']['videoId']}},"body":{"type":"box","layout":"vertical","contents":[{"type":"text","text":'{}'.format(str(data[2]['snippet']['title'])),"size":"md","align":"start","weight":"bold","color":"#000000","wrap":True}]},"footer":{"type":"box","layout":"vertical","spacing":"md","contents":[{"type":"box","layout":"horizontal","spacing":"md","contents":[{"type":"button","action":{"type":"uri","label":"ดูวิดีโอ","uri":'https://www.youtube.com/watch?v='+data[2]['id']['videoId']},"color":"#FF0000","style":"primary"},{"type":"button","action":{"type":"uri","label":"ลิงค์วีดีโอ","uri":"line://app/1644992891-KOnapywG?type=text&text=https://www.youtube.com/watch?v="+data[2]['id']['videoId']},"color":"#FF0000","style":"secondary"}]}]}},{"type":"bubble","direction":"ltr","header":{"type":"box","layout":"vertical","contents":[
{"type":"text","text":'{}'.format(str(data[3]['snippet']['channelTitle'])),"size":"md","weight":"bold","color":"#FF0000"}]},"hero":{"type":"image","url":'https://i.ytimg.com/vi/{}/hqdefault.jpg'.format(data[3]['id']['videoId']),"size":"full","aspectRatio":"20:13","aspectMode":"cover","action":{"type":"uri","uri":'https://www.youtube.com/watch?v='+data[3]['id']['videoId']}},"body":{"type":"box","layout":"vertical","contents":[{"type":"text","text":'{}'.format(str(data[3]['snippet']['title'])),"size":"md","align":"start","weight":"bold","color":"#000000","wrap":True}]},"footer":{"type":"box","layout":"vertical","spacing":"md","contents":[{"type":"box","layout":"horizontal","spacing":"md","contents":[{"type":"button","action":{"type":"uri","label":"ดูวิดีโอ","uri":'https://www.youtube.com/watch?v='+data[3]['id']['videoId']},"color":"#FF0000","style":"primary"},{"type":"button","action":{"type":"uri","label":"ลิงค์วีดีโอ","uri":"line://app/1644992891-KOnapywG?type=text&text=https://www.youtube.com/watch?v="+data[3]['id']['videoId']},"color":"#FF0000","style":"secondary"}]}]}},{"type":"bubble","direction":"ltr","header":{"type":"box","layout":"vertical","contents":[
{"type":"text","text":'{}'.format(str(data[4]['snippet']['channelTitle'])),"size":"md","weight":"bold","color":"#FF0000"}]},"hero":{"type":"image","url":'https://i.ytimg.com/vi/{}/hqdefault.jpg'.format(data[4]['id']['videoId']),"size":"full","aspectRatio":"20:13","aspectMode":"cover","action":{"type":"uri","uri":'https://www.youtube.com/watch?v='+data[4]['id']['videoId']}},"body":{"type":"box","layout":"vertical","contents":[{"type":"text","text":'{}'.format(str(data[4]['snippet']['title'])),"size":"md","align":"start","weight":"bold","color":"#000000","wrap":True}]},"footer":{"type":"box","layout":"vertical","spacing":"md","contents":[{"type":"box","layout":"horizontal","spacing":"md","contents":[{"type":"button","action":{"type":"uri","label":"ดูวิดีโอ","uri":'https://www.youtube.com/watch?v='+data[4]['id']['videoId']},"color":"#FF0000","style":"primary"},{"type":"button","action":{"type":"uri","label":"ลิงค์วีดีโอ","uri":"line://app/1644992891-KOnapywG?type=text&text=https://www.youtube.com/watch?v="+data[4]['id']['videoId']},"color":"#FF0000","style":"secondary"}]}]}},{"type":"bubble","direction":"ltr","header":{"type":"box","layout":"vertical","contents":[
{"type":"text","text":'{}'.format(str(data[5]['snippet']['channelTitle'])),"size":"md","weight":"bold","color":"#FF0000"}]},"hero":{"type":"image","url":'https://i.ytimg.com/vi/{}/hqdefault.jpg'.format(data[5]['id']['videoId']),"size":"full","aspectRatio":"20:13","aspectMode":"cover","action":{"type":"uri","uri":'https://www.youtube.com/watch?v='+data[5]['id']['videoId']}},"body":{"type":"box","layout":"vertical","contents":[{"type":"text","text":'{}'.format(str(data[5]['snippet']['title'])),"size":"md","align":"start","weight":"bold","color":"#000000","wrap":True}]},"footer":{"type":"box","layout":"vertical","spacing":"md","contents":[{"type":"box","layout":"horizontal","spacing":"md","contents":[{"type":"button","action":{"type":"uri","label":"ดูวิดีโอ","uri":'https://www.youtube.com/watch?v='+data[5]['id']['videoId']},"color":"#FF0000","style":"primary"},{"type":"button","action":{"type":"uri","label":"ลิงค์วีดีโอ","uri":"line://app/1644992891-KOnapywG?type=text&text=https://www.youtube.com/watch?v="+data[5]['id']['videoId']},"color":"#FF0000","style":"secondary"}]}]}},{"type":"bubble","direction":"ltr","header":{"type":"box","layout":"vertical","contents":[
{"type":"text","text":'{}'.format(str(data[6]['snippet']['channelTitle'])),"size":"md","weight":"bold","color":"#FF0000"}]},"hero":{"type":"image","url":'https://i.ytimg.com/vi/{}/hqdefault.jpg'.format(data[6]['id']['videoId']),"size":"full","aspectRatio":"20:13","aspectMode":"cover","action":{"type":"uri","uri":'https://www.youtube.com/watch?v='+data[6]['id']['videoId']}},"body":{"type":"box","layout":"vertical","contents":[{"type":"text","text":'{}'.format(str(data[6]['snippet']['title'])),"size":"md","align":"start","weight":"bold","color":"#000000","wrap":True}]},"footer":{"type":"box","layout":"vertical","spacing":"md","contents":[{"type":"box","layout":"horizontal","spacing":"md","contents":[{"type":"button","action":{"type":"uri","label":"ดูวิดีโอ","uri":'https://www.youtube.com/watch?v='+data[6]['id']['videoId']},"color":"#FF0000","style":"primary"},{"type":"button","action":{"type":"uri","label":"ลิงค์วีดีโอ","uri":"line://app/1644992891-KOnapywG?type=text&text=https://www.youtube.com/watch?v="+data[6]['id']['videoId']},"color":"#FF0000","style":"secondary"}]}]}},{"type":"bubble","direction":"ltr","header":{"type":"box","layout":"vertical","contents":[
{"type":"text","text":'{}'.format(str(data[7]['snippet']['channelTitle'])),"size":"md","weight":"bold","color":"#FF0000"}]},"hero":{"type":"image","url":'https://i.ytimg.com/vi/{}/hqdefault.jpg'.format(data[7]['id']['videoId']),"size":"full","aspectRatio":"20:13","aspectMode":"cover","action":{"type":"uri","uri":'https://www.youtube.com/watch?v='+data[7]['id']['videoId']}},"body":{"type":"box","layout":"vertical","contents":[{"type":"text","text":'{}'.format(str(data[7]['snippet']['title'])),"size":"md","align":"start","weight":"bold","color":"#000000","wrap":True}]},"footer":{"type":"box","layout":"vertical","spacing":"md","contents":[{"type":"box","layout":"horizontal","spacing":"md","contents":[{"type":"button","action":{"type":"uri","label":"ดูวิดีโอ","uri":'https://www.youtube.com/watch?v='+data[7]['id']['videoId']},"color":"#FF0000","style":"primary"},{"type":"button","action":{"type":"uri","label":"ลิงค์วีดีโอ","uri":"line://app/1644992891-KOnapywG?type=text&text=https://www.youtube.com/watch?v="+data[7]['id']['videoId']},"color":"#FF0000","style":"secondary"}]}]}},{"type":"bubble","direction":"ltr","header":{"type":"box","layout":"vertical","contents":[
{"type":"text","text":'{}'.format(str(data[8]['snippet']['channelTitle'])),"size":"md","weight":"bold","color":"#FF0000"}]},"hero":{"type":"image","url":'https://i.ytimg.com/vi/{}/hqdefault.jpg'.format(data[8]['id']['videoId']),"size":"full","aspectRatio":"20:13","aspectMode":"cover","action":{"type":"uri","uri":'https://www.youtube.com/watch?v='+data[8]['id']['videoId']}},"body":{"type":"box","layout":"vertical","contents":[{"type":"text","text":'{}'.format(str(data[8]['snippet']['title'])),"size":"md","align":"start","weight":"bold","color":"#000000","wrap":True}]},"footer":{"type":"box","layout":"vertical","spacing":"md","contents":[{"type":"box","layout":"horizontal","spacing":"md","contents":[{"type":"button","action":{"type":"uri","label":"ดูวิดีโอ","uri":'https://www.youtube.com/watch?v='+data[8]['id']['videoId']},"color":"#FF0000","style":"primary"},{"type":"button","action":{"type":"uri","label":"ลิงค์วีดีโอ","uri":"line://app/1644992891-KOnapywG?type=text&text=https://www.youtube.com/watch?v="+data[8]['id']['videoId']},"color":"#FF0000","style":"secondary"}]}]}},{"type":"bubble","direction":"ltr","header":{"type":"box","layout":"vertical","contents":[
{"type":"text","text":'{}'.format(str(data[9]['snippet']['channelTitle'])),"size":"md","weight":"bold","color":"#FF0000"}]},"hero":{"type":"image","url":'https://i.ytimg.com/vi/{}/hqdefault.jpg'.format(data[9]['id']['videoId']),"size":"full","aspectRatio":"20:13","aspectMode":"cover","action":{"type":"uri","uri":'https://www.youtube.com/watch?v='+data[9]['id']['videoId']}},"body":{"type":"box","layout":"vertical","contents":[{"type":"text","text":'{}'.format(str(data[9]['snippet']['title'])),"size":"md","align":"start","weight":"bold","color":"#000000","wrap":True}]},"footer":{"type":"box","layout":"vertical","spacing":"md","contents":[{"type":"box","layout":"horizontal","spacing":"md","contents":[{"type":"button","action":{"type":"uri","label":"ดูวิดีโอ","uri":'https://www.youtube.com/watch?v='+data[9]['id']['videoId']},"color":"#FF0000","style":"primary"},{"type":"button","action":{"type":"uri","label":"ลิงค์วีดีโอ","uri":"line://app/1644992891-KOnapywG?type=text&text=https://www.youtube.com/watch?v="+data[9]['id']['videoId']},"color":"#FF0000","style":"secondary"}]}]}}]}})
        if cmd == "chatbot":
            return client.sendMessage(to, "กรุณาตั้งค่าข้อมูลส่วนตัว\n'{pre}chatbot settings'".format(pre=clientSettings["prefix"]))
        if cmd == "reboot" and ononlist:
            if clientErrorOrNewPatch == []:
                return client.sendMessage(to, "ไม่พบข้อผิดพลาดหรือแพทช์ใหม่")
            clientSettings["rebootTime"] = time.time()
            clientSettings["lastOp"] = str(op)
            saveSettings()
            time.sleep(0.5)
            client.sendMessage(to, "กำลังเริ่มระบบใหม่อีกครั้ง")
            time.sleep(1)
            python = sys.executable
            os.execl(python, python, *sys.argv)
        if cmd.startswith('setkey'):
           textt = removeCmd('setkey', text)
           texttl = textt.lower()
           clientSettings["prefix"] = texttl
           sendFlex(to, "Success change set key to ( {} )".format(texttl))
        if cmd.startswith('cvp'):
           a = text.split(' ')
           b = text.replace(a[0] + ' ','')
           contact = client.getContact(clientMid)
           pic = "http://dl.profile.line-cdn.net/{}".format(contact.pictureStatus)
           a = subprocess.getoutput('youtube-dl --format mp4 --output TeamMax.mp4 {}'.format(b))
           print ("Downloading...\n{}".format(str(a)))
           pict = client.downloadFileURL(pic)
           vids = "TeamMax.mp4"
           changeVideoAndPictureProfile(pict, vids)
           time.sleep(0.5)
           client.sendMessage(to, "เปลี่ยนดิสวีดีโอเรียบร้อย !!")
           youtubeMp4(to,"https://os.line.naver.jp/os/p/" + clientMid + "/vp")
        if cmd == "freboot" and ononlist:
            op.message.text = "{}reboot".format(clientSettings["prefix"])
            clientErrorOrNewPatch.append("Force Reboot")
            client.sendMessage(to, "กรุณารอสักครู่")
            time.sleep(0.5)
            execute(op)
        if cmd == "logout" and ononlist:
            del clientSettings["startTime"]
            clientSettings["lastOp"] = None
            saveSettings()
            time.sleep(1)
            sys.exit()
    if op.type == 26:
        print("[ 26 ] UNSEND MESSAGE")
        msg = op.message
        to = msg._from if msg.toType == 0 else msg.to
        if to in clientSettings["mimic"]:
            if msg._from in clientSettings["mimic"][to]:
                if msg.contentType == 0:
                    if msg.text is not None:
                        MimicTEMP.append(client.sendMessage(to, msg.text).id)
    if op.type == 55:
        if op.param1 not in clientSettings["reader"]["readRom"]:
            clientSettings["reader"]["readRom"][op.param1] = {}
        if op.param2 not in clientSettings["reader"]["readRom"][op.param1]:
            clientSettings["reader"]["readRom"][op.param1][op.param2] = True
    clientSettings["lastOp"] = None
		
if client.authToken != clientSettings["authToken"]:
    clientSettings["authToken"] = client.authToken
    log("Save new auth token")
    saveSettings()
		
if "lastOp" not in clientSettings:
    clientSettings["lastOp"] = None
if clientSettings["lastOp"] is not None:
    op = eval(clientSettings["lastOp"])
    if op.type == 25:
        if op.message.text == "{}reboot".format(clientSettings["prefix"]):
            rebootMSG = ""
            if "rebootTime" in clientSettings:
                totalTime = str(time.time()-clientSettings["rebootTime"]).split(".")
                totalTime = totalTime[0] + "." + totalTime[1][:2]
                rebootMSG = " - {} วินาที".format(totalTime)
            client.sendMessage(op.message.to, "เริ่มต้นระบบใหม่อีกครั้งเรียบร้อย {}".format(rebootMSG))
            clientSettings["lastOp"] = None
    else:
        execute(op)
#===≠============================================================
while True:
    ops = clientPoll.singleTrace(count=100)
    if ops != None:
        for op in ops:
            try:
                clientSettings["lastOp"] = str(op)
                execute(op)
            except Exception as e:
                clientErrorOrNewPatch.append(e)
                client.sendMessage(eval(clientSettings["lastOp"]).message.to, "พบข้อผิดพลาดพิมพ์ '{x}error' เพื่อดูข้อผิดพลาด\nหรือพิมพ์ '{x}reboot' เพื่อเริ่มระบบใหม่อีกครั้ง".format(x=clientSettings["prefix"]))
                log(str(e))
            clientPoll.setRevision(op.revision)