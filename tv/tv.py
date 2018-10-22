# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
from kairos import timing
import configparser
import datetime
import sys
from selenium.webdriver.common.keys import Keys
import re
import time
from selenium.common.exceptions import NoSuchElementException
from kairos import debug
import yaml
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
import os

BASE_DIR = r"" + os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CURRENT_DIR = os.path.curdir
TEXT = 'text'
CHECKBOX = 'checkbox'
SELECTBOX = 'selectbox'
DATE = 'date'
TIME = 'time'

WAIT_TIME_IMPLICIT = 30
PAGE_LOAD_TIMEOUT = 15
WAIT_TIME_CHECK = 15
WAIT_TIME_BREAK_MINI = 0.2
WAIT_TIME_BREAK = 0.5
WAIT_TIME_SUBMIT_ALERT = 3.5
DELAY_CLEAR_INACTIVE_ALERTS = 0


ALERT_NUMBER = 0

css_selectors = dict(
    username='body > div.tv-main > div.tv-header > div.tv-header__inner.tv-layout-width > div.tv-header__area.tv-header__area--right.tv-header__area--desktop > span.tv-dropdown-behavior.tv-header__dropdown.tv-header__dropdown--user > span.tv-header__dropdown-wrap.tv-dropdown-behavior__'
             'button > span.tv-header__dropdown-text.tv-header__dropdown-text--username.js-username.tv-header__dropdown-text--ellipsis.apply-overflow-tooltip.common-tooltip-fixed',
    signin='body > div.tv-main > div.tv-header > div.tv-header__inner.tv-layout-width > div.tv-header__area.tv-header__area--right.tv-header__area--desktop > span.tv-header__dropdown-text > a',
    input_username='#signin-form > div.tv-control-error > div.tv-control-material-input__wrap > input',
    input_password='#signin-form > div.tv-signin-dialog__forget-wrap > div.tv-control-error > div.tv-control-material-input__wrap > input',
    input_watchlist_add_symbol='body > div.js-rootresizer__contents > div.layout__area--right > div > div.widgetbar-pages > div.widgetbar-pagescontent > div.widgetbar-page.active > div.widgetbar-widget.widgetbar-widget-watchlist > div.widgetbar-widgetheader > div.widgetbar-headerspace > input',
    btn_login='#signin-form > div.tv-signin-dialog__footer.tv-signin-dialog__footer--login > div:nth-child(2) > button',
    btn_charts='body > div.tv - main > div.tv - header > div.tv - mainmenu > ul > li.tv - mainmenu__item.tv - mainmenu__item - -chart',
    btn_watchlist_menu='body > div.js-rootresizer__contents > div.layout__area--right > div > div.widgetbar-tabs > div > div:nth-child(1) > div > div > div:nth-child(1)',
    btn_watchlist_menu_active='input.wl-symbol-edit',
    btn_watchlist_dropdown_menu='body > div.js-rootresizer__contents > div.layout__area--right > div > div.widgetbar-pages > div.widgetbar-pagescontent > div.widgetbar-page.active > div.widgetbar-widget.widgetbar-widget-watchlist > div.widgetbar-widgetheader > div.widgetbar-headerspace > a',
    btn_watchlist_dropdown_menu_active='body > div.js-rootresizer__contents > div.layout__area--right > div > div.widgetbar-pages > div.widgetbar-pagescontent > div.widgetbar-page.active > div.widgetbar-widget.widgetbar-widget-watchlist > div.widgetbar-widgetheader > div.widgetbar-headerspace > '
                                       'a.button.active.open',
    btn_load_watchlist='body > div.js-rootresizer__contents > div.layout__area--right > div > div.widgetbar-pages > div.widgetbar-pagescontent > div.widgetbar-page.active > div.widgetbar-widget.widgetbar-widget-watchlist > div.widgetbar-widgetheader > div.widgetbar-headerspace > a',
    btn_add_alert='#header-toolbar-alerts',
    btn_alerts='div[data-name="alerts"]',
    btn_data_window='div[data-name="data-window"]',
    btn_calendar='div[data-name="calendar"]',
    div_watchlist_symbols='body > div.layout__area--right > div > div.widgetbar-pages > div.widgetbar-pagescontent > div.widgetbar-page.active > div.widgetbar-widget.widgetbar-widget-watchlist > div.widgetbar-widgetbody > div.symbol-list-container.wrapper-2KWBfDVB-.touch-E6yQTRo_- > div',
    div_watchlist_item='div.symbol-list > div.symbol-list-item.success',
    form_create_alert='body > div.tv-dialog.js-dialog.tv-dialog--popup.ui-draggable.i-focused > div.tv-dialog__scroll-wrap.i-with-actions.wrapper-2KWBfDVB-.touch-E6yQTRo_- > div > div > div > p > form',
    signout='body > div.tv-main.tv-screener__standalone-main-container > div.tv-header > div.tv-header__inner.tv-layout-width > div.tv-header__area.tv-header__area--right.tv-header__area--desktop > span.tv-dropdown-behavior.tv-header__dropdown.tv-header__dropdown--user.i-opened > '
            'span.tv-dropdown-behavior__body.tv-header__dropdown-body.tv-header__dropdown-body--fixwidth.i-opened > span:nth-child(13) > a')
xpath_selectors = dict(
    btn_watchlist_menu='//div[@data-name=right-toolbar]/div[@data-name=base]'
)
class_selectors = dict(
    form_create_alert='js-alert-form',
    input='tv-control-input',
    selectbox='tv-control-select',
    selectbox_options='selectbox_options'
)

log = debug.log
log.setLevel(20)

config = configparser.RawConfigParser(allow_no_value=True)
config_file = os.path.join(CURRENT_DIR, "kairos.cfg")
if os.path.exists(config_file):
    config.read(config_file)
    log.setLevel(config.getint('logging', 'level'))
else:
    log.error("File " + config_file + " does not exist")
    log.exception(FileNotFoundError)
    exit(0)
log.setLevel(config.getint('logging', 'level'))

path_to_chromedriver = r"" + config.get('chromedriver', 'path')
if os.path.exists(path_to_chromedriver):
    path_to_chromedriver = path_to_chromedriver.replace('.exe', '')
    path_to_chromedriver = re.sub(r"^[a-zA-Z]:", "", path_to_chromedriver)
else:
    log.error("File " + path_to_chromedriver + " does not exist")
    log.exception(FileNotFoundError)
    exit(0)

try:
    WAIT_TIME_IMPLICIT = config.getfloat('chromedriver', 'wait_time_implicit')
    PAGE_LOAD_TIMEOUT = config.getfloat('chromedriver', 'page_load_timeout')
    WAIT_TIME_CHECK = config.getfloat('chromedriver', 'wait_time_check')
    WAIT_TIME_BREAK_MINI = config.getfloat('chromedriver', 'wait_time_break_mini')
    WAIT_TIME_BREAK = config.getfloat('chromedriver', 'wait_time_break')
    WAIT_TIME_SUBMIT_ALERT = config.getfloat('chromedriver', 'wait_time_submit_alert')
    DELAY_CLEAR_INACTIVE_ALERTS = config.getfloat('tradingview', 'delay_clear_inactive_alerts')
    EXACT_CONDITIONS = config.getboolean('tradingview', 'exact_conditions')
except Exception as e:
    log.exception(e)

options = Options()
options.add_argument("--disable-extensions")
options.add_argument('--window-size=1920,1080')
options.add_argument('--disable-notifications')
if config.getboolean('chromedriver', 'run_in_background'):
    options.add_argument('headless')  # this will hide the browser window i.e. run chrome in the background


def close_all_popups(browser):
    for h in browser.window_handles[1:]:
        browser.switch_to.window(h)
        browser.close()
        browser.switch_to.window(browser.window_handles[0])


def element_exists_by_xpath(browser, xpath):
    try:
        log.debug(xpath + ': \n')
        browser.implicitly_wait(WAIT_TIME_CHECK)
        elements = browser.find_element_by_xpath(xpath)
        log.debug('\t' + str(elements))
        browser.implicitly_wait(WAIT_TIME_IMPLICIT)
    except NoSuchElementException:
        log.warning('No such element. XPATH=' + xpath)
        return False
    return True


def element_exists(browser, css_selector):
    try:
        log.debug(css_selector + ': ')
        browser.implicitly_wait(WAIT_TIME_CHECK)
        elements = browser.find_element_by_css_selector(css_selector)
        log.debug('\t' + str(elements))
        browser.implicitly_wait(WAIT_TIME_IMPLICIT)
    except NoSuchElementException:
        log.debug('No such element. CSS SELECTOR=' + css_selector)
        return False
    return True


def wait_and_click(browser, css_selector, wait_time=WAIT_TIME_CHECK):
    WebDriverWait(browser, wait_time).until(
        ec.element_to_be_clickable((By.CSS_SELECTOR, css_selector))).click()


def wait_and_click_by_xpath(browser, xpath, wait_time=WAIT_TIME_CHECK):
    WebDriverWait(browser, wait_time).until(
        ec.element_to_be_clickable((By.XPATH, xpath))).click()


def wait_and_click_by_text(browser, tag, search_text, css_class='', wait_time=WAIT_TIME_CHECK):
    if type(css_class) is str and len(css_class) > 0:
        xpath = '//{0}[contains(text(), "{1}") and @class="{2}"]'.format(tag, search_text, css_class)
    else:
        xpath = '//{0}[contains(text(), "{1}")]'.format(tag, search_text)
    WebDriverWait(browser, wait_time).until(
        ec.element_to_be_clickable((By.XPATH, xpath))).click()


def wait_and_get(browser, css, wait_time=WAIT_TIME_CHECK):
    element = WebDriverWait(browser, wait_time).until(
        ec.element_to_be_clickable((By.CSS_SELECTOR, css)))
    return element


def set_timeframe(browser, timeframe):
    log.info('Setting timeframe to ' + timeframe)
    wait_and_click(browser, '#header-toolbar-intervals > div:last-child')
    # css = '#tooltip-root-element + div + div > div > div > div > div > div > div > div'
    css = '#__outside-render-0 > div > div > div > div > div > div > div'
    el_options = browser.find_elements_by_css_selector(css)
    index = 0
    found = False
    while not found and index < len(el_options):
        if el_options[index].text == timeframe:
            found = True
        index += 1
    if found:
        wait_and_click(browser, css + ':nth-child({0})'.format(index))
    else:
        log.warning('Unable to set timeframe to ' + timeframe)
        raise ValueError

    return found


def open_chart(browser, chart, counter_alerts, total_alerts):
    try:
        # load the chart
        close_all_popups(browser)
        log.info("Opening chart " + chart['url'])
        browser.execute_script("window.open('" + chart['url'] + "');")
        for handle in browser.window_handles[1:]:
            browser.switch_to.window(handle)

        wait_and_click(browser, css_selectors['btn_calendar'])
        wait_and_click(browser, css_selectors['btn_watchlist_menu'])
        time.sleep(WAIT_TIME_BREAK_MINI)
        # scrape the symbols for each watchlist
        dict_watchlist = dict()
        for i in range(len(chart['watchlists'])):
            # open list of watchlists element
            watchlist = chart['watchlists'][i]
            log.info("Collecting symbols from watchlist " + watchlist)
            wait_and_click(browser, 'input.wl-symbol-edit + a.button')
            # time.sleep(WAIT_TIME_BREAK_MINI)
            # load watchlist
            watchlist_exists = False
            el_options = browser.find_elements_by_css_selector('div.charts-popup-list > a.item.first')
            for j in range(len(el_options)):
                if el_options[j].text == watchlist:
                    el_options[j].click()
                    watchlist_exists = True
                    log.debug('Watchlist \'' + watchlist + '\' found')
                    time.sleep(WAIT_TIME_BREAK_MINI)
                    break

            if watchlist_exists:
                # extract symbols from watchlist
                dict_symbols = browser.find_elements_by_css_selector(css_selectors['div_watchlist_item'])
                symbols = dict()
                for j in range(len(dict_symbols)):
                    symbol = dict_symbols[j]
                    symbols[j] = symbol.get_attribute('data-symbol-full')
                    if len(symbols) >= config.getint('tradingview', 'max_symbols_per_watchlist'):
                        break
                log.debug(str(len(dict_symbols)) + ' names found for watchlist \'' + watchlist + '\'')
                dict_watchlist[chart['watchlists'][i]] = symbols

        # open alerts tab
        # wait_and_click(browser, css_selectors['btn_calendar'])
        wait_and_click(browser, css_selectors['btn_alerts'])

        # set the time frame
        for i in range(len(chart['timeframes'])):
            set_timeframe(browser, chart['timeframes'][i])
            time.sleep(WAIT_TIME_BREAK_MINI)

            # iterate over each symbol per watchlist
            for j in range(len(chart['watchlists'])):
                log.info("Opening watchlist " + chart['watchlists'][j])
                symbols = dict_watchlist[chart['watchlists'][j]]

                # open each symbol within the watchlist
                for k in range(len(symbols)):
                    log.info(symbols[k])
                    input_symbol = browser.find_element_by_css_selector('#header-toolbar-symbol-search > div > input')
                    input_symbol.send_keys(Keys.CONTROL + 'a')
                    try:
                        input_symbol.send_keys(symbols[k])
                    except Exception as err:
                        log.debug('Can\'t find ' + str(k) + ' in list of symbols:')
                        log.debug(str(symbols))
                        log.exception(err)
                    input_symbol.send_keys(Keys.ENTER)
                    time.sleep(WAIT_TIME_BREAK_MINI)

                    for l in range(len(chart['alerts'])):
                        if counter_alerts >= config.getint('tradingview', 'max_alerts') and config.getboolean('tradingview', 'clear_inactive_alerts'):
                            # instead of showing a warning first try clean inactive alerts first
                            time.sleep(DELAY_CLEAR_INACTIVE_ALERTS)
                            wait_and_click(browser, 'div.widgetbar-widget-alerts_manage > div > div > a:last-child')
                            wait_and_click(browser, 'div.charts-popup-list > a.item:nth-child(8)')
                            wait_and_click(browser, 'div.tv-dialog > div.tv-dialog__section--actions > div[data-name="yes"]')
                            time.sleep(WAIT_TIME_BREAK)
                            time.sleep(WAIT_TIME_BREAK)
                            time.sleep(WAIT_TIME_BREAK)
                            time.sleep(WAIT_TIME_BREAK)
                            # update counter
                            alerts = browser.find_elements_by_css_selector('table.alert-list > tbody > tr.alert-item')
                            if type(alerts) is list:
                                counter_alerts = len(alerts)

                        if counter_alerts >= config.getint('tradingview', 'max_alerts'):
                            log.warning("Maximum alerts reached. You can set this to a higher number in the kairos.cfg. Exiting program.")
                            return [counter_alerts, total_alerts]
                        try:
                            add_alert(browser, chart['alerts'][l])
                            counter_alerts += 1
                            total_alerts += 1
                        except Exception as err:
                            log.error("Could not set alert: " + symbols[k] + " " + chart['alerts'][l]['name'])
                            log.exception(err)

    except Exception as exc:
        log.exception(exc)
    return [counter_alerts, total_alerts]


def add_alert(browser, alert_config):
    global alert_dialog
    log.debug(alert_config['name'])

    try:
        wait_and_click(browser, '#header-toolbar-alerts')
        time.sleep(WAIT_TIME_BREAK)

        try:
            alert_dialog = browser.find_elements_by_class_name(class_selectors['form_create_alert'])[0]
        except Exception as err:
            log.error('Alert dialog not found.')
            log.exception(err)

        log.debug(str(len(alert_config['conditions'])) + ' yaml conditions found')

        # 1st row, 1st condition
        current_condition = 0
        css_1st_row_left = 'fieldset > div:nth-child(1) > span > div:nth-child(1)'
        wait_and_click(alert_dialog, css_1st_row_left)
        time.sleep(WAIT_TIME_BREAK)

        log.debug('setting condition {0} to {1}'.format(str(current_condition + 1), alert_config['conditions'][current_condition]))
        found = False
        el_options = alert_dialog.find_elements_by_css_selector(css_1st_row_left + " span.tv-control-select__option-wrap")
        condition_yaml = str(alert_config['conditions'][current_condition])
        for i in range(len(el_options)):
            option_tv = str(el_options[i].get_attribute("innerHTML")).strip()
            if option_tv == condition_yaml or ((not EXACT_CONDITIONS) and option_tv.startswith(condition_yaml)):
                el_options[i].click()
                found = True
                break
        if not found:
            log.error("Invalid condition: '" + alert_config['conditions'][current_condition] + "' in yaml definition '" + alert_config['name'] + "'. Did the title/name of the indicator/condition change?")
            return False

        # 1st row, 2nd condition?
        # Check if a second div has come up
        css_1st_row_right = 'fieldset > div:nth-child(1) > span > div:nth-child(2)'
        found = False
        if element_exists(browser, css_1st_row_right):
            current_condition += 1
            wait_and_click(alert_dialog, css_1st_row_right)

            log.debug('setting condition {0} to {1}'.format(str(current_condition + 1), alert_config['conditions'][current_condition]))
            el_options = alert_dialog.find_elements_by_css_selector(css_1st_row_right + " span.tv-control-select__option-wrap")
            condition_yaml = str(alert_config['conditions'][current_condition])
            for i in range(len(el_options)):
                option_tv = str(el_options[i].get_attribute("innerHTML")).strip()
                if (option_tv == condition_yaml) or ((not EXACT_CONDITIONS) and option_tv.startswith(condition_yaml)):
                    el_options[i].click()
                    found = True
                    break
        if not found:
            log.error("Invalid condition: '" + alert_config['conditions'][current_condition] + "' in yaml definition '" + alert_config['name'] + "'. Did the title/name of the indicator/condition change?")
            return False

        # 2nd row, 1st condition
        current_condition += 1
        css_2nd_row = 'fieldset > div:nth-child(2) > span'
        wait_and_click(alert_dialog, css_2nd_row)

        log.debug('setting condition {0} to {1}'.format(str(current_condition + 1), alert_config['conditions'][current_condition]))
        el_options = alert_dialog.find_elements_by_css_selector(css_2nd_row + " span.tv-control-select__option-wrap")
        found = False
        condition_yaml = str(alert_config['conditions'][current_condition])
        for i in range(len(el_options)):
            option_tv = str(el_options[i].get_attribute("innerHTML")).strip()
            if (option_tv == condition_yaml) or ((not EXACT_CONDITIONS) and option_tv.startswith(condition_yaml)):
                el_options[i].click()
                found = True
                break
        if not found:
            log.error("Invalid condition: '" + alert_config['conditions'][current_condition] + "' in yaml definition '" + alert_config['name'] + "'. Did the title/name of the indicator/condition change?")
            return False
        time.sleep(WAIT_TIME_BREAK_MINI)

        # 3rd+ rows, remaining conditions
        current_condition += 1
        i = 0
        while current_condition < len(alert_config['conditions']):
            log.debug('setting condition {0} to {1}'.format(str(current_condition + 1), alert_config['conditions'][current_condition]))
            found = False
            # we need to get the inputs again for every iteration as the number may change
            inputs = alert_dialog.find_elements_by_css_selector('div.js-condition-second-operand-placeholder select, div.js-condition-second-operand-placeholder input')
            condition_yaml = str(alert_config['conditions'][current_condition])
            while True:
                if inputs[i].get_attribute('type') == 'hidden':
                    i += 1
                else:
                    break

            if inputs[i].tag_name == 'select':
                elements = alert_dialog.find_elements_by_css_selector('div.js-condition-second-operand-placeholder div.tv-alert-dialog__group-item')
                if elements[i].text != alert_config['conditions'][current_condition]:
                    elements[i].click()

                    css = 'div.js-condition-second-operand-placeholder > span:nth-child(2) > div.tv-alert-dialog__group-item > span > span.tv-control-select__dropdown.tv-dropdown-behavior__body.i-opened > span > span > span > span'
                    el_options = alert_dialog.find_elements_by_css_selector(css)
                    for j in range(len(el_options)):
                        option_tv = str(el_options[i].get_attribute("innerHTML")).strip()
                        if (option_tv == condition_yaml) or ((not EXACT_CONDITIONS) and option_tv.startswith(condition_yaml)):
                            css = 'span.tv-control-select__dropdown.tv-dropdown-behavior__body.i-opened > span > span > span:nth-child({0}) > span'.format(j + 1)
                            wait_and_click(alert_dialog, css)
                            found = True
                            break
                    if not found:
                        log.error("Invalid condition: '" + alert_config['conditions'][current_condition] + "' in yaml definition '" + alert_config['name'] + "'. Did the title/name of the indicator/condition change?")
                        return False
            elif inputs[i].tag_name == 'input':
                # set focus
                # clear input of any previous value (note that input[0].clear() does NOT work
                inputs[i].send_keys(Keys.CONTROL + 'a')
                # set the new value
                inputs[i].send_keys(str(alert_config['conditions'][current_condition]).strip())

            # give some time
            time.sleep(WAIT_TIME_BREAK_MINI)
            current_condition += 1
            i += 1

        # Options (i.e. frequency)
        wait_and_click(alert_dialog, 'div[data-title="{0}"]'.format(str(alert_config['options']).strip()))
        # Expiration
        set_expiration(alert_dialog, alert_config)
        time.sleep(WAIT_TIME_BREAK_MINI)
        time.sleep(WAIT_TIME_BREAK_MINI)
        time.sleep(WAIT_TIME_BREAK_MINI)

        # Show popup
        checkbox = alert_dialog.find_element_by_name('show-popup')
        if is_checkbox_checked(checkbox) != alert_config['show_popup']:
            wait_and_click(alert_dialog, 'div.tv-alert-dialog__fieldset-value-item:nth-child(1) > label:nth-child(1) > span:nth-child(1) > span:nth-child(3)')

        # Sound
        checkbox = alert_dialog.find_element_by_name('play-sound')
        if is_checkbox_checked(checkbox) != alert_config['sound']['play']:
            wait_and_click(alert_dialog, 'div.tv-alert-dialog__fieldset-value-item:nth-child(2) > label:nth-child(1) > span:nth-child(1) > span:nth-child(3)')
        if is_checkbox_checked(checkbox):
            # set ringtone
            css = 'div.js-sound-settings > div.tv-alert-dialog__group-item.tv-alert-dialog__group-item--left > span'
            wait_and_click(alert_dialog, css)
            css = 'div.js-sound-settings span.tv-control-select__dropdown.tv-dropdown-behavior__body.i-opened span.tv-control-select__option-wrap'
            el_options = alert_dialog.find_elements_by_css_selector(css)
            for i in range(len(el_options)):
                if str(el_options[i].text).strip() == str(alert_config['sound']['ringtone']).strip():
                    el_options[i].click()
            # set duration
            css = 'div.js-sound-settings > div.tv-alert-dialog__group-item.tv-alert-dialog__group-item--right > span'
            wait_and_click(alert_dialog, css)
            css = 'div.js-sound-settings span.tv-control-select__dropdown.tv-dropdown-behavior__body.i-opened span.tv-control-select__option-wrap'
            el_options = alert_dialog.find_elements_by_css_selector(css)
            for i in range(len(el_options)):
                if str(el_options[i].text).strip() == str(alert_config['sound']['duration']).strip():
                    el_options[i].click()

        # Communication options
        # Send Email
        checkbox = alert_dialog.find_element_by_name('send-email')
        if is_checkbox_checked(checkbox) != alert_config['send']['email']:
            wait_and_click(alert_dialog, 'div.tv-alert-dialog__fieldset-value-item:nth-child(4) > label:nth-child(1) > span:nth-child(1) > span:nth-child(3)')
        # Send Email-to-SMS (the checkbox is indeed called 'send-sms'!)
        checkbox = alert_dialog.find_element_by_name('send-sms')
        if is_checkbox_checked(checkbox) != alert_config['send']['email-to-sms']:
            wait_and_click(alert_dialog, 'div.tv-alert-dialog__fieldset-value-item:nth-child(5) > label:nth-child(1) > span:nth-child(1) > span:nth-child(3)')
        # Send SMS (only for premium members)
        checkbox = alert_dialog.find_element_by_name('send-true-sms')
        if is_checkbox_checked(checkbox) != alert_config['send']['sms']:
            wait_and_click(alert_dialog, 'div.tv-alert-dialog__fieldset-value-item:nth-child(6) > label:nth-child(1) > span:nth-child(1) > span:nth-child(3)')
        # Notify on App
        checkbox = alert_dialog.find_element_by_name('send-push')
        if is_checkbox_checked(checkbox) != alert_config['send']['notify-on-app']:
            wait_and_click(alert_dialog, 'div.tv-alert-dialog__fieldset-value-item:nth-child(7) > label:nth-child(1) > span:nth-child(1) > span:nth-child(3)')

        # Construct message
        textarea = alert_dialog.find_element_by_name('description')
        time.sleep(WAIT_TIME_BREAK_MINI)
        if alert_config['message']['prepend']:
            # prepend text to a new line
            textarea.send_keys(Keys.CONTROL + Keys.HOME)
            textarea.send_keys(alert_config['message']['text'])
            textarea.send_keys(Keys.ENTER)
        else:
            textarea.send_keys(Keys.CONTROL + 'a')
            textarea.send_keys('\n', alert_config['message']['text'])

        # prepend name the text
        textarea.send_keys(Keys.CONTROL + Keys.HOME)
        textarea.send_keys(alert_config['name'])
        textarea.send_keys(Keys.ENTER)

        # Submit the form
        element = browser.find_element_by_css_selector('div[data-name="submit"] > span.tv-button__loader')
        element.click()
        time.sleep(WAIT_TIME_SUBMIT_ALERT)

    except Exception as exc:
        log.exception(exc)


def is_checkbox_checked(checkbox):
    checked = False
    try:
        checked = checkbox.get_attribute('checked') == 'true'
    finally:
        return checked


def set_expiration(_alert_dialog, alert_config):
    max_minutes = 86400
    datetime_format = '%Y-%m-%d %H:%M'

    if str(alert_config['expiration']).strip() == '' or str(alert_config['expiration']).strip().lower().startswith('n') or type(alert_config['expiration']) is None:
        return
    elif type(alert_config['expiration']) is int:
        target_date = datetime.datetime.now() + datetime.timedelta(minutes=float(alert_config['expiration']))
    elif type(alert_config['expiration']) is str and len(str(alert_config['expiration']).strip()) > 0:
        target_date = datetime.datetime.strptime(str(alert_config['expiration']).strip(), datetime_format)
    else:
        return

    max_expiration = datetime.datetime.now() + datetime.timedelta(minutes=float(max_minutes - 1440))
    if target_date > max_expiration:
        target_date = max_expiration
    date_value = target_date.strftime('%Y-%m-%d')
    time_value = target_date.strftime('%H:%M')
    # time.sleep(WAIT_TIME_BREAK_MINI)

    input_date = _alert_dialog.find_element_by_name('alert_exp_date')
    input_date.send_keys(Keys.CONTROL + 'a')
    input_date.send_keys(date_value)
    input_time = _alert_dialog.find_element_by_name('alert_exp_time')
    input_time.send_keys(Keys.CONTROL + 'a')
    input_time.send_keys(time_value)
    # time.sleep(WAIT_TIME_BREAK_MINI)


def login(browser):
    url = 'https://www.tradingview.com'
    browser.get(url)

    # if logged in under a different username or not logged in at all log out and then log in again
    elem_username = browser.find_element_by_css_selector(css_selectors['username'])
    if type(elem_username) is WebElement and elem_username.text != '' and elem_username.text == config.get('tradingview', 'username'):
        wait_and_click(browser, css_selectors['username'])
        wait_and_click(browser, css_selectors['signout'])

    wait_and_click(browser, css_selectors['signin'])
    input_username = browser.find_element_by_css_selector(css_selectors['input_username'])
    input_password = browser.find_element_by_css_selector(css_selectors['input_password'])
    input_username.clear()
    input_username.send_keys(config.get('tradingview', 'username'))
    input_password.clear()
    input_password.send_keys(config.get('tradingview', 'password'))
    wait_and_click(browser, css_selectors['btn_login'])

    time.sleep(WAIT_TIME_BREAK)
    time.sleep(WAIT_TIME_BREAK)
    time.sleep(WAIT_TIME_BREAK)
    time.sleep(WAIT_TIME_BREAK)


def run():
    counter_alerts = 0
    total_alerts = 0
    browser = None

    try:
        if len(sys.argv) > 1:
            file = r"" + os.path.join(config.get('tradingview', 'settings_dir'), sys.argv[1])
        else:
            file = r"" + os.path.join(config.get('tradingview', 'settings_dir'), config.get('tradingview', 'settings'))
        if not os.path.exists(file):
            log.error("File " + str(file) + " does not exist. Did you setup your kairos.cfg and yaml file correctly?")
            raise FileNotFoundError

        chromedriver_file = r"" + str(config.get('chromedriver', 'path'))
        if not os.path.exists(chromedriver_file):
            log.error("File " + chromedriver_file + " does not exist. Did setup your kairos.cfg correctly?")
            raise FileNotFoundError
        chromedriver_file.replace('.exe', '')

        browser = webdriver.Chrome(executable_path=chromedriver_file, options=options)
        browser.implicitly_wait(WAIT_TIME_IMPLICIT)
        login(browser)
        browser.set_page_load_timeout(PAGE_LOAD_TIMEOUT)

        # do some maintenance on the alert list (removing or restarting)
        if config.getboolean('tradingview', 'clear_alerts'):
            wait_and_click(browser, css_selectors['btn_calendar'])
            wait_and_click(browser, css_selectors['btn_alerts'])
            wait_and_click(browser, 'div.widgetbar-widget-alerts_manage > div > div > a:last-child')
            wait_and_click(browser, 'div.charts-popup-list > a.item:last-child')
            wait_and_click(browser, 'div.tv-dialog > div.tv-dialog__section--actions > div[data-name="yes"]')
            time.sleep(WAIT_TIME_BREAK)
            time.sleep(WAIT_TIME_BREAK)
        else:
            if config.getboolean('tradingview', 'restart_inactive_alerts'):
                wait_and_click(browser, css_selectors['btn_calendar'])
                wait_and_click(browser, css_selectors['btn_alerts'])
                wait_and_click(browser, 'div.widgetbar-widget-alerts_manage > div > div > a:last-child')
                wait_and_click(browser, 'div.charts-popup-list > a.item:nth-child(6)')
                wait_and_click(browser, 'div.tv-dialog > div.tv-dialog__section--actions > div[data-name="yes"]')
                time.sleep(WAIT_TIME_BREAK)
                time.sleep(WAIT_TIME_BREAK)
            elif config.getboolean('tradingview', 'clear_inactive_alerts'):
                wait_and_click(browser, css_selectors['btn_calendar'])
                wait_and_click(browser, css_selectors['btn_alerts'])
                wait_and_click(browser, 'div.widgetbar-widget-alerts_manage > div > div > a:last-child')
                wait_and_click(browser, 'div.charts-popup-list > a.item:nth-child(8)')
                wait_and_click(browser, 'div.tv-dialog > div.tv-dialog__section--actions > div[data-name="yes"]')
                time.sleep(WAIT_TIME_BREAK)
                time.sleep(WAIT_TIME_BREAK)
            # count the number of existing alerts
            alerts = browser.find_elements_by_css_selector('table.alert-list > tbody > tr.alert-item')
            if type(alerts) is not None:
                counter_alerts = len(alerts)

        # get the user defined settings file
        try:
            with open(file, 'r') as stream:
                try:
                    tv = yaml.safe_load(stream)
                    for file, charts in tv.items():
                        if type(charts) is list:
                            for i in range(len(charts)):
                                [counter_alerts, total_alerts] = open_chart(browser, charts[i], counter_alerts, total_alerts)
                except yaml.YAMLError as err_yaml:
                    log.exception(err_yaml)
        except FileNotFoundError as err_file:
            log.exception(err_file)
        except OSError as err_os:
            log.exception(err_os)

        close(browser, total_alerts)
    except Exception as exc:
        log.exception(exc)
        close(browser, total_alerts)


def close(browser, total_alerts):
    print()
    if total_alerts > 0:
        elapsed = timing.clock() - timing.start
        avg = '%s' % float('%.5g' % (elapsed / total_alerts))
        print(str(total_alerts) + " alerts set with an average process time of " + avg + " seconds")
    else:
        print("No alerts set")
    print()
    if type(browser) is webdriver.Chrome:
        close_all_popups(browser)
        browser.close()
        browser.quit()
