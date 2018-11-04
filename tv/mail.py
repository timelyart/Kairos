import imaplib
import email
import smtplib
from configparser import RawConfigParser
import time
from kairos import debug
import os
from bs4 import BeautifulSoup
import re
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# -------------------------------------------------
#
# Utility to read email from Gmail Using Python
#
# ------------------------------------------------

BASE_DIR = r"" + os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CURRENT_DIR = os.path.curdir

log = debug.log
log.setLevel(20)

config = RawConfigParser(allow_no_value=True)
config_file = os.path.join(CURRENT_DIR, "kairos.cfg")
if os.path.exists(config_file):
    config.read(config_file)
    if config.getboolean('logging', 'clear_on_start_up'):
        debug.clear_log()
    log.setLevel(config.getint('logging', 'level'))
else:
    log.error("File " + config_file + " does not exist")
    log.exception(FileNotFoundError)
    exit(0)
log.setLevel(config.getint('logging', 'level'))

uid = str(config.get('mail', 'uid'))
pwd = str(config.get('mail', 'pwd'))
imap_server = config.get("mail", "imap_server")
imap_port = 993
smtp_server = config.get("mail", "smtp_server")
smtp_port = 465

charts = dict()


def process_data(data):
    for response_part in data:
        if isinstance(response_part, tuple):
            msg = email.message_from_string(response_part[1].decode('utf-8'))
            email_subject = str(msg['subject'])
            if email_subject.find('TradingView Alert') >= 0:
                log.info('Processing: ' + msg['date'] + ' - ' + msg['subject'])
                return True
                # get email body
                if msg.is_multipart():
                    for part in msg.walk():
                        ctype = part.get_content_type()
                        cdispo = str(part.get('Content-Disposition'))
                        # only use parts that are text/plain and not an attachment
                        if ctype == 'text/plain' and 'attachment' not in cdispo:
                            process_body(part)
                            break
                else:
                    process_body(msg)


def process_body(msg):
    # symbol = re.sub(r"\w*:\w*$:", "", msg['subject'])
    url = ''
    alert = ''
    date = msg['date']
    body = msg.get_payload()
    soup = BeautifulSoup(body, features="lxml")
    links = soup.find_all('a', href=True)
    for link in links:
        # log.info(link)
        if link['href'].startswith('https://www.tradingview.com/chart/'):
            url = link['href']
            break

    # symbol = re.sub(r"\w*%3\w*$:", "", url)
    match = re.search("\w*[%3|:]\w*$", url)
    symbol = match.group(0)
    symbol = symbol.replace('%3', ':')
    for script in soup(["script", "style"]):
        script.extract()  # rip it out
    # text = soup.get_text(separator=' ')
    text = soup.get_text()
    lines = (line.strip() for line in text.splitlines())  # break into lines and remove leading and trailing space on each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))  # break multi-headlines into a line each
    # drop blank lines
    j = 0
    for chunk in chunks:
        if chunk:
            # first chunk is the alert message
            if j == 0:
                alert = chunk
                break
            j += 1

    match = re.search("(\d+)\s(\w\w\w)", alert)
    if type(match) is re.Match:
        interval = match.group(1)
        unit = match.group(2)
        if unit == 'day':
            interval += 'D'
        elif unit == 'wee':
            interval += 'W'
        elif unit == 'hou':
            interval += 'H'
        elif unit == 'min':
            interval += 'M'
        url += '&interval=' + interval
    charts[url] = [symbol, alert, date]


def read_mail():
    try:
        mail = imaplib.IMAP4_SSL(imap_server)
        mail.login(uid, pwd)
        result, data = mail.list()
        if result != 'OK':
            log.error(result)
            return False

        mailbox = 'inbox'
        if config.has_option('mail', 'mailbox') and config.get('mail', 'mailbox') != '':
            mailbox = str(config.get('mail', 'mailbox'))
        mail.select(mailbox)

        search_area = "UNSEEN"
        if config.has_option('mail', 'search_area') and config.get('mail', 'search_area') != '':
            search_area = str(config.get('mail', 'search_area'))
        if search_area != "UNSEEN" and config.has_option('mail', 'search_term') and config.get('mail', 'search_term') != '':
            search_term = u"" + str(config.get('mail', 'search_term'))
            log.info('search_term: ' + search_term)
            mail.literal = search_term.encode("UTF-8")

        log.info('search_area: ' + search_area)
        try:
            result, data = mail.search("utf-8", search_area)
            mail_ids = data[0]
            id_list = mail_ids.split()
            if len(id_list) == 0:
                log.info('No mail to process')

            for mail_id in id_list:
                result, data = mail.fetch(mail_id, '(RFC822)')
                process_data(data)

        except imaplib.IMAP4.error as mail_error:
            log.error("Search failed. Please verify you have a correct search_term and search_area defined.")
            log.exception(mail_error)

        mail.close()
        mail.logout()
    except Exception as e:
        log.exception(e)


def send_mail():
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "TradingView Alert Summary"
    msg['From'] = uid
    msg['To'] = uid

    text = ''
    html = '<html><body><table>'
    html += '<thead><tr><th>Date</th><th>Symbol</th><th>Alert</th><th>Chart</th></tr></thead><tbody>'
    count = 0
    for url in charts:
        symbol = charts[url][0]
        alert = charts[url][1]
        date = charts[url][2]
        html += '<tr><td>' + date + '</td><td>' + symbol + '</td><td>' + alert + '</td><td>' + '<a href="' + url + '">' + url + '</a>' + '</td></tr>'
        text += url+"\n"+alert+"\n"+symbol+"\n"+date+"\n"
        count += 1

    html += '</tbody></tfooter><tr><td>Number of alerts:' + str(count) + '</td></tr></tfooter>'
    html += '</table></body></html>'

    msg.attach(MIMEText(text, 'plain'))
    msg.attach(MIMEText(html, 'html'))
    server = smtplib.SMTP_SSL(smtp_server, smtp_port)
    server.login(uid, pwd)
    server.sendmail(uid, uid, msg.as_string())
    log.info("Mail send")
    server.quit()


def run(delay):
    log.info("Generating summary mail with a of " + str(delay) + " minutes.")
    time.sleep(delay*60)
    read_mail()
    if len(charts) > 0:
        send_mail()

