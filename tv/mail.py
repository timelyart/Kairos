import imaplib
import email
import smtplib
import time
from email.mime.image import MIMEImage
import os
from bs4 import BeautifulSoup
import re
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from kairos import tools
from tv import tv
import requests

# -------------------------------------------------
#
# Utility to read email from Gmail Using Python
#
# ------------------------------------------------

BASE_DIR = r"" + os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CURRENT_DIR = os.path.curdir

log = tools.log
log.setLevel(20)
config = tools.get_config(CURRENT_DIR)
log.setLevel(config.getint('logging', 'level'))

uid = str(config.get('mail', 'uid'))
pwd = str(config.get('mail', 'pwd'))
imap_server = config.get("mail", "imap_server")
imap_port = 993
smtp_server = config.get("mail", "smtp_server")
smtp_port = 465

charts = dict()


def create_browser():
    return tv.create_browser()


def destroy_browser(browser):
    tv.destroy_browser(browser)


def login(browser):
    tv.login(browser)


def take_screenshot(browser, symbol, interval, retry_number=0):
    return tv.take_screenshot(browser, symbol, interval, retry_number)


def process_data(data, browser):
    for response_part in data:
        if isinstance(response_part, tuple):
            msg = email.message_from_string(response_part[1].decode('utf-8'))
            email_subject = str(msg['subject'])
            if email_subject.find('TradingView Alert') >= 0:
                log.info('Processing: ' + msg['date'] + ' - ' + email_subject)
                # get email body
                if msg.is_multipart():
                    for part in msg.walk():
                        ctype = part.get_content_type()
                        cdispo = str(part.get('Content-Disposition'))
                        # only use parts that are text/plain and not an attachment
                        if ctype == 'text/plain' and 'attachment' not in cdispo:
                            process_body(part, browser)
                            break
                else:
                    process_body(msg, browser)


def process_body(msg, browser):
    url = ''
    screenshot_url = ''
    filename = ''
    date = msg['date']
    body = msg.get_payload()
    soup = BeautifulSoup(body, features="lxml")
    links = soup.find_all('a', href=True)
    for link in links:
        if link['href'].startswith('https://www.tradingview.com/chart/'):
            url = link['href']
            break
        if link['href'].startswith('https://www.tradingview.com/x/'):
            screenshot_url = link['href']

    log.debug("chart's url: " + url)
    if url == '':
        return False

    symbol = ''
    match = re.search("\w+[%3A|:]\w+$", url, re.M)
    try:
        symbol = match.group(0)
        symbol = symbol.replace('%3A', ':')
    except re.error as match_error:
        log.exception(match_error)
    for script in soup(["script", "style"]):
        script.extract()  # rip it out

    text = soup.get_text()
    lines = (line.strip() for line in text.splitlines())  # break into lines and remove leading and trailing space on each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))  # break multi-headlines into a line each
    # drop blank lines
    j = 0
    alert = ''
    for chunk in chunks:
        chunk = str(chunk).replace('\u200c', '')
        chunk = str(chunk).replace('&zwn', '')
        if j == 0:
            if chunk:
                alert = str(chunk).split(':')[1].strip()
                j = 1
        elif not chunk:
            break
        elif str(chunk).startswith('https://www.tradingview.com/chart/'):
            url = str(chunk)
        elif str(chunk).startswith('https://www.tradingview.com/x/'):
            screenshot_url = str(chunk)
        else:
            alert += ', ' + str(chunk)
    alert = alert.replace(',,', ',')
    alert = alert.replace(':,', ':')

    interval = ''
    match = re.search("(\d+)\s(\w\w\w)", alert)
    if match:
        interval = match.group(1)
        unit = match.group(2)
        if unit == 'day':
            interval += 'D'
        elif unit == 'wee':
            interval += 'W'
        elif unit == 'mon':
            interval += 'M'
        elif unit == 'hou':
            interval += 'H'
        elif unit == 'min':
            interval += ''
        if not url.endswith(interval):
            url += '&interval=' + interval

    # Open the chart and make a screenshot
    if config.has_option('logging', 'screenshot_timing') and config.get('logging', 'screenshot_timing') == 'summary':
        browser.execute_script("window.open('" + url + "');")
        for handle in browser.window_handles[1:]:
            browser.switch_to.window(handle)
        # page is loaded when we are done waiting for an clickable element
        tv.wait_and_click(browser, tv.css_selectors['btn_calendar'])
        tv.wait_and_click(browser, tv.css_selectors['btn_watchlist_menu'])
        [screenshot_url, filename] = take_screenshot(browser, symbol, interval)
        tv.close_all_popups(browser)

    charts[url] = [symbol, alert, date, screenshot_url, filename]


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
            else:
                browser = create_browser()
                login(browser)

                for mail_id in id_list:
                    result, data = mail.fetch(mail_id, '(RFC822)')
                    process_data(data, browser)

                destroy_browser(browser)

        except imaplib.IMAP4.error as mail_error:
            log.error("Search failed. Please verify you have a correct search_term and search_area defined.")
            log.exception(mail_error)

        mail.close()
        mail.logout()
    except Exception as e:
        log.exception(e)


def send_mail(webhooks=True):

    msg = MIMEMultipart('alternative')
    msg['Subject'] = "TradingView Alert Summary"
    msg['From'] = uid
    msg['To'] = uid
    text = ''
    list_html = ''
    html = '<html><body>'

    count = 0
    if config.has_option('mail', 'format') and config.get('mail', 'format') == 'table':
        html += '<table><thead><tr><th>Date</th><th>Symbol</th><th>Alert</th><th>Screenshot</th><th>Chart</th></tr></thead><tbody>'

    for url in charts:
        symbol = charts[url][0]
        alert = charts[url][1]
        date = charts[url][2]
        screenshot = charts[url][3]

        filename = ''
        if len(charts) >= 4:
            filename = charts[url][4]

        if config.has_option('mail', 'format') and config.get('mail', 'format') == 'table':
            html += generate_table_row(date, symbol, alert, screenshot, url)
        else:
            list_html += generate_list_entry(msg, date, symbol, alert, screenshot, filename, url, count)

        text += generate_text(date, symbol, alert, screenshot, url)
        if webhooks:
            send_webhooks(date, symbol, alert, screenshot, filename, url)
        count += 1

    if config.has_option('mail', 'format') and config.get('mail', 'format') == 'table':
        html += '</tbody></tfooter><tr><td>Number of alerts:' + str(count) + '</td></tr></tfooter></table></body></html>'
    else:
        html += '<h2>TradingView Alert Summary</h2><h3>Number of signals: ' + str(count) + '</h3>' + list_html + '</body></html>'

    msg.attach(MIMEText(text, 'plain'))
    msg.attach(MIMEText(html, 'html'))
    server = smtplib.SMTP_SSL(smtp_server, smtp_port)
    server.login(uid, pwd)
    server.sendmail(uid, uid, msg.as_string())
    log.info("Mail send")
    server.quit()


def generate_text(date, symbol, alert, screenshot, url):
    return url + "\n" + alert + "\n" + symbol + "\n" + date + "\n" + screenshot + "\n"


def generate_list_entry(msg, date, symbol, alert, screenshot, filename, url, count):
    result = ''
    if screenshot:
        result += '<hr><h4>' + alert + '</h4><a href="' + url + '"><img src="' + screenshot + '"/></a><p>' + screenshot + '<br/>' + url + '</p>'
    elif filename:
        try:
            screenshot_id = str(count + 1)
            fp = open(filename, 'rb')
            msgImage = MIMEImage(fp.read())
            fp.close()
            msgImage.add_header('Content-ID', '<screenshot' + screenshot_id + '>')
            msg.attach(msgImage)
            result += '<hr><h4>' + alert + '</h4><a href="' + url + '"><img src="cid:screenshot' + screenshot_id + '"/></a><p>' + screenshot + '<br/>' + url + '</p>'
        except Exception as send_mail_error:
            log.exception(send_mail_error)
            result += '<hr><h4>' + alert + '</h4><a href="' + url + '">Error embedding screenshot: ' + filename + '</a><p>' + screenshot + '<br/>' + url + '</p>'
    else:
        result += '<hr><h4>' + alert + '</h4><a href="' + url + '">' + url + '</a><p>' + screenshot + '<br/>' + url + '</p>'
    return result


def generate_table_row(date, symbol, alert, screenshot, url):
    return '<tr><td>' + date + '</td><td>' + symbol + '</td><td>' + alert + '</td><td>' + '<a href="' + screenshot + '">' + screenshot + '</a>' + '</td><td>' + '<a href="' + url + '">' + url + '</a>' + '</td></tr>'


def send_webhooks(date, symbol, alert, screenshot, filename, url):
    result = False
    if config.has_option('webhooks', 'search_criteria') and config.has_option('webhooks', 'webhook'):
        search_criteria = config.getlist('webhooks', 'search_criteria')
        webhooks = config.getlist('webhooks', 'webhook')

        for i in range(len(search_criteria)):

            if search_criteria[i] and str(alert).find(str(search_criteria[i])):
                for j in range(len(webhooks)):

                    if webhooks[j]:
                        result = [500, 'Internal Server Error; search_criteria: ' + str(search_criteria[i]) + '; webhook: ' + str(webhooks[j])]
                        if screenshot:
                            r = requests.post(str(webhooks[j]), json={'date': date, 'symbol': symbol, 'alert': alert, 'chart_url': url, 'screenshot_url': screenshot})
                        # unfortunately, we cannot always send a raw image (e.g. zapier)
                        # elif filename:
                        #     screenshot_bytestream = ''
                        #     try:
                        #         fp = open(filename, 'rb')
                        #         screenshot_bytestream = MIMEImage(fp.read())
                        #         fp.close()
                        #     except Exception as send_webhook_error:
                        #         log.exception(send_webhook_error)
                        #     r = requests.post(webhook_url, json={'date': date, 'symbol': symbol, 'alert': alert, 'chart_url': url, 'screenshot_url': screenshot, 'screenshot_bytestream': screenshot_bytestream})
                            result = [r.status_code, r.reason]
                        if result[0] != 200:
                            log.warn(str(result[0]) + ' ' + str(result[1]))
    return result


def run(delay):
    log.info("Generating summary mail with a delay of " + str(delay) + " minutes.")
    time.sleep(delay*60)
    read_mail()
    if len(charts) > 0:
        send_mail()
