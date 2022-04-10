import imaplib
import email
import io
import time
import typing
from email.header import decode_header
from imap_tools import MailBox
import vk_api
import requests
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import os

# mail_name = os.environ.get("mail_test")
# password = os.environ.get("password_test")
mail_name = os.environ.get("mail")
password = os.environ.get("password")
token = os.environ.get("Token")

vk_session = vk_api.VkApi(token=token)
longpoll = VkBotLongPoll(vk_session, 206937500)  # id группы

imap = imaplib.IMAP4_SSL("imap.mail.ru")
imap.login(mail_name, password)


def sender(id, text):
    if text == "" or text is None:
        pass
    else:
        vk_session.method('messages.send', {'chat_id': id, 'message': text, 'random_id': 0})


def attach(id):
    with MailBox('imap.mail.ru').login(mail_name, password) as mailbox:
        for msg in mailbox.fetch(id):
            for att in msg.attachments:
                with open(format(att.filename), 'wb') as f:
                    f.write(att.payload)


def send_docs(doc):
    a = vk_session.method("docs.getMessagesUploadServer", {"type": "doc", "peer_id": 2000000001})
    print(a)
    b = requests.post(a["upload_url"], files={"file": doc}).json()
    print(b)
    c = vk_session.method("docs.save", {"file": b["file"], "title": "Document"})
    print(c)

    for q1 in c:
        print(q1)
    print()
    print(c['doc']['owner_id'])
    print(c['doc']['id'])
    d = 'doc{}_{}'.format(c['doc']['owner_id'], c['doc']['id'])
    vk_session.method('messages.send', {'chat_id': 1, 'attachment': d, 'random_id': 0})


def body_1(email_mes):
    body = None
    bol = True
    for part in email_mes.walk():
        print(part.get_payload)
        if part.get_content_type() == "text/plain":
            body = part.get_payload(decode=True)
            body = body.decode('UTF-8')
            bol = False
        elif bol and part.get_content_type() == "text/html":
            body = part.get_payload(decode=True)
            body = body.decode('UTF-8').replace("<div>", '').replace("</div>", '')
    if body is not None:
        return body
    else:
        return None


def vk(s, msg):
    for response in msg:
        if isinstance(response, tuple):
            # parse a bytes email into a message object
            msg = email.message_from_bytes(response[1])
            # decode email sender
            From, encoding_1 = decode_header(msg.get("From"))[0]
            try:
                sub, encoding_2 = decode_header(msg.get("Subject"))[0]
            except Exception as e:
                print(e)
                #sender(1, e)
                sub = "Без темы"
            if isinstance(From, bytes):
                From = From.decode(encoding_1)
            if isinstance(sub, bytes):
                sub = sub.decode(encoding_2)
    sender(2, From)
    sender(2, sub)
    sender(2, s)


def first_enter():
    imap.select("INBOX")
    result, data = imap.search(None, "ALL")
    id_list = data[0].split()
    latest_email_id = id_list[-1]
    result, mes = imap.fetch(latest_email_id, "(RFC822)")
    email_mes = email.message_from_bytes(mes[0][1])
    email_mes.get
    return email_mes["Message-Id"]


def work():
    id_mes = first_enter()
    # id_mes = "1"
    print("start")
    while True:
        imap.select("INBOX")
        result, data = imap.search(None, "ALL")
        id_list = data[0].split()
        latest_email_id = id_list[-1]

        result, mes = imap.fetch(latest_email_id, "(RFC822)")
        email_mes = email.message_from_bytes(mes[0][1])
        email_mes.get

        body = body_1(email_mes)

        if email_mes["Message-Id"] != id_mes:
            print(1)
            vk(body, mes)
            # attach(latest_email_id)
            id_mes = email_mes['Message-Id']
            # print(id_mes)
            imap.close()
            time.sleep(5)


try:
    work()
except Exception as e:
    print(e)
    sender(1, e)
