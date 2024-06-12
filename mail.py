import os
import imaplib
import email
from email.header import decode_header

from bs4 import BeautifulSoup
from dotenv import load_dotenv, find_dotenv

from database import orm
from parse import get_parsed_body, get_text
from sheets.sheets import get_current_time

load_dotenv(find_dotenv())


async def send_message(text, bot, info_dict, session, exchanger):
    chat_id = os.getenv('CHAT_ID')
    message = await bot.send_message(chat_id, text)
    message_id = message.message_id
    await orm.add_exchange(session,
                           message_id=message_id,
                           exchanger=exchanger,
                           info_dict=info_dict)


async def process_email(bot, session, exchanger):
    if exchanger == 'Transit-Bit':
        mail_pass = os.getenv('PASSWORD_TRANSIT')
        username = os.getenv('LOGIN_TRANSIT')
    else:
        mail_pass = os.getenv('PASSWORD_GOODBOY')
        username = os.getenv('LOGIN_GOODBOY')
    imap_server = os.getenv('IMAP_SERVER')

    print(f'{exchanger}: установка соединения\n'
          f'{get_current_time("time")}')

    mail = imaplib.IMAP4_SSL(imap_server)
    try:
        mail.login(username, mail_pass)
    except imaplib.IMAP4.error as e:
        await bot.send_message(
            chat_id=os.getenv('ADMIN_ID'),
            text=(f'Ошибка при попытке зайти в почту\n{e}\n'
                  f'{get_current_time("time")}'))
        return

    mail.select('INBOX/ToMyself')
    status, messages = mail.uid('search', "UNSEEN", "ALL")

    print(f'{exchanger}: соединение открыто\n'
          f'{get_current_time("time")}')

    if status == 'OK':

        uids = messages[0].split()

        for uid in uids:
            res, msg = mail.uid('fetch', uid, '(RFC822)')
            if res == 'OK':
                msg = email.message_from_bytes(msg[0][1])
                subject = decode_header(msg["Subject"])[0][0].decode()
                if subject.startswith('Оплаченная заявка'):
                    for part in msg.walk():
                        if part.get_content_type() == 'text/html':
                            body = part.get_payload(decode=True).decode()
                            soup = BeautifulSoup(body, 'html.parser')
                            body_without_tags = soup.get_text()
                            body_without_tags = body_without_tags.split('\n')
                            while '' in body_without_tags:
                                body_without_tags.remove('')
                            info_dict = get_parsed_body(body_without_tags)
                            text = get_text(info_dict, exchanger)
                            await send_message(text=text,
                                               bot=bot,
                                               info_dict=info_dict,
                                               session=session,
                                               exchanger=exchanger)
    mail.close()

    print(f'{exchanger}: cоединение закрыто\n'
          f'{get_current_time("time")}')
