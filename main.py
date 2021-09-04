import imaplib
import email
from email.header import decode_header
import webbrowser
import os
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import threading
import time
import re

print('start')
token = os.environ.get('Token')
username = os.environ.get('mail')
password = os.environ.get('password')

vk_session = vk_api.VkApi(token=token)
longpoll = VkBotLongPoll(vk_session, 206937500) #id группы

def sender(id, text):
    vk_session.method('messages.send', {'chat_id' : id, 'message' : text, 'random_id' : 0})
    
def cleanhtml(raw_html):
  cleanr = re.compile('<.*?>')
  cleantext = re.sub(cleanr, '', raw_html)
  return cleantext
    
def clean(text):
    # чистый текст для создания папки
    return "".join(c if c.isalnum() else "_" for c in text)
# create an IMAP4 class with SSL
imap = imaplib.IMAP4_SSL("imap.mail.ru")
# authenticate
imap.login(username, password)
# количество популярных писем для получения
z=0

def vk(s,f,msg,subject):
    sender(1,s)
    sender(1,f)
    # if the email message is multipart
    if msg.is_multipart():
        for payload in email_message.get_payload():
            body = payload.get_payload(decode=True).decode('utf-8')
            sender(1,cleanhtml(body))
    else:
        body = email_message.get_payload(decode=True).decode('utf-8')
        sender(1,cleanhtml(body))
    print('='*100)

def work():
    z = 0
    while True:
        status, messages = imap.select("INBOX")
        i=int(messages[0])
        res, msg = imap.fetch(str(i), "(RFC822)")
        for response in msg:
            if isinstance(response, tuple):
                # parse a bytes email into a message object
                msg = email.message_from_bytes(response[1])
                # decode the email subject
                subject, encoding = decode_header(msg["Subject"])[0]
                if isinstance(subject, bytes):
                    # if it's a bytes, decode to str
                    subject = subject.decode(encoding)
                # decode email sender
                From, encoding = decode_header(msg.get("From"))[0]
                if isinstance(From, bytes):
                    From = From.decode(encoding)
        if z==0:
            z=1
            id=msg['Message-Id']
            #print(1)
        if (msg['Message-Id']!=id):
            vk(subject,From,msg,subject)
            id=msg['Message-Id']
        imap.close()
        
def work2():
    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            if event.from_chat:
                id = event.chat_id
                print(id)
                msg = event.object.message['text'].lower()
                if msg == 'ping':
                    sender(id, 'pong')
                    
try:
    task1 = threading.Thread(target=work, args=())
    task2 = threading.Thread(target=work2, args=())

    task1.start()
    task2.start()

    task1.join()
    task2.join()
except Exception or ConnectionError or ConnectionResetError or ConnectionAbortedError or RuntimeError or TimeoutError or BaseException as e:
    print(e)
    sender(1,e)
# close the connection and logout
#imap.logout()
