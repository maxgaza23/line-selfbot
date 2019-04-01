# -*- coding: utf-8 -*-
import requests, json, codecs, time, sys, os
if not os.path.isfile(fileName): clientVersion = "0.0.0.0"
else: clientVersion = open('version.txt','r').readlines()[0]
originalVersion = requests.get("https://raw.githubusercontent.com/PASUNX/LINESELFBOT/master/version.txt").text

def removeIfIsFile(fileName):
    if os.path.isfile(fileName):
        os.remove(fileName)

def restartScript():
    python = sys.executable
    os.execl(python, python, *sys.argv)

def updateScript():
    clientFilePath = "https://raw.githubusercontent.com/PASUNX/LINESELFBOT/master/client.py"
    clientFileSource = requests.get(clientFilePath)
    clientFileName = clientFilePath[::-1].split(".")[1][::-1].split("/")[::-1][0] + "." + clientFilePath[::-1].split(".")[0][::-1]
    removeIfIsFile(clientFileName+".old")
    removeIfIsFile(clientFileName+".new")
    removeIfIsFile("version.txt")

    with open("version.txt", 'a+', encoding='utf-8') as v:
        v.write(originalVersion)
    with open(clientFileName+".new", 'a+', encoding='utf-8') as new:
        for line in clientFileSource.text.split("\n"):
            new.write(line)
    os.rename(clientFileName, clientFileName+'.old')
    os.rename(clientFileName+'.new', clientFileName)
    time.sleep(1)
    restartScript()

if clientVersion != originalVersion:
    updateScript()

from linepy import LINE as CLIENT
from linepy import OEPoll
from datetime import datetime
from akad.ttypes import LiffViewRequest, LiffContext, LiffChatContext, Operation, Message

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

clientMid = client.profile.mid
clientPoll = OEPoll(client)
clientErrorOrNewPatch = []

helpMessageJSON = {
    'รายละเอียดบัญชี': {
        "ชื่อผู้ใช้งาน: {dp}": "",
        "เวลาทำงาน: {rt}": "",
        "ไอดี: {mid}": ""
    },
    'คำสั่งทั่วไป': {
        "profile (@)": "โปรไฟล์",
        "contact (@)": "ข้อมูลติดต่อ",
        "mid (@)": "ดู Mid ผู้ใช้",
        "optest": "ทดสอบความเร็วในการทำงาน",
        "speed": "ทดสอบความเร็วในการรับข้อมูล",
        "runtime": "ดูเวลาทำงาน",
        "reader":"ดูบัญชีที่อ่านข้อความ",
        "tagall":"แท็กสมาชิกทั้งหมด"
    },
    'คำสั่งพิเศษ': {
        "shorturl": "ย่อ URL"
    },
    'บัญชี': {
        "freboot": "บังคับเริ่มระบบใหม่",
        "reboot": "เริ่มระบบใหม่หรืออัพเดทระบบ",
        "logout": "ออกจากระบบ"
    }
}

if "reader" not in clientSettings:
    clientSettings["reader"] = {}
    clientSettings["reader"]["readRom"] = {}

def log(text):
    global client
    print("[%s] [%s] : %s" % (str(datetime.now()), client.profile.displayName, text))

def helpMessage():
    global clientSettings
    helpMessageList = []
    for x, y in enumerate(helpMessageJSON):
        helpMessageList.append("{l} {title} {l}".format(title=y, l="-"*10))
        for z in helpMessageJSON[y]:
            if helpMessageJSON[y][z] == "": helpMessageList.append(z)
            else: helpMessageList.append("- {prefix}{command} {des}".format(prefix=clientSettings["prefix"], command=z, des=helpMessageJSON[y][z]))
        if x+1 != len(helpMessageJSON): helpMessageList.append("")
    return ('\n'.join(helpMessageList))

def getProfile():
    global client
    client.profile = client.getProfile()
    if "profile" not in clientSettings:
        clientSettings["profile"] = {}
    clientSettings["profile"]["displayName"] = client.profile.displayName
    clientSettings["profile"]["statusMessage"] = client.profile.statusMessage
    clientSettings["profile"]["pictureStatus"] = client.profile.pictureStatus
    return client.profile

def commandMidContact(to, mid, cmd):
    if cmd in ["mid","contact"]:
        if cmd == "mid":
            return client.sendMessage(to, mid)
        if cmd == "contact":
            return client.sendContact(to, mid)
    return
    
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
    
def sendFlex(to, data):
    view = client.issueLiffView(LiffViewRequest("1616062718-gRzkqKmm",LiffContext(chat=LiffChatContext(chatMid=to))))
    headers = {'content-type': 'application/json', "Authorization": "Bearer %s" % view.accessToken, "X-Requested-With": "jp.naver.line.android", "Connection": "keep-alive"}
    data = {"messages": [data]}
    post = requests.post("https://api.line.me/message/v3/share", headers=headers,data=json.dumps(data))
    
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
    global clientVersion
    if op.type == 1:
        return getProfile()
    if op.type == 13:
        client.acceptGroupInvitation(op.param1)
        group = client.getGroup(op.param1)
        if group.name in clientSettings["spamGroupProtect"]:
            for x in clientSettings["spamGroupProtect"]:
                if x == group.name:
                    client.leaveGroup(clientSettings["spamGroupProtect"][x])
            return client.leaveGroup(group.id)
        clientSettings["spamGroupProtect"][group.name] = group.id
    if op.type == 22:
        client.leaveRoom(op.param1)
    if op.type == 25:
        msg = op.message
        text = msg.text
        to = msg.to
		
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
        oneonlist = oneOnList(text)
        if cmd == "False":
            clientSettings["reader"]["readRom"][to] = {}
            return
        fullCmd = (clientSettings["prefix"]+cmd)
		
        if cmd == "help" and oneonlist:
            return client.sendMessage(to, helpMessage().format(dp=client.profile.displayName,mid=client.profile.mid[:len(client.profile.mid)-20]+"*"*7, rt=getRuntime()))
			
        if cmd == "optest" and oneonlist:
            for x in range(5):
                OPTEST[client.sendMessage(to, ".").id] = time.time()
				
        if cmd in ["mimic:add","mimic:del","mimic"]:
            if to not in clientSettings['mimic']:
                clientSettings['mimic'][to] = {}
            if settingsCommand2(cmd) == None and cmd == "mimic":
                mimicList = [client.getContact(mid).displayName for mid in clientSettings['mimic'][to]]
                if mimicList == []:
                    return client.sendMessage(to, 'ไม่มีรายชื่อที่ลอกเลียนแบบ')
                text = "รายชื่อบัญชีที่เลียนแบบ:"
                for x in mimicList: text+="\n- {}".format(x)
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
				
        if cmd == "runtime" and oneonlist:
            client.sendMessage(to, getRuntime())
			
        if cmd == "speed" and oneonlist:
            startTime = time.time()
            pingMessage = getProfile()
            totalTime = time.time() - startTime
            client.sendMessage(to, "Pong! ({} ms)\n{} วินาที".format(str(totalTime*1000).split(".")[0], totalTime))
			
        if cmd in ["contact","mid"]:
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
			
        if cmd == "reader" and oneonlist:
            if to not in clientSettings["reader"]["readRom"]:
                clientSettings["reader"]["readRom"][to] = {}
            readerMids = [i for i in clientSettings["reader"]["readRom"][to]]
            if readerMids == []:
                return client.sendMessage(to, 'ไม่มีบัญชีที่อ่านข้อความ')
            return mentionMembers(to, readerMids, 'บัญชีที่อ่านข้อความ:\n')
			
        if cmd == 'tagall' and oneonlist:
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
				
        if cmd == "shorturl":
            urlsList = msg.text.split(" ")
            urlsList.remove(fullCmd)
            result = "URLs:"
            if urlsList != []:
                for num, url in enumerate(urlsList):
                    if url not in result:
                        r = requests.get("https://pasunx.tk/api/urlshorten.php?url={url}".format(url=url))
                        res = json.loads(r.text)['text']
                        if res == "VALID URL! URL must be startwith http or https":
                            res = "URL ไม่ถูกต้อง"
                        result+="\n[{}.] {}\n- {}".format(num+1, url, res)
                client.sendMessage(to, result)
				
        if cmd == "profile" and oneonlist:
            profileList = []
            if len(msg.text.split(" ")) == 1:
                profile = getProfile()
                profileList = [profile]
            else:
                if msg.text.split(" ")[1] == "@":
                    if msg.toType == 0:
                        profileList.append(client.getContact(to))
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
                    else: profilePicURL = "https://pasunx.tk/ww.jpg"
                    if profile.displayName: displayName = profile.displayName
                    else: displayName = "Unknow"
                    statusMessage = profile.statusMessage if profile.statusMessage != "" else " "
                    profileCoverURL = client.getProfileCoverURL()
                    statusMessageContents = {"type": "text","text": statusMessage,"wrap": True,"size": "xs","color": "#000000","weight": "bold","align": "center","flex": 1}
                    flexContents = {"type": "bubble","hero": {"type": "image","url": profileCoverURL,"size": "full","aspectRatio": "16:9","aspectMode": "cover","action": {"type": "uri","uri": profilePicURL}},"body": {"type": "box","layout": "vertical","spacing": "md","contents": [{"type": "box","layout": "vertical","spacing": "sm","contents": [{"type": "image","url": profilePicURL,"aspectMode": "cover","size": "xl"},{"type": "text","text": displayName,"wrap": True,"size": "lg","color": "#000000","weight": "bold","align": "center","flex": 0},statusMessageContents]}]}}
                    data = {"type": "flex", "altText": displayName, "contents":flexContents}
                    sendFlex(to, data)
            return
			
        if cmd == "error" and oneonlist:
            text = "ข้อผิดพลาดที่บันทึก:"
            if clientErrorOrNewPatch == []:
                return client.sendMessage(to, "ไม่มีข้อผิดพลาดหรือไม่พบข้อผิดพลาดที่ถูกบันทึก")
            for e in clientErrorOrNewPatch:
                text+="\n- {}".format(e)
            text+="\n\nรายงานข้อผิดพลาดได้ที่:\nline://ti/p/~{spcontact}".format(spcontact="pasunx.tk")
            client.sendMessage(to, text)
			
        if cmd == "chatbot":
            return client.sendMessage(to, "กรุณาตั้งค่าข้อมูลส่วนตัว\n'{prefix}chatbot settings'".format(prefix=clientSettings["prefix"]))
			
        if cmd == "reboot" and oneonlist:
            if clientErrorOrNewPatch == []:
                originalVersion = requests.get("https://raw.githubusercontent.com/PASUNX/LINESELFBOT/master/version.txt").text
                if clientVersion != originalVersion:
                    client.sendMessage(to, "ตรวจพบแพทซ์ใหม่")
                    op.message.text = "[updateScript]"
                    clientSettings["lastOp"] = str(op)
                    saveSettings()
                    time.sleep(1)
                    updateScript()
                return client.sendMessage(to, "ไม่พบข้อผิดพลาดหรือแพทช์ใหม่")
            clientSettings["rebootTime"] = time.time()
            clientSettings["lastOp"] = str(op)
            saveSettings()
            client.sendMessage(to, "กำลังเริ่มระบบใหม่อีกครั้ง")
            time.sleep(1)
            restartScript()
			
        if cmd == "freboot" and oneonlist:
            op.message.text = "{}reboot".format(clientSettings["prefix"])
            clientErrorOrNewPatch.append("Force Reboot")
            client.sendMessage(to, "กรุณารอสักครู่")
            execute(op)
			
        if cmd == "logout" and oneonlist:
            del clientSettings["startTime"]
            clientSettings["lastOp"] = None
            saveSettings()
            time.sleep(1)
            sys.exit()
			
    if op.type == 26:
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
        if op.message.text == "{prefix}reboot".format(prefix=clientSettings["prefix"]):
            client.sendMessage(op.message.to, "เริ่มระบบใหม่อีกครั้งเรียบร้อยแล้ว")
            clientSettings["lastOp"] = None
        if op.message.text == "[updateScript]".format(prefix=clientSettings["prefix"]):
            client.sendMessage(op.message.to, "อัพเดทระบบเรียบร้อยแล้ว")
            clientSettings["lastOp"] = None
        saveSettings()
    else:
        execute(op)
        
while True:
    ops = clientPoll.singleTrace(count=100)
    if ops != None:
        for op in ops:
            try:
                clientSettings["lastOp"] = str(op)
                execute(op)
            except Exception as e:
                clientErrorOrNewPatch.append(e)
                client.sendMessage(eval(clientSettings["lastOp"]).message.to, "พบข้อผิดพลาดพิมพ์ '{prefix}error' เพื่อดูข้อผิดพลาด\nหรือพิมพ์ '{prefix}reboot' เพื่อเริ่มระบบใหม่อีกครั้ง".format(prefix=clientSettings["prefix"]))
                log(str(e))
            clientPoll.setRevision(op.revision)
