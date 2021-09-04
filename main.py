import imaplib
import email
from email.header import decode_header
import webbrowser
import os
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import threading

token = os.environ.get('Token')
username = os.environ.get('mail')
password = os.environ.get('password')

vk_session = vk_api.VkApi(token=token)
longpoll = VkBotLongPoll(vk_session, 206937500) #id группы

def sender(id, text):
    vk_session.method('messages.send', {'chat_id' : id, 'message' : text, 'random_id' : 0})

def clean(text):
    # чистый текст для создания папки
    return "".join(c if c.isalnum() else "_" for c in text)
# create an IMAP4 class with SSL
imap = imaplib.IMAP4_SSL("imap.yandex.com")
# authenticate
imap.login(username, password)
# количество популярных писем для получения
z=0

def vk(s,f,msg,subject):
    sender(1,s)
    sender(1,f)
    # if the email message is multipart
    if msg.is_multipart():
        # iterate over email parts
        for part in msg.walk():
            # extract content type of email
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))
            try:
                # get the email body
                body = part.get_payload(decode=True).decode()
            except:
                pass
            if content_type == "text/plain" and "attachment" not in content_disposition:
                pass
                # print text/plain emails and skip attachments
                sender(1,body)
            elif "attachment" in content_disposition:
                # download attachment
                filename = part.get_filename()
                if filename:
                    folder_name = clean(subject)
                    if not os.path.isdir(folder_name):
                        # make a folder for this email (named after the subject)
                        os.mkdir(folder_name)
                    filepath = os.path.join(folder_name, filename)
                    # download attachment and save it
                    open(filepath, "wb").write(part.get_payload(decode=True))
    else:
        # extract content type of email
        content_type = msg.get_content_type()
        # get the email body
        body = msg.get_payload(decode=True).decode()
        if content_type == "text/plain":
            pass
            # print only text email parts
            sender(1,body)
    print('='*100)

def work():
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
                    
task1 = threading.Thread(target=work, args=())
task2 = threading.Thread(target=work1, args=())

task1.start()
task2.start()

task1.join()
task2.join()
# close the connection and logout
#imap.logout()
