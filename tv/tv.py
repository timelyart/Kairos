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
import datetime
import getpass
import json
import math
import numbers
import os
import re
import sys
import time
import errno
import dill
import numpy

from urllib.parse import unquote
from PIL import Image
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, WebDriverException, StaleElementReferenceException, NoAlertPresentException, TimeoutException
from selenium.webdriver import DesiredCapabilities, ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support.color import Color
from multiprocessing import Pool

from kairos import timing
from kairos import tools

TEST = False

triggered_signals = []
invalid = set()

EXECUTOR = 'http://192.168.0.140:4444/wd/hub'
FILENAME = 'webdriver.instance'
COUNTER_ALERTS = 0
TOTAL_ALERTS = 0
CURRENT_DIR = os.path.curdir
TEXT = 'text'
CHECKBOX = 'checkbox'
SELECTBOX = 'selectbox'
DATE = 'date'
TIME = 'time'
MAX_SCREENSHOTS_ON_ERROR = 0
WAIT_TIME_IMPLICIT_DEF = 30
PAGE_LOAD_TIMEOUT_DEF = 15
CHECK_IF_EXISTS_TIMEOUT_DEF = 15
DELAY_BREAK_MINI_DEF = 0.2
DELAY_BREAK_DEF = 0.5
DELAY_SUBMIT_ALERT_DEF = 3.5
DELAY_CLEAR_INACTIVE_ALERTS_DEF = 0
DELAY_CHANGE_SYMBOL_DEF = 0.2
DELAY_SCREENSHOT_DIALOG = 3
DELAY_SCREENSHOT = 1
DELAY_KEYSTROKE = 0.01
DELAY_WATCHLIST = 0.5
DELAY_TIMEFRAME = 0.5
DELAY_SCREENER_SEARCH = 2
RUN_IN_BACKGROUND = False
MULTI_THREADING = False
ALERT_NUMBER = 0
SEARCH_FOR_WARNING = True

MODIFIER_KEY = Keys.LEFT_CONTROL
OS = 'windows'
if sys.platform == 'os2':
    OS = 'macos'
    MODIFIER_KEY = Keys.COMMAND
elif os.name == 'posix':
    OS = 'linux'
SELECT_ALL = MODIFIER_KEY + 'a'
CUT = MODIFIER_KEY + 'x'
PASTE = MODIFIER_KEY + 'v'
COPY = MODIFIER_KEY + 'c'

TV_UID = ''
TV_PWD = ''

NEGATIVE_COLOR = '#DD2E02'

css_selectors = dict(
    # ALERTS
    username='span.tv-header__dropdown-text.tv-header__dropdown-text--username.js-username.tv-header__dropdown-text--ellipsis.apply-overflow-tooltip.common-tooltip-fixed',
    signin='body > div.tv-main > div.tv-header > div.tv-header__inner.tv-layout-width > div.tv-header__area.tv-header__area--right.tv-header__area--desktop > span.tv-header__dropdown-text > a',
    input_username='#signin-form > div.tv-control-error > div.tv-control-material-input__wrap > input',
    input_password='#signin-form > div.tv-signin-dialog__forget-wrap > div.tv-control-error > div.tv-control-material-input__wrap > input',
    btn_login='#signin-form > div.tv-signin-dialog__footer.tv-signin-dialog__footer--login > div:nth-child(2) > button',
    btn_timeframe='#header-toolbar-intervals > div:last-child',
    options_timeframe='div[class^="dropdown-"] div[class^="item"]',
    btn_watchlist_menu='body > div.js-rootresizer__contents > div.layout__area--right > div > div.widgetbar-tabs > div > div:nth-child(1) > div > div > div:nth-child(1)',
    btn_watchlist_menu_menu='input.wl-symbol-edit + a.button',
    options_watchlist='div.charts-popup-list > a.item.first',
    input_symbol='#header-toolbar-symbol-search > div > input',
    asset='div.pane-legend-title__description',
    btn_alert_menu='div.widgetbar-widget-alerts_manage > div > div > a:last-child',
    item_clear_alerts='div.charts-popup-list > a.item:last-child',
    item_clear_inactive_alerts='div.charts-popup-list > a.item:nth-child(8)',
    item_restart_inactive_alerts='div.charts-popup-list > a.item:nth-child(6)',
    btn_dlg_clear_alerts_confirm='div.tv-dialog > div.tv-dialog__section--actions > div[data-name="yes"]',
    item_alerts='table.alert-list > tbody > tr.alert-item',
    btn_create_alert='#header-toolbar-alerts',
    dlg_create_alert_first_row_first_item='fieldset > div:nth-child(1) > span > div:nth-child(1)',
    options_dlg_create_alert_first_row_first_item='fieldset > div:nth-child(1) > span > div:nth-child(1) span.tv-control-select__option-wrap',
    exists_dlg_create_alert_first_row_second_item='div.js-condition-first-operand-placeholder div.tv-alert-dialog__group-item--right > span > span',
    dlg_create_alert_first_row_second_item='div.js-condition-first-operand-placeholder div.tv-alert-dialog__group-item--right > span',
    options_dlg_create_alert_first_row_second_item='div.js-condition-first-operand-placeholder div.tv-alert-dialog__group-item--right span.tv-control-select__option-wrap',
    dlg_create_alert_second_row='fieldset > div:nth-child(2) > span',
    options_dlg_create_alert_second_row='fieldset > div:nth-child(2) > span span.tv-control-select__option-wrap',
    inputs_and_selects_create_alert_3rd_row_and_above='div.js-condition-second-operand-placeholder select, div.js-condition-second-operand-placeholder input',
    dlg_create_alert_3rd_row_group_item='div.js-condition-second-operand-placeholder div.tv-alert-dialog__group-item',
    options_dlg_create_alert_3rd_row_group_item='span.tv-control-select__dropdown.tv-dropdown-behavior__body.i-opened span.tv-control-select__option-wrap',
    selected_dlg_create_alert_3rd_row_group_item='span.tv-control-select__dropdown.tv-dropdown-behavior__body.i-opened > span > span > span:nth-child({0}) > span',
    checkbox_dlg_create_alert_frequency='div[data-title="{0}"]',
    # Notify on App
    clickable_dlg_create_alert_send_push='div.tv-alert-dialog__fieldset-value-item > label > span.tv-control-checkbox > input[name="send-push"] + span + span.tv-control-checkbox__ripple',
    # Show Popup
    clickable_dlg_create_alert_show_popup='div.tv-alert-dialog__fieldset-value-item > label > span.tv-control-checkbox > input[name="show-popup"] + span + span.tv-control-checkbox__ripple',
    # Send Email
    clickable_dlg_create_alert_send_email='div.tv-alert-dialog__fieldset-value-item > label > span.tv-control-checkbox > input[name="send-email"] + span + span.tv-control-checkbox__ripple',
    # Toggle more actions
    btn_toggle_more_actions='div.tv-alert-dialog__fieldset-wrapper-toggle.js-fieldset-wrapper-toggle',
    # Play Sound
    clickable_dlg_create_alert_play_sound='div.tv-alert-dialog__fieldset-value-item > label > span.tv-control-checkbox > input[name="play-sound"] + span + span.tv-control-checkbox__ripple',
    # Sound options
    dlg_create_alert_ringtone='div.js-sound-settings > div.tv-alert-dialog__group-item.tv-alert-dialog__group-item--left > span',
    options_dlg_create_alert_ringtone='div.js-sound-settings span.tv-control-select__dropdown.tv-dropdown-behavior__body.i-opened span.tv-control-select__option-wrap',
    dlg_create_alert_sound_duration='div.js-sound-settings > div.tv-alert-dialog__group-item.tv-alert-dialog__group-item--right > span',
    options_dlg_create_alert_sound_duration='div.js-sound-settings span.tv-control-select__dropdown.tv-dropdown-behavior__body.i-opened span.tv-control-select__option-wrap',
    # Send Email-to-SMS
    clickable_dlg_create_alert_send_email_to_sms='div.tv-alert-dialog__fieldset-value-item > label > span.tv-control-checkbox > input[name="send-sms"] + span + span.tv-control-checkbox__ripple',
    # Send SMS
    clickable_dlg_create_alert_send_sms='div.tv-alert-dialog__fieldset-value-item > label > span.tv-control-checkbox > input[name="send-true-sms"] + span + span.tv-control-checkbox__ripple',
    btn_dlg_create_alert_submit='div[data-name="submit"] > span.tv-button__loader',
    btn_alerts='div[data-name="alerts"]',
    btn_calendar='div[data-name="calendar"]',
    div_watchlist_item='div.symbol-list > div.symbol-list-item.success',
    signout='body > div.tv-main.tv-screener__standalone-main-container > div.tv-header K> div.tv-header__inner.tv-layout-width > div.tv-header__area.tv-header__area--right.tv-header__area--desktop > span.tv-dropdown-behavior.tv-header__dropdown.tv-header__dropdown--user.i-opened > '
            'span.tv-dropdown-behavior__body.tv-header__dropdown-body.tv-header__dropdown-body--fixwidth.i-opened > span:nth-child(13) > a',
    checkbox_dlg_create_alert_open_ended='div.tv-alert-dialog__fieldset-value-item--open-ended input',
    clickable_dlg_create_alert_open_ended='div.tv-alert-dialog__fieldset-value-item--open-ended span.tv-control-checkbox__label',
    btn_dlg_screenshot='#header-toolbar-screenshot',
    dlg_screenshot_url='div[class^="copyForm"] > div > input',
    dlg_screenshot_close='div[class^="dialog"] > div > span[class^="close"]',
    btn_watchlist_sort_symbol='div.symbol-list-header.sortable > div.header-symbol',
    # SCREENERS
    btn_filters='tv-screener-toolbar__button--filters',
    select_exchange='div.tv-screener-dialog__filter-field.js-filter-field.js-filter-field-exchange.tv-screener-dialog__filter-field--cat1.js-wrap.tv-screener-dialog__filter-field--active > '
                    'div.tv-screener-dialog__filter-field-content.tv-screener-dialog__filter-field-content--select.js-filter-field-_content > div > span',
    select_screener='div.tv-screener-toolbar__button.tv-screener-toolbar__button--with-options.tv-screener-toolbar__button--arrow-down.tv-screener-toolbar__button--with-state.apply-common-tooltip.common-tooltip-fixed.js-filter-sets.tv-dropdown-behavior__button',
    options_screeners='div.tv-screener-popup__item--presets > div.tv-dropdown-behavior__item',
    input_screener_search='div.tv-screener-table__search-query.js-search-query.tv-screener-table__search-query--without-description > input',
    # Strategy Tester
    tab_strategy_tester='#footer-chart-panel div[data-name=backtesting]',
    tab_strategy_tester_inactive='div[data-name="backtesting"][data-active="false"]',
    tab_strategy_tester_performance_summary='div.backtesting-select-wrapper > ul > li:nth-child(2)',
    btn_strategy_dialog='div.icon-button.backtesting-open-format-dialog',
    performance_overview_net_profit='div.report-data > div:nth-child(1) > strong',
    performance_overview_net_profit_percentage='div.report-data > div:nth-child(1) > p > span',
    performance_overview_total_closed_trades='div.report-data > div:nth-child(2) > strong',
    performance_overview_percent_profitable='div.report-data > div:nth-child(3) > strong',
    performance_overview_profit_factor='div.report-data > div:nth-child(4) > strong',
    performance_overview_max_drawdown='div.report-data > div:nth-child(5) > strong',
    performance_overview_max_drawdown_percentage='div.report-data > div:nth-child(5) > p > span',
    performance_overview_avg_trade='div.report-data > div:nth-child(6) > strong',
    performance_overview_avg_trade_percentage='div.report-data > div:nth-child(6) > p > span',
    performance_overview_avg_bars_in_trade='div.report-data > div:nth-child(7) > strong',
    performance_summary_net_profit='div.report-content.performance > div > table > tbody > tr:nth-child(1) > td:nth-child(2) > div:nth-child(1)',
    performance_summary_net_profit_percentage='div.report-content.performance > div > table > tbody > tr:nth-child(1) > td:nth-child(2) > div:nth-child(2) > span',
    performance_summary_total_closed_trades='div.report-content.performance > div > table > tbody > tr:nth-child(11) > td:nth-child(2)',
    performance_summary_percent_profitable='div.report-content.performance > div > table > tbody > tr:nth-child(15) > td:nth-child(2)',
    performance_summary_profit_factor='div.report-content.performance > div > table > tbody > tr:nth-child(7) > td:nth-child(2)',
    performance_summary_max_drawdown='div.report-content.performance > div > table > tbody > tr:nth-child(4) > td:nth-child(2) > div:nth-child(1)',
    performance_summary_max_drawdown_percentage='div.report-content.performance > div > table > tbody > tr:nth-child(4) > td:nth-child(2) > div:nth-child(2) > span',
    performance_summary_avg_trade='div.report-content.performance > div > table > tbody > tr:nth-child(16) > td:nth-child(2) > div:nth-child(1)',
    performance_summary_avg_trade_percentage='div.report-content.performance > div > table > tbody > tr:nth-child(16) > td:nth-child(2) > div:nth-child(2) > span',
    performance_summary_avg_bars_in_trade='div.report-content.performance > div > table > tbody > tr:nth-child(22) > td:nth-child(2)',
    # Indicator dialog
    indicator_dialog_tab_inputs='#overlap-manager-root div[class^="tab-"]:nth-child(1)',
    indicator_dialog_tab_properties='#overlap-manager-root div[class^="tab-"]:nth-child(2)',
    # indicator_dialog_tab_cells='#overlap-manager-root div[class^="content"] div[class^="cell-"] > div',
    indicator_dialog_tab_cells='#overlap-manager-root div[class^="content"] div[class^="cell-"]',
    indicator_dialog_tab_cell='#overlap-manager-root div[class^="content"] div[class^="cell-"]:nth-child({})',
    indicator_dialog_titles='#overlap-manager-root div[class^="content"] div[class*="first"] > div',
    indicator_dialog_checkbox_titles='#overlap-manager-root label[class^="checkbox"] span > span',
    indicator_dialog_checkbox='#overlap-manager-root label[class^="checkbox"] input:nth-child({})',
    indicator_dialog_value='#overlap-manager-root div[class^="content"] div[class*="last"] > div:nth-child({})',
    indicator_dialog_container='#overlap-manager-root div[class^="content"] div[class*="last"] div[class^="inputGroup"]',
    indicator_dialog_select_options='#overlap-manager-root div[class^="dropdown"] div[class^="item"]',
    btn_indicator_dialog_ok='#overlap-manager-root button[name="ok"]',
    active_chart_asset='div.chart-container.active div.pane-legend-line.main div.pane-legend-title__description',
    active_chart_interval='div.chart-container.active div.pane-legend-line.main div.pane-legend-title__interval',
    # User Menu
    btn_user_menu="span.tv-dropdown-behavior.tv-header__dropdown.tv-header__dropdown--user",
    btn_logout="a[href='#signout']",
)

class_selectors = dict(
    form_create_alert='js-alert-form',
    rows_screener_result='tv-screener-table__result-row',
)

name_selectors = dict(
    checkbox_dlg_create_alert_show_popup='show-popup',
    checkbox_dlg_create_alert_play_sound='play-sound',
    checkbox_dlg_create_alert_send_email='send-email',
    checkbox_dlg_create_alert_email_to_sms='send-sms',
    checkbox_dlg_create_alert_send_sms='send-true-sms',
    checkbox_dlg_create_alert_send_push='send-push'
)
config = tools.get_config()
mode = 'a'  # append
if config.getboolean('logging', 'clear_on_start_up'):
    mode = 'w'  # overwrite
log = tools.create_log(mode)
log.setLevel(20)

path_to_chromedriver = r"" + config.get('webdriver', 'path')
if os.path.exists(path_to_chromedriver):
    path_to_chromedriver = path_to_chromedriver.replace('.exe', '')
else:
    log.error("File {} does not exist".format(path_to_chromedriver))
    log.exception(FileNotFoundError)
    exit(0)

screenshot_dir = ''
if config.has_option('logging', 'screenshot_path'):
    screenshot_dir = config.get('logging', 'screenshot_path')
    if screenshot_dir != '':
        screenshot_dir = os.path.join(CURRENT_DIR, screenshot_dir)
    if not os.path.exists(screenshot_dir):
        # noinspection PyBroadException
        try:
            os.mkdir(screenshot_dir)
        except Exception as screenshot_error:
            log.info('No screenshot directory specified or unable to create it.')
            screenshot_dir = ''

if config.has_option('logging', 'max_screenshots_on_error'):
    MAX_SCREENSHOTS_ON_ERROR = config.getint('logging', 'max_screenshots_on_error')

WAIT_TIME_IMPLICIT = config.getfloat('webdriver', 'wait_time_implicit')
PAGE_LOAD_TIMEOUT = config.getfloat('webdriver', 'page_load_timeout')
CHECK_IF_EXISTS_TIMEOUT = config.getfloat('webdriver', 'check_if_exists_timeout')
DELAY_BREAK_MINI = config.getfloat('delays', 'break_mini')
DELAY_BREAK = config.getfloat('delays', 'break')
DELAY_SUBMIT_ALERT = config.getfloat('delays', 'submit_alert')
DELAY_CHANGE_SYMBOL = config.getfloat('delays', 'change_symbol')
DELAY_CLEAR_INACTIVE_ALERTS = config.getfloat('delays', 'clear_inactive_alerts')
if config.has_option('delays', 'screenshot_dialog'):
    DELAY_SCREENSHOT_DIALOG = config.getfloat('delays', 'screenshot_dialog')
if config.has_option('delays', 'screenshot'):
    DELAY_SCREENSHOT = config.getfloat('delays', 'screenshot')
if config.has_option('delays', 'keystroke'):
    DELAY_KEYSTROKE = 0.05
EXACT_CONDITIONS = config.getboolean('tradingview', 'exact_conditions')

RESOLUTION = '1920,1080'
if config.has_option('webdriver', 'resolution'):
    RESOLUTION = config.get('webdriver', 'resolution').strip(' ')


def close_all_popups(browser):
    for h in browser.window_handles[1:]:
        browser.switch_to.window(h)
        close_alerts(browser)
        browser.close()
    browser.switch_to.window(browser.window_handles[0])


def close_alerts(browser):
    try:
        alert = browser.switch_to.alert
        alert.accept()
    except NoAlertPresentException as e:
        log.debug(e)
    except Exception as e:
        log.exception(e)


def refresh(browser):
    log.info('refreshing browser')
    browser.refresh()
    # Switching to Alert
    close_alerts(browser)
    # Close the watchlist menu if it is open
    if find_element(browser, css_selectors['btn_watchlist_menu'], By.CSS_SELECTOR, False, 0.5):
        wait_and_click(browser, css_selectors['btn_watchlist_menu'])


def element_exists(dom, css_selector, delay=CHECK_IF_EXISTS_TIMEOUT):
    result = False
    try:
        element = find_element(dom, css_selector, By.CSS_SELECTOR, delay)
        result = type(element) is WebElement
    except NoSuchElementException:
        log.debug('No such element. CSS SELECTOR=' + css_selector)
    except Exception as element_exists_error:
        log.error(element_exists_error)
    finally:
        log.debug("{} ({})".format(str(result), css_selector))
        return result


def wait_and_click(browser, css_selector, delay=CHECK_IF_EXISTS_TIMEOUT):
    return WebDriverWait(browser, delay).until(
        ec.element_to_be_clickable((By.CSS_SELECTOR, css_selector))).click()


def wait_and_click_by_xpath(browser, xpath, delay=CHECK_IF_EXISTS_TIMEOUT):
    WebDriverWait(browser, delay).until(
        ec.element_to_be_clickable((By.XPATH, xpath))).click()


def wait_and_click_by_text(browser, tag, search_text, css_class='', delay=CHECK_IF_EXISTS_TIMEOUT):
    if type(css_class) is str and len(css_class) > 0:
        xpath = '//{0}[contains(text(), "{1}") and @class="{2}"]'.format(tag, search_text, css_class)
    else:
        xpath = '//{0}[contains(text(), "{1}")]'.format(tag, search_text)
    WebDriverWait(browser, delay).until(
        ec.element_to_be_clickable((By.XPATH, xpath))).click()


def wait_and_get(browser, css, delay=CHECK_IF_EXISTS_TIMEOUT):
    element = WebDriverWait(browser, delay).until(
        ec.element_to_be_clickable((By.CSS_SELECTOR, css)))
    return element


def wait_and_visible(browser, css, delay=CHECK_IF_EXISTS_TIMEOUT):
    element = WebDriverWait(browser, delay).until(
        ec.visibility_of_element_located((By.CSS_SELECTOR, css)))
    return element


def find_element(browser, locator, locator_strategy=By.CSS_SELECTOR, except_on_timeout=True, delay=CHECK_IF_EXISTS_TIMEOUT):
    if except_on_timeout:
        element = WebDriverWait(browser, delay).until(
            ec.presence_of_element_located((locator_strategy, locator)))
        return element
    else:
        # noinspection PyBroadException
        try:
            element = WebDriverWait(browser, delay).until(
                ec.presence_of_element_located((locator_strategy, locator)))
            return element
        except Exception as e:
            log.debug(e)
            return None


def find_elements(browser, locator, locator_strategy=By.CSS_SELECTOR, except_on_timeout=True, delay=CHECK_IF_EXISTS_TIMEOUT):
    if except_on_timeout:
        elements = WebDriverWait(browser, delay).until(
            ec.presence_of_all_elements_located((locator_strategy, locator)))
        return elements
    else:
        try:
            elements = WebDriverWait(browser, delay).until(
                ec.presence_of_all_elements_located((locator_strategy, locator)))
            return elements
        except TimeoutException as e:
            log.debug(e)
            return None


def set_timeframe(browser, timeframe):
    log.info('Setting timeframe to ' + timeframe)
    wait_and_click(browser, css_selectors['btn_timeframe'])
    css = css_selectors['options_timeframe']
    el_options = find_elements(browser, css)
    index = 0
    found = False
    while not found and index < len(el_options):
        if el_options[index].text == timeframe:
            el_options[index].click()
            found = True
        index += 1
    if not found:
        log.warning('Unable to set timeframe to ' + timeframe)
        raise ValueError

    if found:
        # TODO replace 'element.send_keys" with
        #  action = ActionChains(browser)
        #  action.send_keys(Keys.TAB)
        #  action.perform()
        html = find_element(browser, 'html', By.TAG_NAME)
        html.send_keys(MODIFIER_KEY + 's')
        time.sleep(DELAY_BREAK)

    return found


def get_interval(timeframe):
    """
    Get TV's short timeframe notation
    :param timeframe: String.
    :return: interval: Short timeframe notation if found, empty string otherwise.
    """
    match = re.search("(\\d+)\\s(\\w\\w\\w)", timeframe)
    interval = ""
    if match is None:
        log.warning("Cannot find match for timeframe '{}' with regex (\\d+)\\s(\\w\\w\\w). [0]".format(timeframe))
    else:
        try:
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
        except Exception as interval_exception:
            log.warning("Cannot find match for timeframe '{}' with regex (\\d+)\\s(\\w\\w\\w). [1]".format(timeframe))
            log.exception(interval_exception)
    return interval


def set_delays(chart):
    global WAIT_TIME_IMPLICIT
    global PAGE_LOAD_TIMEOUT
    global CHECK_IF_EXISTS_TIMEOUT
    global DELAY_BREAK_MINI
    global DELAY_BREAK
    global DELAY_SUBMIT_ALERT
    global DELAY_CLEAR_INACTIVE_ALERTS
    global DELAY_CHANGE_SYMBOL
    global DELAY_KEYSTROKE

    # set delays as defined within the chart with a fallback to the config file
    if 'wait_time_implicit' in chart and isinstance(chart['wait_time_implicit'], numbers.Real):
        WAIT_TIME_IMPLICIT = chart['wait_time_implicit']
    elif config.has_option('webdriver', 'wait_time_implicit'):
        WAIT_TIME_IMPLICIT = config.getfloat('webdriver', 'wait_time_implicit')

    if 'page_load_timeout' in chart and isinstance(chart['page_load_timeout'], numbers.Real):
        PAGE_LOAD_TIMEOUT = chart['page_load_timeout']
    elif config.has_option('webdriver', 'page_load_timeout'):
        PAGE_LOAD_TIMEOUT = config.getfloat('webdriver', 'page_load_timeout')

    if 'check_if_exists_timeout' in chart and isinstance(chart['check_if_exists_timeout'], numbers.Real):
        CHECK_IF_EXISTS_TIMEOUT = chart['check_if_exists_timeout']
    elif config.has_option('webdriver', 'check_if_exists_timeout'):
        CHECK_IF_EXISTS_TIMEOUT = config.getfloat('webdriver', 'check_if_exists_timeout')

    if 'delays' in chart and isinstance(chart['delays'], dict):
        delays = chart['delays']

        if 'change_symbol' in delays and isinstance(delays['change_symbol'], numbers.Real):
            DELAY_CHANGE_SYMBOL = delays['change_symbol']
        elif config.has_option('delays', 'change_symbol'):
            DELAY_CHANGE_SYMBOL = config.getfloat('delays', 'change_symbol')
        if 'submit_alert' in delays and isinstance(delays['submit_alert'], numbers.Real):
            DELAY_SUBMIT_ALERT = delays['submit_alert']
        elif config.has_option('delays', 'submit_alert'):
            DELAY_SUBMIT_ALERT = config.getfloat('delays', 'submit_alert')
        if 'break' in delays and isinstance(delays['break'], numbers.Real):
            DELAY_BREAK = delays['break']
        elif config.has_option('delays', 'break'):
            DELAY_BREAK = config.getfloat('delays', 'break')
        if 'break_mini' in delays and isinstance(delays['break_mini'], numbers.Real):
            DELAY_BREAK_MINI = delays['break_mini']
        elif config.has_option('delays', 'break_mini'):
            DELAY_BREAK_MINI = config.getfloat('delays', 'break_mini')
        if 'clear_inactive_alerts' in delays and isinstance(delays['clear_inactive_alerts'], numbers.Real):
            DELAY_CLEAR_INACTIVE_ALERTS = delays['clear_inactive_alerts']
        elif config.has_option('delays', 'clear_inactive_alerts'):
            DELAY_CLEAR_INACTIVE_ALERTS = config.getfloat('delays', 'clear_inactive_alerts')
        if 'keystroke' in delays and isinstance(delays['keystroke'], numbers.Real):
            DELAY_KEYSTROKE = delays['keystroke']
        elif config.has_option('delays', 'keystroke'):
            DELAY_KEYSTROKE = config.getfloat('delays', 'keystroke')


def get_indicator_values(browser, indicator, symbol, retry_number=0):
    result = []
    chart_index = -1
    pane_index = -1
    indicator_index = -1

    if 'chart_index' in indicator and str(indicator['chart_index']).isdigit():
        chart_index = indicator['chart_index']
    if 'pane_index' in indicator and str(indicator['pane_index']).isdigit():
        pane_index = indicator['pane_index']
    if 'indicator_index' in indicator and str(indicator['indicator_index']).isdigit():
        indicator_index = indicator['indicator_index']

    studies = []
    if indicator_index < 0:
        try:
            # css = '.chart-container > div.chart-container-border > div > table > tbody > tr:nth-child({}) > td.chart-markup-table.pane > div > div.pane-legend > div.study > span.pane-legend-line__wrap-description > div > div.pane-legend-title__description'
            css = 'div.chart-container.active tr:nth-child({}) .study .pane-legend-title__description'.format((pane_index+1) * 2 - 1)
            studies = find_elements(browser, css)
            for i, study in enumerate(studies):
                study_name = studies[i].text
                log.debug('Found '.format(study_name))
                if study_name.startswith(indicator['name']):
                    indicator_index = i
                    break
                try:
                    if str(study_name).lower().index('loading'):
                        time.sleep(0.1)
                        return retry_get_indicator_values(browser, indicator, symbol, retry_number)
                    if str(study_name).lower().index('compiling'):
                        time.sleep(0.1)
                        return retry_get_indicator_values(browser, indicator, symbol, retry_number)
                    if str(study_name).lower().index('error'):
                        time.sleep(0.1)
                        return retry_get_indicator_values(browser, indicator, symbol, retry_number)
                except ValueError:
                    pass
        except StaleElementReferenceException:
            log.debug('StaleElementReferenceException in studies')
            return retry_get_indicator_values(browser, indicator, symbol, retry_number)
        except TimeoutException:
            log.warning('timeout in finding studies')
            # return False which will force a browser refresh
            result = False
        except Exception as e:
            log.exception(e)
            return retry_get_indicator_values(browser, indicator, symbol, retry_number)
        # use css
    try:
        if 0 <= indicator_index < len(studies):
            css = '#header-toolbar-symbol-search'
            element = find_element(browser, css)
            action = ActionChains(browser)
            action.move_to_element_with_offset(element, 5, 5)
            action.perform()

            elem_values = find_elements(find_elements(find_elements(find_elements(browser, 'chart-container', By.CLASS_NAME)[chart_index], 'pane', By.CLASS_NAME)[pane_index], 'study', By.CLASS_NAME)[indicator_index], 'pane-legend-item-value', By.CLASS_NAME)
            for e in elem_values:
                result.append(e.text)
    except StaleElementReferenceException:
        log.debug('StaleElementReferenceException in values')
        return retry_get_indicator_values(browser, indicator, symbol, retry_number)
    except TimeoutException:
        log.warning('timeout in getting values', )
        # return False which will force a browser refresh
        result = False
    except Exception as e:
        log.exception(e)
        return retry_get_indicator_values(browser, indicator, symbol, retry_number)

    # values_read = False
    # for value in result:
    #     if value != 'n/a':
    #         values_read = True
    #         break
    if not result or (isinstance(result, list) and len(result) == 0):
        return retry_get_indicator_values(browser, indicator, symbol, retry_number)
    # log.info(result)
    return result


def retry_get_indicator_values(browser, indicator, symbol, retry_number=0):
    max_retries = config.getint('tradingview', 'create_alert_max_retries') * 10
    if config.has_option('tradingview', 'get_indicator_values_max_retries'):
        max_retries = config.getint('tradingview', 'get_indicator_values_max_retries')
    if retry_number < max_retries:
        return get_indicator_values(browser, indicator, symbol, retry_number + 1)


def is_indicator_triggered(indicator, values):
    # log.info(values)
    result = False
    try:
        if 'trigger' in indicator:
            comparison = '='
            lhs = ''
            rhs = ''

            if 'type' in indicator['trigger']:
                comparison = indicator['trigger']['type']
            if 'left-hand-side' in indicator['trigger']:
                if 'index' in indicator['trigger']['left-hand-side'] and str(indicator['trigger']['left-hand-side']['index']).isdigit():
                    ignore = []
                    if 'ignore' in indicator['trigger']['left-hand-side'] and isinstance(indicator['trigger']['left-hand-side']['ignore'], list):
                        ignore = indicator['trigger']['left-hand-side']['ignore']
                    index = int(indicator['trigger']['left-hand-side']['index'])
                    try:
                        if index < len(values) and not (values[index] in ignore):
                            lhs = values[index]
                    except IndexError:
                        log.exception('YAML value trigger -> left-hand-side -> index is out of range. Index is {} but must be between 0 and {}'.format(str(index), str(len(values)-1)))
                if not lhs and indicator['trigger']['left-hand-side']['value']:
                    lhs = indicator['trigger']['left-hand-side']['value']
            if 'right-hand-side' in indicator['trigger']:
                if 'index' in indicator['trigger']['right-hand-side'] and str(indicator['trigger']['right-hand-side']['index']).isdigit():
                    ignore = []
                    if 'ignore' in indicator['trigger']['right-hand-side'] and isinstance(indicator['trigger']['right-hand-side']['ignore'], list):
                        ignore = indicator['trigger']['right-hand-side']['ignore']
                    index = int(indicator['trigger']['right-hand-side']['index'])
                    try:
                        if index < len(values) and not (values[index] in ignore):
                            rhs = values[index]
                    except IndexError:
                        log.exception('YAML value trigger -> right-hand-side -> index is out of range. Index is {} but must be between 0 and {}'.format(str(index), str(len(values)-1)))
                if not rhs and indicator['trigger']['right-hand-side']['value']:
                    rhs = indicator['trigger']['right-hand-side']['value']

            if lhs and rhs:
                if comparison == '=':
                    result = lhs == rhs
                elif comparison == '!=':
                    result = lhs != rhs
                elif comparison == '>=':
                    result = lhs >= rhs
                elif comparison == '>':
                    result = lhs > rhs
                elif comparison == '<=':
                    result = lhs <= rhs
                elif comparison == '<':
                    result = lhs < rhs
            else:
                if not lhs:
                    lhs = 'undefined'
                if not rhs:
                    rhs = 'undefined'
            log.debug('({} {} {}) returned {}'.format(str(lhs), comparison, str(rhs), str(result)))

        else:
            log.debug('No trigger information found, returning True')
            result = True
    except Exception as e:
        log.exception(e)
    return result


def save_strategy_results(data, save_as):
    filename = "{}_{}.json".format(save_as, datetime.datetime.today().strftime('%Y%m%d_%H%M'))
    if not os.path.exists('output'):
        os.mkdir('output')
    filename = os.path.join('output', filename)
    with open(filename, 'w+') as file:
        file.write(data)


def open_chart(browser, chart, save_as, counter_alerts, total_alerts):
    """
    :param browser:
    :param chart:
    :param save_as:
    :param counter_alerts:
    :param total_alerts:
    :return:

    TODO:   remember original setting of opened chart, and place them back when finished
    """
    global SEARCH_FOR_WARNING
    SEARCH_FOR_WARNING = True
    try:
        # load the chart
        close_all_popups(browser)
        log.info("Opening chart " + chart['url'])

        # set wait times defined in chart
        set_delays(chart)
        log.info("WAIT_TIME_IMPLICIT = " + str(WAIT_TIME_IMPLICIT))
        log.info("PAGE_LOAD_TIMEOUT = " + str(PAGE_LOAD_TIMEOUT))
        log.info("CHECK_IF_EXISTS_TIMEOUT = " + str(CHECK_IF_EXISTS_TIMEOUT))
        log.info("DELAY_BREAK_MINI = " + str(DELAY_BREAK_MINI))
        log.info("DELAY_BREAK = " + str(DELAY_BREAK))
        log.info("DELAY_SUBMIT_ALERT = " + str(DELAY_SUBMIT_ALERT))
        log.info("DELAY_CHANGE_SYMBOL = " + str(DELAY_CHANGE_SYMBOL))
        log.info("DELAY_CLEAR_INACTIVE_ALERTS = " + str(DELAY_CLEAR_INACTIVE_ALERTS))
        log.info("DELAY_KEYSTROKE = " + str(DELAY_KEYSTROKE))

        url = unquote(chart['url'])
        browser.execute_script("window.open('" + url + "');")
        for handle in browser.window_handles[1:]:
            browser.switch_to.window(handle)

        wait_and_click(browser, css_selectors['btn_calendar'], 30)
        wait_and_click(browser, css_selectors['btn_watchlist_menu'])
        time.sleep(DELAY_WATCHLIST)
        # scrape the symbols for each watchlist
        dict_watchlist = dict()
        for i, watchlist in enumerate(chart['watchlists']):
            watchlist = chart['watchlists'][i]
            # open list of watchlists element
            log.info("Collecting symbols from watchlist " + watchlist)
            wait_and_click(browser, css_selectors['btn_watchlist_menu_menu'])

            # load watchlist
            watchlist_exists = False
            el_options = find_elements(browser, css_selectors['options_watchlist'])
            for option in el_options:
                if option.text == watchlist:
                    option.click()
                    watchlist_exists = True
                    log.debug('Watchlist \'' + watchlist + '\' found')
                    break

            if watchlist_exists:
                # wait until the list is loaded (unfortunately sorting doesn't get saved
                wait_and_click(browser, css_selectors['btn_watchlist_sort_symbol'])

                # extract symbols from watchlist
                symbols = []
                try:
                    dict_symbols = find_elements(browser, css_selectors['div_watchlist_item'], By.CSS_SELECTOR, True, 30)
                    for symbol in dict_symbols:
                        symbols.append(symbol.get_attribute('data-symbol-full'))
                        if len(symbols) >= config.getint('tradingview', 'max_symbols_per_watchlist'):
                            break
                    # symbols = list(sorted(set(symbols)))
                    log.info("{} symbols found for '{}'".format(str(len(dict_symbols)), watchlist))
                except Exception as e:
                    log.exception(e)
                    snapshot(browser)

                dict_watchlist[chart['watchlists'][i]] = symbols

        # close the watchlist menu to save some loading time
        wait_and_click(browser, css_selectors['btn_watchlist_menu'])

        if 'strategies' in chart:
            summaries = dict()
            for strategy in chart['strategies']:
                summaries[strategy['name']] = dict()
                for watchlist in chart['watchlists']:
                    symbols = dict_watchlist[watchlist]
                    summaries[strategy['name']][watchlist] = back_test(browser, strategy, symbols)

            # save the results
            log.info(json.dumps(summaries))
            match = re.search(r"([\w\-_]*)", save_as)
            if re.Match:
                filename = match.group(1)
            elif save_as == "":
                filename = "run"
            else:
                filename = save_as
            save_strategy_results(json.dumps(summaries, indent=4), filename)

        if 'alerts' in chart or 'signals' in chart:
            # time.sleep(5)
            # set the time frame
            for timeframe in chart['timeframes']:
                set_timeframe(browser, timeframe)
                time.sleep(DELAY_TIMEFRAME)

                # iterate over each symbol per watchlist
                for watchlist in chart['watchlists']:
                    log.info("Opening watchlist " + watchlist)
                    try:
                        number_of_windows = 2
                        symbols = dict_watchlist[watchlist]

                        # log.info(__name__)
                        if MULTI_THREADING:
                            batch_size = math.ceil(len(symbols) / number_of_windows)
                            batches = list(tools.chunks(symbols, batch_size))

                            browsers = dict()

                            if __name__ == 'tv.tv':
                                pool = Pool(number_of_windows)  # use all available cores, otherwise specify the number you want as an argument
                                for k, batch in enumerate(batches):
                                    batch = batches[k]
                                    if k == 0:
                                        browsers[k] = browser
                                    else:
                                        browsers[k] = get_browser_instance()
                                    result = pool.apply_async(process_symbols, args=(browser, chart, batch, timeframe, counter_alerts, total_alerts,))
                                    log.info(result)
                                    # [counter_alerts, total_alerts]
                                    # pool.apply_async(process_symbols, args=(browser, chart, batch, timeframe))
                                pool.close()
                                pool.join()
                        else:
                            [counter_alerts, total_alerts] = process_symbols(browser, chart, symbols, timeframe, counter_alerts, total_alerts)
                        # pickle.dump(browser, 'webdriver.instance')
                    except KeyError:
                        log.error(watchlist + " doesn't exist")
                        break
    except Exception as exc:
        log.exception(exc)
        snapshot(browser)
    return [counter_alerts, total_alerts]


def process_symbols(browser, chart, symbols, timeframe, counter_alerts, total_alerts):
    log.info(timeframe)
    # open each symbol within the watchlist
    for k, symbol in enumerate(symbols):
        use_space = False
        if k > 0:
            use_space = False
        [counter_alerts, total_alerts] = process_symbol(browser, chart, symbols[k], timeframe, counter_alerts, total_alerts, use_space)
    return [counter_alerts, total_alerts]


def process_symbol(browser, chart, symbol, timeframe, counter_alerts, total_alerts, use_space=False, retry_number=0):
    log.info(symbol)
    # change symbol
    try:
        # Try to browse through the watchlist using space instead of setting the symbol value
        if use_space:
            # TODO replace 'element.send_keys" with
            #  action = ActionChains(browser)
            #  action.send_keys(Keys.TAB)
            #  action.perform()
            html = find_element(browser, 'html', By.TAG_NAME)
            html.send_keys(Keys.SPACE)
        else:
            # might be useful for multi threading set the symbol by going to different url like this:
            # https://www.tradingview.com/chart/?symbol=BINANCE%3AAGIBTC
            input_symbol = find_element(browser, css_selectors['input_symbol'])
            set_value(browser, input_symbol, symbol)
            input_symbol.send_keys(Keys.ENTER)

        # instead of a fixed delay, do a delay until there are no longer 'loading' / 'error' indicators
        # time.sleep(DELAY_CHANGE_SYMBOL)
        # loaded = False
        # total_wait_time = 0
        # while not loaded and total_wait_time < DELAY_CHANGE_SYMBOL:
        #     css = '.study .pane-legend-title__description'
        #     studies = find_elements(browser, css)
        #     for i, study in enumerate(studies):
        #         study_name = studies[i].text
        #         try:
        #             if str(study_name).index('loading'):
        #                 time.sleep(0.1)
        #                 total_wait_time += 0.1
        #                 break
        #             if str(study_name).index('compiling'):
        #                 time.sleep(0.1)
        #                 total_wait_time += 0.1
        #                 break
        #             if str(study_name).index('error'):
        #                 time.sleep(0.1)
        #                 total_wait_time += 0.1
        #                 break
        #             loaded = True
        #             break
        #         except ValueError:
        #             loaded = True
        #             break
        # log.info('Loaded in {} seconds'.format(total_wait_time))

        # xpath_loading = "//*[matches(text(),'(loading|compiling)','i')]"
        # elem_loading = find_elements(browser, xpath_loading, By.XPATH, False, DELAY_CHANGE_SYMBOL)
        # while elem_loading and len(elem_loading) > 0:
        #     elem_loading = find_elements(browser, xpath_loading, By.XPATH, False, DELAY_CHANGE_SYMBOL)
        # try:
        #     if wait_and_visible(browser, 'span.tv-market-status--invalid--for-chart', 1):
        #         invalid.add(symbol)
        #         log.info('Invalid symbol')
        #         return [counter_alerts, total_alerts]
        # except TimeoutException:
        #     pass

    except Exception as err:
        log.debug('Unable to change to symbol')
        log.exception(err)
        snapshot(browser)

    # check for errors /

    try:
        if 'signals' in chart:
            for signal in chart['signals']:

                triggered = []
                indicators = signal['indicators']
                timestamp = time.time()

                data = dict()
                data['timestamp'] = timestamp
                data['date_utc'] = datetime.datetime.utcfromtimestamp(timestamp).strftime("%a, %d %b %Y %H:%M:%S") + ' +0000'
                data['date'] = datetime.datetime.fromtimestamp(timestamp).strftime("%a, %d %b %Y %H:%M:%S %z") + tools.get_timezone()
                data['timeframe'] = timeframe
                data['symbol'] = symbol
                [data['exchange'], data['ticker']] = str(symbol).split(':')
                data['name'] = signal['name']

                interval = get_interval(timeframe)
                data['interval'] = interval
                url = browser.current_url + '?symbol=' + symbol
                multi_time_frame_layout = False
                try:
                    multi_time_frame_layout = signal['multi_time_frame_layout']
                except KeyError:
                    if log.level == 10:
                        log.warn('charts: multi_time_frame_layout not set in yaml, defaulting to multi_time_frame_layout = no')
                if type(interval) is str and len(interval) > 0 and not multi_time_frame_layout:
                    url += '&interval=' + str(interval)
                data['url'] = url

                signal_triggered = True
                for m, indicator in enumerate(indicators):
                    indicator = indicators[m]
                    values = get_indicator_values(browser, indicator, symbol)
                    # if we can't find a value, process this symbol again until we hit max retries which at that point we assume that the symbol doesn't exist or only hav 'n/a' values is correct
                    if (not values) and retry_number < config.getint('tradingview', 'create_alert_max_retries'):
                        return retry_process_symbol(browser, chart, symbol, timeframe, counter_alerts, total_alerts, retry_number)
                    signal['indicators'][m]['values'] = values
                    indicator_triggered = is_indicator_triggered(indicator, values)
                    if not indicator_triggered:
                        signal_triggered = False
                        break
                    signal['indicators'][m]['triggered'] = indicator_triggered
                    triggered.append(indicator_triggered)
                    if 'data' in indicator:
                        for item in indicator['data']:
                            for _key in item:
                                if not (_key in data):
                                    if isinstance(item[_key], list):
                                        indices = item[_key]
                                        data[_key] = []
                                        for index in indices:
                                            if index < len(values):
                                                data[_key].append(values[index])
                                    else:
                                        index = item[_key]
                                        if index < len(values):
                                            data[_key] = values[index]
                    # use tab to put focus on the next layout
                    # TODO replace 'element.send_keys" with
                    #  action = ActionChains(browser)
                    #  action.send_keys(Keys.TAB)
                    #  action.perform()
                    html = find_element(browser, 'html', By.TAG_NAME)
                    html.send_keys(Keys.TAB)

                if signal_triggered:
                    signal['triggered'] = signal_triggered
                    screenshots = dict()
                    filenames = dict()
                    screenshots_url = []
                    asset = ''
                    for m in range(5):
                        try:
                            el_asset_name = find_element(browser, css_selectors['asset'])
                            asset = el_asset_name.text
                            break
                        except StaleElementReferenceException:
                            log.warning('Unable to retrieve asset name... trying again')
                            pass
                    try:
                        for m, screenshot_chart in enumerate(signal['include_screenshots_of_charts']):
                            screenshot_chart = unquote(signal['include_screenshots_of_charts'][m])
                            [screenshot_url, filename] = take_screenshot(browser, symbol, interval)
                            if screenshot_url != '':
                                screenshots[screenshot_chart] = screenshot_url
                                screenshots_url.append(screenshot_url)
                                if m == 0:
                                    data['screenshot'] = screenshot_url
                            if filename != '':
                                filenames[screenshot_chart] = filename
                    except ValueError as value_error:
                        log.exception(value_error)
                        snapshot(browser)
                    except KeyError:
                        if log.level == 10:
                            log.warn('charts: include_screenshots_of_charts not set in yaml, defaulting to default screenshot')
                    data['screenshots_url'] = screenshots_url
                    data['screenshots'] = screenshots
                    data['filenames'] = filenames
                    data['asset'] = asset
                    if 'labels' in signal:
                        for label in signal['labels']:
                            for _key in label:
                                if not (_key in data):
                                    data[_key] = label[_key]
                    data['signal'] = signal
                    log.info('"{}" triggered'.format(signal['name']))
                    # log.info(signal['indicators'][0]['values'])
                    triggered_signals.append(data)
                total_alerts += 1

        if 'alerts' in chart:
            interval = get_interval(timeframe)
            for alert in chart['alerts']:
                if counter_alerts >= config.getint('tradingview', 'max_alerts') and config.getboolean('tradingview', 'clear_inactive_alerts'):
                    # try clean inactive alerts first
                    # open alerts tab
                    if not find_element(browser, css_selectors['btn_alert_menu'], By.CSS_SELECTOR, False):
                        wait_and_click(browser, css_selectors['btn_alerts'])
                    time.sleep(DELAY_CLEAR_INACTIVE_ALERTS)
                    wait_and_click(browser, css_selectors['btn_alert_menu'])
                    wait_and_click(browser, css_selectors['item_clear_inactive_alerts'])
                    wait_and_click(browser, css_selectors['btn_dlg_clear_alerts_confirm'])
                    time.sleep(DELAY_BREAK * 8)
                    # update counter
                    alerts = find_elements(browser, css_selectors['item_alerts'])
                    if type(alerts) is list:
                        counter_alerts = len(alerts)
                    # close alerts tab
                    if find_element(browser, css_selectors['btn_alert_menu'], By.CSS_SELECTOR, False):
                        wait_and_click(browser, css_selectors['btn_alerts'])

                if counter_alerts >= config.getint('tradingview', 'max_alerts'):
                    log.warning("Maximum alerts reached. You can set this to a higher number in the kairos.cfg. Exiting program.")
                    return [counter_alerts, total_alerts]
                try:
                    screenshot_url = ''
                    if config.has_option('logging', 'screenshot_timing') and config.get('logging', 'screenshot_timing') == 'alert':
                        screenshot_url = take_screenshot(browser, symbol, interval)[0]
                    create_alert(browser, alert, timeframe, interval, symbol, screenshot_url)
                    counter_alerts += 1
                    total_alerts += 1
                except Exception as err:
                    log.error("Could not set alert: {} {}".format(symbol, alert['name']))
                    log.exception(err)
                    snapshot(browser)
    except Exception as e:
        log.exception(e)
        return retry_process_symbol(browser, chart, symbol, timeframe, counter_alerts, total_alerts, retry_number)
    return [counter_alerts, total_alerts]


def retry_process_symbol(browser, chart, symbol, timeframe, counter_alerts, total_alerts, retry_number=0):
    if retry_number < config.getint('tradingview', 'create_alert_max_retries'):
        log.info('trying again ({})'.format(str(retry_number + 1)))
        refresh(browser)
        try:
            # might be useful for multi threading set the symbol by going to different url like this:
            # https://www.tradingview.com/chart/?symbol=BINANCE%3AAGIBTC
            input_symbol = find_element(browser, css_selectors['input_symbol'])
            set_value(browser, input_symbol, symbol)
            input_symbol.send_keys(Keys.ENTER)
            # time.sleep(DELAY_CHANGE_SYMBOL)
        except Exception as err:
            log.debug('Unable to change to symbol')
            log.exception(err)
            snapshot(browser)
        return process_symbol(browser, chart, symbol, timeframe, counter_alerts, total_alerts, False, retry_number + 1)
    else:
        log.error('Max retries reached.')
        snapshot(browser)
        return False


def snapshot(browser, quit_program=False, name=''):
    global MAX_SCREENSHOTS_ON_ERROR
    if config.has_option('logging', 'screenshot_on_error') and config.getboolean('logging', 'screenshot_on_error') and MAX_SCREENSHOTS_ON_ERROR > 0:
        MAX_SCREENSHOTS_ON_ERROR -= 1
        filename = datetime.datetime.now().strftime('%Y%m%d_%H%M%S') + '.png'
        if name:
            filename = '{}_{}'.format(str(name), filename)
        if not os.path.exists('log'):
            os.mkdir('log')
        filename = os.path.join('log', filename)

        try:
            element = find_element(browser, 'html')
            location = element.location
            size = element.size
            browser.save_screenshot(filename)
            offset_left, offset_right, offset_top, offset_bottom = [0, 0, 0, 0]
            if config.has_option('logging', 'screenshot_offset_left'):
                offset_left = config.getint('logging', 'screenshot_offset_right')
            if config.has_option('logging', 'screenshot_offset_right'):
                offset_right = config.getint('logging', 'screenshot_offset_top')
            if config.has_option('logging', 'screenshot_offset_top'):
                offset_top = config.getint('logging', 'screenshot_offset_left')
            if config.has_option('logging', 'screenshot_offset_bottom'):
                offset_bottom = config.getint('logging', 'screenshot_offset_bottom')
            x = location['x'] + offset_left
            y = location['y'] + offset_top
            width = location['x'] + size['width'] + offset_right
            height = location['y'] + size['height'] + offset_bottom
            im = Image.open(filename)
            im = im.crop((int(x), int(y), int(width), int(height)))
            im.save(filename)
            log.error(str(filename))
        except Exception as take_screenshot_error:
            log.exception(take_screenshot_error)
        if quit_program:
            write_console_log(browser)
            exit(errno.EFAULT)


def take_screenshot(browser, symbol, interval, retry_number=0):
    """
    Use selenium for a screenshot, or alternatively use TradingView's screenshot feature
    :param browser:
    :param symbol:
    :param interval:
    :param retry_number:
    :return:
    """
    screenshot_url = ''
    filename = ''

    try:

        if config.has_option('tradingview', 'tradingview_screenshot') and config.getboolean('tradingview', 'tradingview_screenshot'):
            # TODO replace 'element.send_keys" with
            #  action = ActionChains(browser)
            #  action.send_keys(Keys.TAB)
            #  action.perform()
            html = find_element(browser, 'html')
            html.send_keys(Keys.ALT + "s")
            time.sleep(DELAY_SCREENSHOT_DIALOG)
            input_screenshot_url = find_element(html, css_selectors['dlg_screenshot_url'])
            screenshot_url = input_screenshot_url.get_attribute('value')
            # TODO replace 'element.send_keys" with
            #  action = ActionChains(browser)
            #  action.send_keys(Keys.TAB)
            #  action.perform()
            html.send_keys(Keys.ESCAPE)
            log.debug(screenshot_url)

        elif screenshot_dir != '':
            chart_dir = ''
            match = re.search("^.*chart.(\\w+).*", browser.current_url)
            if re.Match:
                today_dir = os.path.join(screenshot_dir, datetime.datetime.today().strftime('%Y%m%d'))
                if not os.path.exists(today_dir):
                    os.mkdir(today_dir)
                chart_dir = os.path.join(today_dir, match.group(1))
                if not os.path.exists(chart_dir):
                    os.mkdir(chart_dir)
                chart_dir = os.path.join(chart_dir, )
            filename = symbol.replace(':', '_') + '_' + str(interval) + '.png'
            filename = os.path.join(chart_dir, filename)
            elem_chart = find_elements(browser, 'layout__area--center', By.CLASS_NAME)
            time.sleep(DELAY_SCREENSHOT)

            location = elem_chart.location
            size = elem_chart.size
            browser.save_screenshot(filename)
            offset_left, offset_right, offset_top, offset_bottom = [0, 0, 0, 0]
            if config.has_option('logging', 'screenshot_offset_left'):
                offset_left = config.getint('logging', 'screenshot_offset_right')
            if config.has_option('logging', 'screenshot_offset_right'):
                offset_right = config.getint('logging', 'screenshot_offset_top')
            if config.has_option('logging', 'screenshot_offset_top'):
                offset_top = config.getint('logging', 'screenshot_offset_left')
            if config.has_option('logging', 'screenshot_offset_bottom'):
                offset_bottom = config.getint('logging', 'screenshot_offset_bottom')
            x = location['x'] + offset_left
            y = location['y'] + offset_top
            width = location['x'] + size['width'] + offset_right
            height = location['y'] + size['height'] + offset_bottom
            im = Image.open(filename)
            im = im.crop((int(x), int(y), int(width), int(height)))
            im.save(filename)

            log.debug(filename)

    except Exception as take_screenshot_error:
        log.exception(take_screenshot_error)
        return retry_take_screenshot(browser, symbol, interval, retry_number)
    if screenshot_url == '' and filename == '':
        return retry_take_screenshot(browser, symbol, interval, retry_number)

    return [screenshot_url, filename]


def retry_take_screenshot(browser, symbol, interval, retry_number=0):

    if retry_number + 1 == config.getint('tradingview', 'create_alert_max_retries'):
        log.info('trying again ({})'.format(str(retry_number + 1)))
        refresh(browser)
        try:
            input_symbol = find_element(browser, css_selectors['input_symbol'])
            set_value(browser, input_symbol, symbol)
            input_symbol.send_keys(Keys.ENTER)
            # time.sleep(DELAY_CHANGE_SYMBOL)
        except Exception as e:
            log.exception(e)
    elif retry_number < config.getint('tradingview', 'create_alert_max_retries'):
        log.info('trying again ({})'.format(str(retry_number + 1)))
        return take_screenshot(browser, symbol, interval, retry_number + 1)
    else:
        log.warn('max retries reached')
        snapshot(browser)


def create_alert(browser, alert_config, timeframe, interval, symbol, screenshot_url='', retry_number=0):
    """
    Create an alert based upon user specified yaml configuration.
    :param browser:         The webdriver.
    :param alert_config:    The config for this specific alert.
    :param timeframe:       Timeframe, e.g. 1 day, 2 days, 4 hours, etc.
    :param interval:        TV's short format, e.g. 2 weeks = 2W, 1 day = 1D, 4 hours =4H, 5 minutes = 5M.
    :param symbol:          Ticker / Symbol, e.g. COINBASE:BTCUSD.
    :param screenshot_url:  URL of TV's screenshot feature
    :param retry_number:    Optional. Number of retries if for some reason the alert wasn't created.
    :return: true, if successful
    """
    global alert_dialog
    global SEARCH_FOR_WARNING
    try:
        if retry_number == 0:
            # TODO replace 'element.send_keys" with
            #  action = ActionChains(browser)
            #  action.send_keys(Keys.TAB)
            #  action.perform()
            html = find_element(browser, 'html')
            html.send_keys(Keys.ALT + "a")
        else:
            wait_and_click(browser, css_selectors['btn_create_alert'])
        # time.sleep(DELAY_BREAK)
        alert_dialog = find_element(browser, class_selectors['form_create_alert'], By.CLASS_NAME)
        log.debug(str(len(alert_config['conditions'])) + ' yaml conditions found')

        # 1st row, 1st condition
        current_condition = 0
        css_1st_row_left = css_selectors['dlg_create_alert_first_row_first_item']
        try:
            wait_and_click(alert_dialog, css_1st_row_left)
        except Exception as alert_err:
            log.exception(alert_err)
            return retry(browser, alert_config, timeframe, interval, symbol, screenshot_url, retry_number)

        el_options = find_elements(alert_dialog, css_selectors['options_dlg_create_alert_first_row_first_item'])
        if not select(alert_config, current_condition, el_options, symbol):
            return False

        # 1st row, 2nd condition (if applicable)
        css_1st_row_right = css_selectors['exists_dlg_create_alert_first_row_second_item']
        if element_exists(alert_dialog, css_1st_row_right, 0.5):
            current_condition += 1
            wait_and_click(alert_dialog, css_selectors['dlg_create_alert_first_row_second_item'])
            el_options = find_elements(alert_dialog, css_selectors['options_dlg_create_alert_first_row_second_item'])
            if not select(alert_config, current_condition, el_options, symbol):
                return False

        # 2nd row, 1st condition
        current_condition += 1
        css_2nd_row = css_selectors['dlg_create_alert_second_row']
        wait_and_click(alert_dialog, css_2nd_row)
        el_options = find_elements(alert_dialog, css_selectors['options_dlg_create_alert_second_row'])
        if not select(alert_config, current_condition, el_options, symbol):
            return False

        # 3rd+ rows, remaining conditions
        current_condition += 1
        i = 0
        while current_condition < len(alert_config['conditions']):
            time.sleep(DELAY_BREAK_MINI)
            log.debug('setting condition {0} to {1}'.format(str(current_condition + 1), alert_config['conditions'][current_condition]))
            # we need to get the inputs again for every iteration as the number may change
            inputs = find_elements(alert_dialog, css_selectors['inputs_and_selects_create_alert_3rd_row_and_above'])
            while True:
                if inputs[i].get_attribute('type') == 'hidden':
                    i += 1
                else:
                    break

            if inputs[i].tag_name == 'select':
                elements = find_elements(alert_dialog, css_selectors['dlg_create_alert_3rd_row_group_item'])
                if not ((elements[i].text == alert_config['conditions'][current_condition]) or ((not EXACT_CONDITIONS) and elements[i].text.startswith(alert_config['conditions'][current_condition]))):
                    elements[i].click()
                    time.sleep(DELAY_BREAK_MINI)

                    el_options = find_elements(elements[i], css_selectors['options_dlg_create_alert_3rd_row_group_item'])
                    condition_yaml = str(alert_config['conditions'][current_condition])
                    found = False
                    for j, option in enumerate(el_options):
                        option = el_options[j]
                        option_tv = str(option.get_attribute("innerHTML")).strip()
                        if (option_tv == condition_yaml) or ((not EXACT_CONDITIONS) and option_tv.startswith(condition_yaml)):
                            wait_and_click(alert_dialog, css_selectors['selected_dlg_create_alert_3rd_row_group_item'].format(j + 1))
                            found = True
                            break
                    if not found:
                        log.error("Invalid condition ({}): '{}' in yaml definition '{}'. Did the title/name of the indicator/condition change?".format(str(current_condition + 1), alert_config['conditions'][current_condition], alert_config['name']))
                        return False
            elif inputs[i].tag_name == 'input':
                set_value(browser, inputs[i], str(alert_config['conditions'][current_condition]).strip())

            # give some time
            current_condition += 1
            i += 1

        # Options (i.e. frequency)
        wait_and_click(alert_dialog, css_selectors['checkbox_dlg_create_alert_frequency'].format(str(alert_config['options']).strip()))
        # Expiration
        set_expiration(browser, alert_dialog, alert_config)

        # Toggle 'more actions'
        wait_and_click(alert_dialog, css_selectors['btn_toggle_more_actions'])

        # Show popup
        checkbox = find_element(alert_dialog, name_selectors['checkbox_dlg_create_alert_show_popup'], By.NAME)
        if is_checkbox_checked(checkbox) != alert_config['show_popup']:
            wait_and_click(alert_dialog, css_selectors['clickable_dlg_create_alert_show_popup'])

        # Sound
        checkbox = find_element(alert_dialog, name_selectors['checkbox_dlg_create_alert_play_sound'], By.NAME)
        if is_checkbox_checked(checkbox) != alert_config['sound']['play']:
            wait_and_click(alert_dialog, css_selectors['clickable_dlg_create_alert_play_sound'])
        if is_checkbox_checked(checkbox):
            # set ringtone
            wait_and_click(alert_dialog, css_selectors['dlg_create_alert_ringtone'])
            el_options = find_elements(alert_dialog, css_selectors['options_dlg_create_alert_ringtone'])
            for option in el_options:
                if str(option.text).strip() == str(alert_config['sound']['ringtone']).strip():
                    option.click()
            # set duration
            wait_and_click(alert_dialog, css_selectors['dlg_create_alert_sound_duration'])
            el_options = find_elements(alert_dialog, css_selectors['options_dlg_create_alert_sound_duration'])
            for option in el_options:
                if str(option.text).strip() == str(alert_config['sound']['duration']).strip():
                    option.click()

        # Communication options
        # Send Email
        try:
            checkbox = find_element(alert_dialog, name_selectors['checkbox_dlg_create_alert_send_email'], By.NAME)
            if is_checkbox_checked(checkbox) != alert_config['send']['email']:
                wait_and_click(alert_dialog, css_selectors['clickable_dlg_create_alert_send_email'])
            # Send Email-to-SMS (the checkbox is indeed called 'send-sms'!)
            checkbox = find_element(alert_dialog, name_selectors['checkbox_dlg_create_alert_email_to_sms'], By.NAME)
            if is_checkbox_checked(checkbox) != alert_config['send']['email-to-sms']:
                wait_and_click(alert_dialog, css_selectors['clickable_dlg_create_alert_send_email_to_sms'])
            # Send SMS (only for premium members)
            checkbox = find_element(alert_dialog, name_selectors['checkbox_dlg_create_alert_send_sms'], By.NAME)
            if is_checkbox_checked(checkbox) != alert_config['send']['sms']:
                wait_and_click(alert_dialog, css_selectors['clickable_dlg_create_alert_send_sms'])
            # Notify on App
            checkbox = find_element(alert_dialog, name_selectors['checkbox_dlg_create_alert_send_push'], By.NAME)
            if is_checkbox_checked(checkbox) != alert_config['send']['notify-on-app']:
                wait_and_click(alert_dialog, css_selectors['clickable_dlg_create_alert_send_push'])

            # Construct message
            chart = browser.current_url + '?symbol=' + symbol
            show_multi_chart_layout = False
            try:
                show_multi_chart_layout = alert_config['show_multi_chart_layout']
            except KeyError:
                log.warn('charts: multichartlayout not set in yaml, defaulting to multichartlayout = no')
            if type(interval) is str and len(interval) > 0 and not show_multi_chart_layout:
                chart += '&interval=' + str(interval)
            textarea = find_element(alert_dialog, 'description', By.NAME)
            """
            # This has stopped working. :( The text is visible but not set.           
            generated = textarea.text
            """
            # fall back to an empty generated text
            generated = ''
            text = str(alert_config['message']['text'])
            text = text.replace('%TIMEFRAME', ' ' + timeframe)
            text = text.replace('%SYMBOL', ' ' + symbol)
            text = text.replace('%NAME', ' ' + alert_config['name'])
            text = text.replace('%CHART', ' ' + chart)
            text = text.replace('%SCREENSHOT', ' ' + screenshot_url)
            text = text.replace('%GENERATED', generated)
            try:
                screenshot_urls = []
                for screenshot_chart in alert_config['include_screenshots_of_charts']:
                    screenshot_urls.append(str(screenshot_chart) + '?symbol=' + symbol)
                text += ' screenshots_to_include: ' + str(screenshot_urls).replace("'", "")
            except ValueError as value_error:
                log.exception(value_error)
                snapshot(browser)
            except KeyError:
                log.warn('charts: include_screenshots_of_charts not set in yaml, defaulting to default screenshot')
            set_value(browser, textarea, text, True)
        except Exception as alert_err:
            log.exception(alert_err)
            snapshot(browser)
            return retry(browser, alert_config, timeframe, interval, symbol, screenshot_url, retry_number)

        # Submit the form
        element = find_element(browser, css_selectors['btn_dlg_create_alert_submit'])
        element.click()
        # ignore warnings if they are there
        if SEARCH_FOR_WARNING:
            try:
                wait_and_click_by_xpath(browser, '//*[@id="overlap-manager-root"]/div[2]/div/span/div[1]/div/div[2]/div[2]/button', 30)
                log.info('Warning found and closed')
            except TimeoutException:
                # we are getting a timeout exception because there likely was no warning
                log.info('No warning found when setting the alert.')
                SEARCH_FOR_WARNING = False

        time.sleep(DELAY_SUBMIT_ALERT)
    except TimeoutError:
        log.warn('time out')
        # on except, refresh and try again
        return retry(browser, alert_config, timeframe, interval, symbol, screenshot_url, retry_number)
    except Exception as exc:
        log.exception(exc)
        snapshot(browser)
        # on except, refresh and try again
        return retry(browser, alert_config, timeframe, interval, symbol, screenshot_url, retry_number)

    return True


def select(alert_config, current_condition, el_options, ticker_id):
    log.debug('setting condition {0} to {1}'.format(str(current_condition + 1), alert_config['conditions'][current_condition]))
    value = str(alert_config['conditions'][current_condition])

    if value == "%SYMBOL":
        value = ticker_id.split(':')[1]

    found = False
    for option in el_options:
        option_tv = str(option.get_attribute("innerHTML")).strip()
        if (option_tv == value) or ((not EXACT_CONDITIONS) and option_tv.startswith(value)):
            option.click()
            found = True
            break
    if not found:
        log.error("Invalid condition ({}): '{}' in yaml definition '{}'. Did the title/name of the indicator/condition change?".format(str(current_condition + 1), alert_config['conditions'][current_condition], alert_config['name']))
    return found


def clear(element):
    element.clear()
    element.send_keys(MODIFIER_KEY + 'a')
    element.send_keys(Keys.BACKSPACE)
    time.sleep(DELAY_BREAK_MINI * 0.5)


def send_keys(element, string, interval=DELAY_KEYSTROKE):
    if interval == 0:
        element.send_keys(string)
    else:
        for char in string:
            element.send_keys(char)
            time.sleep(interval)


def set_value(browser, element, string, use_clipboard=False, use_send_keys=False, interval=DELAY_KEYSTROKE):
    if use_send_keys:
        send_keys(element, string, interval)
    else:

        browser.execute_script("arguments[0].value = '{}';".format(string), element)
        if use_clipboard:
            if config.getboolean('webdriver', 'clipboard'):
                element.send_keys(SELECT_ALL)
                element.send_keys(CUT)
                element.send_keys(PASTE)
            else:
                send_keys(element, string, interval)


def retry(browser, alert_config, timeframe, interval, symbol, screenshot_url, retry_number=0):
    if retry_number < config.getint('tradingview', 'create_alert_max_retries'):
        log.info('trying again ({})'.format(str(retry_number + 1)))
        refresh(browser)
        try:
            # change symbol
            input_symbol = find_element(browser, css_selectors['input_symbol'])
            set_value(browser, input_symbol, symbol)
            input_symbol.send_keys(Keys.ENTER)
            time.sleep(DELAY_CHANGE_SYMBOL)
        except Exception as err:
            log.debug("Can't find {} in list of symbols" + str(symbol))
            log.exception(err)
        return create_alert(browser, alert_config, timeframe, interval, symbol, screenshot_url, retry_number + 1)
    else:
        log.error('Max retries reached.')
        snapshot(browser)
        return False


def is_checkbox_checked(checkbox):
    checked = False
    try:
        checked = checkbox.get_attribute('checked') == 'true'
    finally:
        return checked


def set_expiration(browser, _alert_dialog, alert_config):
    max_minutes = 86400
    datetime_format = '%Y-%m-%d %H:%M'

    exp = alert_config['expiration']
    if type(exp) is int:
        alert_config['expiration'] = dict()
        alert_config['expiration']['time'] = exp
        alert_config['expiration']['open-ended'] = False
    else:
        if 'time' not in alert_config['expiration']:
            alert_config['expiration']['time'] = exp
        if 'open-ended' not in alert_config['expiration']:
            alert_config['expiration']['open-ended'] = False

    checkbox = find_element(_alert_dialog, css_selectors['checkbox_dlg_create_alert_open_ended'])
    if is_checkbox_checked(checkbox) != alert_config['expiration']['open-ended']:
        wait_and_click(_alert_dialog, css_selectors['clickable_dlg_create_alert_open_ended'])

    if alert_config['expiration']['open-ended'] or str(alert_config['expiration']['time']).strip() == '' or str(alert_config['expiration']['time']).strip().lower().startswith('n') or type(alert_config['expiration']['time']) is None:
        return
    elif type(alert_config['expiration']['time']) is int:
        target_date = datetime.datetime.now() + datetime.timedelta(minutes=float(alert_config['expiration']['time']))
    elif type(alert_config['expiration']['time']) is str and len(str(alert_config['expiration']['time']).strip()) > 0:
        target_date = datetime.datetime.strptime(str(alert_config['expiration']['time']).strip(), datetime_format)
    else:
        return

    max_expiration = datetime.datetime.now() + datetime.timedelta(minutes=float(max_minutes - 1440))
    if target_date > max_expiration:
        target_date = max_expiration
    date_value = target_date.strftime('%Y-%m-%d')
    time_value = target_date.strftime('%H:%M')

    # For some reason TV does not register setting the date value directly.
    # Furthermore, we need to make sure that the date and time inputs are cleared beforehand.
    input_date = find_element(alert_dialog, 'alert_exp_date', By.NAME)
    time.sleep(DELAY_BREAK_MINI)
    clear(input_date)
    set_value(browser, input_date, date_value, True)
    input_time = find_element(_alert_dialog, 'alert_exp_time', By.NAME)
    time.sleep(DELAY_BREAK_MINI)
    clear(input_time)
    set_value(browser, input_time, time_value, True)


def login(browser, uid='', pwd='', retry_login=False):
    global TV_UID
    global TV_PWD
    if uid == '' and config.has_option('tradingview', 'username'):
        uid = config.get('tradingview', 'username')
    if pwd == '' and config.has_option('tradingview', 'password'):
        pwd = config.get('tradingview', 'password')

    if not retry_login:
        try:
            url = 'https://www.tradingview.com'
            browser.get(url)
            try:
                res = RESOLUTION.split(',')
                if len(res) >= 2:
                    browser.set_window_size(res[0], res[1])
                    # log.info("resolution set to " + str(res[0]) + 'x' + str(res[1]))
            except Exception as e:
                log.debug(e)

            # if logged in under a different username or not logged in at all log out and then log in again
            try:
                elem_username = wait_and_visible(browser, css_selectors['username'], 5)
                if type(elem_username) is WebElement:
                    if elem_username.get_attribute('textContent') != '' and elem_username.get_attribute('textContent') == uid:
                        log.info("Already logged in")
                        return True
                    else:
                        log.info("Logged in under a different username. Logging out.")
                        wait_and_click(browser, css_selectors['username'])
                        wait_and_click(browser, css_selectors['signout'])
            except TimeoutException as e:
                log.debug(e)
            except Exception as e:
                log.exception(e)

        except Exception as e:
            log.exception(e)
            snapshot(browser, True)

    try:
        wait_and_click(browser, css_selectors['signin'])
        input_username = find_element(browser, css_selectors['input_username'])
        if input_username.get_attribute('value') == '' or retry_login:
            while uid == '':
                uid = input("Type your TradingView username and press enter: ")

        input_password = find_element(browser, css_selectors['input_password'])
        if input_password.get_attribute('value') == '' or retry_login:
            while pwd == '':
                pwd = getpass.getpass("Type your TradingView password and press enter: ")

        # set credentials on website login page
        if uid != '' and pwd != '':
            set_value(browser, input_username, uid)
            time.sleep(DELAY_BREAK_MINI)
            set_value(browser, input_password, pwd)
            time.sleep(DELAY_BREAK_MINI)
        # if there are no user credentials then exit
        else:
            log.info("No credentials provided.")
            write_console_log(browser)
            exit(0)

        wait_and_click(browser, css_selectors['btn_login'])

    except Exception as e:
        log.error(e)
        snapshot(browser, True)

    try:
        elem_username = wait_and_get(browser, css_selectors['username'])
        if type(elem_username) is WebElement and elem_username.get_attribute('textContent') != '' and elem_username.get_attribute('textContent') == uid:
            TV_UID = uid
            TV_PWD = pwd
            log.info("logged in successfully at tradingview.com as {}".format(elem_username.get_attribute('textContent')))
        else:
            if elem_username.get_attribute('textContent') == '' or elem_username.get_attribute('textContent') == 'Guest':
                log.warn("not logged in at tradingview.com")
            elif elem_username.get_attribute('textContent') != uid:
                log.warn("logged in under a different username at tradingview.com")
            error = find_element(browser, 'body > div.tv-dialog__modal-wrap > div > div > div > div.tv-dialog__error.tv-dialog__error--dark')
            if error:
                print(error.get_attribute('innerText'))
                login(browser, '', '', True)
    except Exception as e:
        log.error(e)
        snapshot(browser, True)


def create_browser(run_in_background):
    capabilities = DesiredCapabilities.CHROME.copy()

    options = webdriver.ChromeOptions()
    if OS == 'linux':
        options.add_argument('--no-sandbox')
        options.add_argument("--disable-dev-shm-usage")
    if config.has_option('webdriver', 'profile_path'):
        profile_path = config.get('webdriver', 'profile_path')
        if OS == 'windows':
            profile_path = str(profile_path).replace('\\', '\\\\')
        log.info(profile_path)
        options.add_argument('--user-data-dir=' + profile_path)
    # options.add_argument('--user-data-dir=C:\\PyCharm Projects\\Kairos\\profile')
    # options.add_argument('--user-data-dir=profile')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-notifications')
    options.add_argument('--noerrdialogs')
    options.add_argument('--disable-session-crashed-bubble')
    # options.add_argument('--disable-infobars')
    # options.add_argument('--disable-restore-session-state')
    options.add_argument('--window-size=' + RESOLUTION)
    # suppress the INFO:CONSOLE messages
    options.add_argument("--log-level=3")

    prefs = {
        'profile.default_content_setting_values.notifications': 2
        # , 'disk-cache-size': 52428800
    }
    options.add_experimental_option('prefs', prefs)
    exclude_switches = [
        'enable-automation',
    ]
    options.add_experimental_option('excludeSwitches', exclude_switches)
    # fix gpu_process_transport)factory.cc(980) error on Windows when in 'headless' mode, see:
    # https://stackoverflow.com/questions/50143413/errorgpu-process-transport-factory-cc1007-lost-ui-shared-context-while-ini
    if OS == 'windows':
        options.add_argument('--disable-gpu')
    # run chrome in the background
    if run_in_background:
        options.add_argument('--headless')
    browser = None

    chromedriver_file = r"" + str(config.get('webdriver', 'path'))
    if not os.path.exists(chromedriver_file):
        log.error("File {} does not exist. Did setup your kairos.cfg correctly?".format(chromedriver_file))
        raise FileNotFoundError
    chromedriver_file.replace('.exe', '')

    # use open chrome browser
    # options = webdriver.ChromeOptions()
    # options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

    try:
        # Create webdriver.remote
        # Note, we cannot serialize webdriver.Chrome
        if MULTI_THREADING:
            browser = webdriver.Remote(command_executor=EXECUTOR, options=options, desired_capabilities=capabilities)
        else:
            browser = webdriver.Chrome(executable_path=chromedriver_file, options=options, desired_capabilities=capabilities, service_args=["--verbose", "--log-path=.\\chromedriver.log"])
        browser.implicitly_wait(WAIT_TIME_IMPLICIT)
        browser.set_page_load_timeout(PAGE_LOAD_TIMEOUT)
    except WebDriverException as web_err:
        log.exception(web_err)
        exit(0)
    except Exception as e:
        log.exception(e)
        exit(0)

    return browser


def save_browser_state(browser):
    # Serialize and save on disk
    fp = open(FILENAME, 'wb')
    # pickle()
    dill.dump(browser, fp)
    fp.close()


def get_browser_instance(browser=None):
    result = browser
    if os.path.exists(FILENAME):
        result = dill.load(open(FILENAME, 'rb'))
    return result


def logout(browser):
    try:
        browser.switch_to.window(browser.window_handles[0])
        wait_and_click(browser, css_selectors['btn_user_menu'])
        wait_and_click(browser, css_selectors['btn_logout'])
        log.info("Logged out of TradingView")
    except Exception as e:
        log.exception(e)
        snapshot(browser)


def destroy_browser(browser):
    try:
        if type(browser) is webdriver.Chrome:
            close_all_popups(browser)
            logout(browser)
            write_console_log(browser)
    except Exception as e:
        log.exception(e)
        snapshot(browser)
    finally:
        browser.close()
        browser.quit()


def write_console_log(browser):
    write_mode = 'a'
    if config.getboolean('logging', 'clear_on_start_up'):
        write_mode = 'w'
    tools.write_console_log(browser, write_mode)


def run(file, export_signals_immediately, multi_threading=False):
    """
        TODO:   multi threading
    """
    counter_alerts = 0
    total_alerts = 0
    browser = None

    global RUN_IN_BACKGROUND
    global MULTI_THREADING
    MULTI_THREADING = multi_threading

    save_as = ""
    try:
        if len(file) > 1:
            head, tail = os.path.split(r""+file)
            save_as = tail
            file = r"" + os.path.join(config.get('tradingview', 'settings_dir'), file)
        else:
            file = r"" + os.path.join(config.get('tradingview', 'settings_dir'), config.get('tradingview', 'settings'))
        if not os.path.exists(file):
            log.error("File {} does not exist. Did you setup your kairos.cfg and yaml file correctly?".format(str(file)))
            raise FileNotFoundError

        # get the user defined yaml file
        tv = tools.get_yaml_config(file, log, True)
        has_charts = 'charts' in tv
        has_screeners = 'screeners' in tv

        RUN_IN_BACKGROUND = config.getboolean('webdriver', 'run_in_background')
        if 'webdriver' in tv and 'run-in-background' in tv['webdriver']:
            RUN_IN_BACKGROUND = tv['webdriver']['run-in-background']

        if has_screeners or has_charts:
            browser = create_browser(RUN_IN_BACKGROUND)
            login(browser, TV_UID, TV_PWD)
            if has_screeners:
                try:
                    screeners_yaml = tv['screeners']

                    for screener_yaml in screeners_yaml:
                        if (not ('enabled' in screener_yaml)) or screener_yaml['enabled']:
                            log.info("create/update watchlist '{}' from screener. Please be patient, this may take several minutes ...".format(screener_yaml['name']))
                            delay_after_update = 5
                            if 'delay_after_update' in screeners_yaml:
                                delay_after_update = screeners_yaml['delay_after_update']
                            markets = get_screener_markets(browser, screener_yaml)
                            if markets:
                                if update_watchlist(browser, screener_yaml['name'], markets, delay_after_update):
                                    log.info('watchlist {} updated ({} markets)'.format(screener_yaml['name'], str(len(markets))))
                            else:
                                log.info('no markets to update')
                except Exception as e:
                    log.exception(e)
                    snapshot(browser)

            if has_charts:
                # do some maintenance on the alert list (removing or restarting)
                try:
                    if config.getboolean('tradingview', 'clear_alerts'):
                        wait_and_click(browser, css_selectors['btn_calendar'])
                        wait_and_click(browser, css_selectors['btn_alerts'])
                        wait_and_click(browser, css_selectors['btn_alert_menu'])
                        wait_and_click(browser, css_selectors['item_clear_alerts'])
                        wait_and_click(browser, css_selectors['btn_dlg_clear_alerts_confirm'])
                        time.sleep(DELAY_BREAK * 2)
                    else:
                        if config.getboolean('tradingview', 'restart_inactive_alerts'):
                            wait_and_click(browser, css_selectors['btn_calendar'])
                            wait_and_click(browser, css_selectors['btn_alerts'])
                            wait_and_click(browser, css_selectors['btn_alert_menu'])
                            wait_and_click(browser, css_selectors['item_restart_inactive_alerts'])
                            wait_and_click(browser, css_selectors['btn_dlg_clear_alerts_confirm'])
                            time.sleep(DELAY_BREAK * 2)
                        elif config.getboolean('tradingview', 'clear_inactive_alerts'):
                            wait_and_click(browser, css_selectors['btn_calendar'])
                            wait_and_click(browser, css_selectors['btn_alerts'])
                            wait_and_click(browser, css_selectors['btn_alert_menu'])
                            wait_and_click(browser, css_selectors['item_clear_inactive_alerts'])
                            wait_and_click(browser, css_selectors['btn_dlg_clear_alerts_confirm'])
                            time.sleep(DELAY_BREAK * 2)
                        # count the number of existing alerts
                        alerts = find_elements(browser, css_selectors['item_alerts'], By.CSS_SELECTOR, False)
                        if isinstance(alerts, list):
                            counter_alerts = len(alerts)
                except Exception as e:
                    log.exception(e)
                # iterate over all items that have an 'alerts' or 'signals' property
                for file, items in tv.items():
                    if type(items) is list:
                        for item in items:
                            if 'alerts' in item or 'signals' in item or 'strategies' in item:
                                [counter_alerts, total_alerts] = open_chart(browser, item, save_as, counter_alerts, total_alerts)
                summary(total_alerts)
                if len(triggered_signals) > 0:
                    from tv import mail
                    mail.post_process_signals(triggered_signals)
                    if export_signals_immediately:
                        if 'summary' in tv:
                            mail.send_mail(browser, tv['summary'], triggered_signals, False)
                            # we've send the signals, let's make sure they aren't send a 2nd time
                            triggered_signals.clear()
                        else:
                            log.warn('No summary configuration found in {}. Unable to create a summary and to export data.'.format(str(file)))
                elif export_signals_immediately:
                    log.info('No signals triggered. Nothing to send')
                destroy_browser(browser)
    except Exception as exc:
        log.exception(exc)
        summary(total_alerts)
        destroy_browser(browser)
    return triggered_signals


def get_screener_markets(browser, screener_yaml):
    markets = []

    close_all_popups(browser)
    url = unquote(screener_yaml['url'])
    browser.get(url)
    time.sleep(DELAY_BREAK * 2)

    wait_and_click(browser, css_selectors['select_screener'])
    time.sleep(DELAY_BREAK_MINI)

    el_options = find_elements(browser, css_selectors['options_screeners'])
    time.sleep(DELAY_BREAK)
    found = False

    for option in el_options:
        if str(option.text) == screener_yaml['name']:
            option.click()
            found = True
            break

    if not found:
        log.warn("screener '{}' doesn't exist.".format(screener_yaml['name']))
        return False

    if 'search' in screener_yaml and screener_yaml['search'] != '':
        search_box = find_element(browser, css_selectors['input_screener_search'])
        set_value(browser, search_box, screener_yaml['search'], True)
        time.sleep(DELAY_SCREENER_SEARCH)

    el_total_found = find_element(browser, 'tv-screener-table__field-value--total', By.CLASS_NAME)
    match = re.search("(\\d+)", el_total_found.text)
    html = find_element(browser, 'html', By.TAG_NAME)
    chunck_size = 150

    scroll_delay = 2
    if 'scroll_delay' in screener_yaml and screener_yaml['scroll_delay'] != '':
        scroll_delay = screener_yaml['scroll_delay']

    if re.Match:
        number_of_scrolls = math.ceil(int(match.group(1)) / chunck_size) - 1
        for scroll in range(number_of_scrolls):
            for j in range(20):
                # TODO replace 'element.send_keys" with
                #  action = ActionChains(browser)
                #  action.send_keys(Keys.TAB)
                #  action.perform()
                html.send_keys(Keys.PAGE_DOWN)
                time.sleep(DELAY_BREAK_MINI)
            time.sleep(scroll_delay)

    rows = find_elements(browser, class_selectors['rows_screener_result'], By.CLASS_NAME)
    for i, row in enumerate(rows):
        try:
            market = rows[i].get_attribute('data-symbol')
        except StaleElementReferenceException:
            WebDriverWait(browser, 5).until(
                ec.presence_of_element_located((By.CLASS_NAME, class_selectors['rows_screener_result'])))
            # try again
            rows = find_elements(browser, class_selectors['rows_screener_result'], By.CLASS_NAME)
            market = rows[i].get_attribute('data-symbol')
        markets.append(market)

    # markets = list(sorted(set(markets)))
    markets = list(set(markets))
    log.debug('found {} unique markets'.format(str(len(markets))))
    return markets


def update_watchlist(browser, name, markets, delay_after_update):
    try:
        wait_and_click(browser, css_selectors['btn_calendar'])
        wait_and_click(browser, 'body > div.layout__area--right > div > div.widgetbar-tabs > div > div > div > div > div:nth-child(1)')
        time.sleep(DELAY_BREAK)
        wait_and_click(browser, 'body > div.layout__area--right > div > div.widgetbar-pages > div.widgetbar-pagescontent > div.widgetbar-page.active > div.widgetbar-widget.widgetbar-widget-watchlist > div.widgetbar-widgetheader > div.widgetbar-headerspace > a')
        time.sleep(DELAY_BREAK)

        input_symbol = find_element(browser, 'wl-symbol-edit', By.CLASS_NAME)

        if isinstance(markets, str):
            markets = markets.split(',')

        batches = list(tools.chunks(markets, 20))

        el_general_options = find_elements(browser, 'div.charts-popup-list > a.item.special')
        time.sleep(DELAY_BREAK)
        for option in el_general_options:
            if str(option.text).startswith('Create New'):
                option.click()
                break
        time.sleep(DELAY_BREAK)

        css = '#overlap-manager-root > div > div > div.tv-dialog__scroll-wrap.i-with-actions > div > div > div > label > input'
        input_watchlist_name = find_element(browser, css)
        set_value(browser, input_watchlist_name, name)
        input_watchlist_name.send_keys(Keys.ENTER)
        time.sleep(DELAY_BREAK)

        for batch in batches:
            csv = ",".join(batch)
            set_value(browser, input_symbol, csv)
            input_symbol.send_keys(Keys.ENTER)
            time.sleep(delay_after_update)

        # sort the watchlist
        try:
            wait_and_click(browser, css_selectors['btn_watchlist_sort_symbol'])
            time.sleep(DELAY_BREAK * 2)
        except Exception as e:
            log.exception(e)

        # remove double watchlist
        remove_watchlists(browser, name)
        return True
    except Exception as e:
        log.exception(e)
        snapshot(browser)


def remove_watchlists(browser, name):
    # After a watchlist is imported, TV opens it. Since we cannot delete a watchlist while opened, we can safely assume that any watchlist of the same name that can be deleted is old and should be deleted
    wait_and_click(browser, 'body > div.layout__area--right > div > div.widgetbar-pages > div.widgetbar-pagescontent > div.widgetbar-page.active > div.widgetbar-widget.widgetbar-widget-watchlist > div.widgetbar-widgetheader > div.widgetbar-headerspace > a')
    time.sleep(DELAY_BREAK)
    el_options = find_elements(browser, 'div.charts-popup-list > a.item.first:not(.active-item-backlight)')
    time.sleep(DELAY_BREAK)
    j = 0
    while j < len(el_options):
        try:
            if str(el_options[j].text) == name:
                btn_delete = find_element(el_options[j], 'icon-delete', By.CLASS_NAME)
                time.sleep(DELAY_BREAK)
                browser.execute_script("arguments[0].setAttribute('style','visibility:visible;');", btn_delete)
                time.sleep(DELAY_BREAK)
                btn_delete.click()
                # handle confirmation dialog
                wait_and_click(browser, 'div.js-dialog__action-click.js-dialog__no-drag.tv-button.tv-button--success')
                # give TV time to remove the watchlist
                time.sleep(DELAY_BREAK * 2)
                log.debug('watchlist {} removed'.format(name))
        except StaleElementReferenceException:
            # open the watchlists menu again and update the options to prevent 'element is stale' error
            wait_and_click(browser, 'body > div.layout__area--right > div > div.widgetbar-pages > div.widgetbar-pagescontent > div.widgetbar-page.active > div.widgetbar-widget.widgetbar-widget-watchlist > div.widgetbar-widgetheader > div.widgetbar-headerspace > a')
            time.sleep(DELAY_BREAK)
            el_options = find_elements(browser, 'div.charts-popup-list > a.item.first:not(.active-item-backlight)')
            time.sleep(DELAY_BREAK)
            j = 0
        except Exception as e:
            log.exception(e)
            snapshot(browser)
        j = j + 1


def back_test(browser, strategy_config, symbols):
    try:
        # open strategy tab
        strategy_tab = find_element(browser, css_selectors['tab_strategy_tester_inactive'], By.CSS_SELECTOR, False, 1)
        if isinstance(strategy_tab, WebElement):
            strategy_tab.click()

        # open performance summary tab
        max_tries = max(config.getint('tradingview', 'create_alert_max_retries'), 10)
        tries = 0
        while tries < max_tries:
            # noinspection PyBroadException
            try:
                strategy_performance_strategy_tab = find_element(browser, css_selectors['tab_strategy_tester_performance_summary'], By.CSS_SELECTOR, False, 1)
                if isinstance(strategy_tab, WebElement):
                    strategy_performance_strategy_tab.click()
                tries = max_tries
            except Exception:
                tries += 1

        summaries = []
        atomic_inputs = []
        atomic_properties = []
        name = strategy_config['name']

        # number_of_timeframes = 1
        # if 'timeframes' in strategy_config and isinstance(strategy_config['timeframes'], list):
        #     number_of_timeframes = len(strategy_config['timeframes'])
        try:
            css = 'div.chart-container'
            number_of_charts = find_elements(browser, css)
            number_of_charts = len(number_of_charts)
        except TimeoutException:
            number_of_charts = 1
        log.info("Found {} charts on the layout".format(number_of_charts))

        avg_change_symbol_time = 0.6 * number_of_charts
        avg_change_strategy_time = 4.5 * number_of_charts - avg_change_symbol_time
        factor = 1

        if 'inputs' in strategy_config:
            inputs = get_config_values(strategy_config['inputs'])
            # log.info(inputs)
            generate_atomic_values(inputs, atomic_inputs)
        if 'properties' in strategy_config:
            properties = get_config_values(strategy_config['properties'])
            # log.info(properties)
            generate_atomic_values(properties, atomic_properties)

        expected_minutes = ((max(len(atomic_inputs), 1) * max(len(atomic_properties), 1) * len(symbols) * avg_change_symbol_time) + (max(len(atomic_inputs), 1) * max(len(atomic_properties), 1) * avg_change_strategy_time)) * factor / 60
        expected_time = "{} minutes".format(math.ceil(expected_minutes))
        if expected_minutes > 90:
            expected_hours = expected_minutes / 60
            expected_time = "{} hours".format(math.ceil(expected_hours))
            if expected_hours > 48:
                expected_time = "{} days".format(math.ceil(expected_hours / 7))

        number_of_strategies = len(atomic_properties) * len(atomic_inputs)
        # Both inputs and properties have been defined
        if len(atomic_properties) > 0 and len(atomic_inputs) > 0:

            log.info("Back testing {} with {} input sets and {} property sets. Test expected to finish in {}.".format(name, len(atomic_inputs), len(atomic_properties), expected_time))
            for i, properties in enumerate(atomic_properties):
                for j, inputs in enumerate(atomic_inputs):
                    strategy_number = (i+1)*(j+1)
                    log.info("Strategy variant {}/{}".format(strategy_number, number_of_strategies))
                    strategy_summary = dict()
                    strategy_summary['inputs'] = inputs
                    strategy_summary['properties'] = properties
                    strategy_summary['results'] = back_test_strategy(browser, inputs, properties, symbols, strategy_config, number_of_charts)
                    summaries.append(strategy_summary)
        # Inputs have been defined. Run back test for each input with default properties
        elif len(atomic_inputs) > 0:
            log.info("Back testing {} with {} input sets and default property set. Test expected to finish in {}.".format(name, len(atomic_inputs), expected_time))
            for i, inputs in enumerate(atomic_inputs):
                log.info("Strategy variant {}/{}".format(i+1, number_of_strategies))
                strategy_summary = dict()
                strategy_summary['inputs'] = inputs
                strategy_summary['properties'] = []
                strategy_summary['results'] = back_test_strategy(browser, inputs, [], symbols, strategy_config, number_of_charts)
                summaries.append(strategy_summary)
        # Properties have been defined. Run back test for property with default inputs
        elif len(atomic_properties) > 0:
            log.info("Back testing {} with default input set and {} properties sets. Test expected to finish in {}.".format(name, len(atomic_properties), expected_time))
            for i, properties in enumerate(atomic_properties):
                log.info("Strategy variant {}/{}".format(i+1, number_of_strategies))
                strategy_summary = dict()
                strategy_summary['inputs'] = []
                strategy_summary['properties'] = properties
                strategy_summary['results'] = back_test_strategy(browser, [], properties, symbols, strategy_config, number_of_charts)
                summaries.append(strategy_summary)
        # Run just one back test with default inputs and properties
        else:
            log.info("Back testing {} with default input set and default property set. Test expected to finish in {}.".format(name, expected_time))
            strategy_summary = dict()
            strategy_summary['inputs'] = []
            strategy_summary['properties'] = []
            strategy_summary['results'] = back_test_strategy(browser, [], [], symbols, strategy_config, number_of_charts)
            summaries.append(strategy_summary)
        # log.info(summaries)
        # close strategy tab
        strategy_tab = find_element(browser, css_selectors['tab_strategy_tester_inactive'], By.CSS_SELECTOR, False, 1)
        if isinstance(strategy_tab, WebElement):
            strategy_tab.click()
        return summaries

    except ValueError as e:
        log.exception(e)


def back_test_strategy(browser, inputs, properties, symbols, strategy_config, number_of_charts):
    results = []
    input_locations = dict()
    property_locations = dict()
    averages = dict()
    symbol_averages = dict()
    max_tries = max(config.getint('tradingview', 'create_alert_max_retries'), 10)

    first_symbol = True
    intervals = []
    for symbol in symbols:
        input_symbol = find_element(browser, css_selectors['input_symbol'])
        set_value(browser, input_symbol, symbol)
        input_symbol.send_keys(Keys.ENTER)

        symbol_average = dict()
        symbol_average['Net Profit'] = 0
        symbol_average['Net Profit %'] = 0
        symbol_average['Closed Trades'] = 0
        symbol_average['Percent Profitable'] = 0
        symbol_average['Profit Factor'] = 0
        symbol_average['Max Drawdown'] = 0
        symbol_average['Max Drawdown %'] = 0
        symbol_average['Avg Trade'] = 0
        symbol_average['Avg Trade %'] = 0
        symbol_average['Avg # Bars In Trade'] = 0
        symbol_average['Counter'] = 0

        for chart_index in range(number_of_charts):

            # first time chart setup
            # - set inputs and properties of charts
            # - get interval of chart
            # - create a dict() for each interval and add it to averages
            if first_symbol:
                # set the strategy if there are inputs or properties defined
                if len(inputs) > 0 or len(properties) > 0:
                    # Select correct strategy on the chart, wait for it to be loaded and get current inputs and properties
                    select_strategy(browser, strategy_config, chart_index)
                    # open the strategy dialog and set the input & property values
                    format_strategy(browser, inputs, properties, input_locations, property_locations)

                interval = 'na'
                tries = 0
                while tries < max_tries:
                    try:
                        # element = find_element(browser, css_selectors['active_chart_interval'])
                        interval = repr(find_element(browser, css_selectors['active_chart_interval']).get_attribute('innerHTML')).replace(', ', '')
                        # interval = str(element.text).replace(', ', '')
                        tries = max_tries
                    except StaleElementReferenceException:
                        if interval == 'na':
                            tries += 1
                        else:
                            tries = max_tries
                    except Exception as e:
                        log.exception(e)
                        tries += 1
                intervals.append(interval)

                if not (interval in averages):
                    averages[interval] = dict()
                    averages[interval]['Net Profit'] = 0
                    averages[interval]['Net Profit %'] = 0
                    averages[interval]['Closed Trades'] = 0
                    averages[interval]['Percent Profitable'] = 0
                    averages[interval]['Profit Factor'] = 0
                    averages[interval]['Max Drawdown'] = 0
                    averages[interval]['Max Drawdown %'] = 0
                    averages[interval]['Avg Trade'] = 0
                    averages[interval]['Avg Trade %'] = 0
                    averages[interval]['Avg # Bars In Trade'] = 0
                    averages[interval]['Counter'] = 0

            wait_until_indicator_is_loaded(browser, strategy_config['name'], strategy_config['pane_index'])
            interval = intervals[chart_index]
            # log.info("{}: {}".format(symbol, interval))

            # Extract Strategy Tester result:
            result = dict()
            result['Symbol'] = symbol
            result['Interval'] = interval
            result['Net Profit'] = get_strategy_statistic(browser, css_selectors['performance_summary_net_profit'])
            result['Net Profit %'] = get_strategy_statistic(browser, css_selectors['performance_summary_net_profit_percentage'])
            result['Closed Trades'] = get_strategy_statistic(browser, css_selectors['performance_summary_total_closed_trades'])
            result['Percent Profitable'] = get_strategy_statistic(browser, css_selectors['performance_summary_percent_profitable'])
            result['Profit Factor'] = get_strategy_statistic(browser, css_selectors['performance_summary_profit_factor'])
            result['Max Drawdown'] = get_strategy_statistic(browser, css_selectors['performance_summary_max_drawdown'])
            result['Max Drawdown %'] = get_strategy_statistic(browser, css_selectors['performance_summary_max_drawdown_percentage'])
            result['Avg Trade'] = get_strategy_statistic(browser, css_selectors['performance_summary_avg_trade'])
            result['Avg Trade %'] = get_strategy_statistic(browser, css_selectors['performance_summary_avg_trade_percentage'])
            result['Avg # Bars In Trade'] = get_strategy_statistic(browser, css_selectors['performance_summary_avg_bars_in_trade'])

            # log.info("Data extracted")
            # log.info(result)
            # time.sleep(600)
            results.append(result)

            # add to averages
            if isinstance(result['Avg # Bars In Trade'], int):
                try:
                    symbol_average['Net Profit'] += float(result['Net Profit'])
                    symbol_average['Net Profit %'] += float(result['Net Profit %'])
                    symbol_average['Closed Trades'] += int(result['Closed Trades'])
                    symbol_average['Percent Profitable'] += float(result['Percent Profitable'])
                    symbol_average['Profit Factor'] += float(result['Profit Factor'])
                    symbol_average['Max Drawdown'] += float(result['Max Drawdown'])
                    symbol_average['Max Drawdown %'] += float(result['Max Drawdown %'])
                    symbol_average['Avg Trade'] += float(result['Avg Trade'])
                    symbol_average['Avg Trade %'] += float(result['Avg Trade %'])
                    symbol_average['Avg # Bars In Trade'] += int(result['Avg # Bars In Trade'])
                    symbol_average['Counter'] += 1

                    averages[interval]['Net Profit'] += float(result['Net Profit'])
                    averages[interval]['Net Profit %'] += float(result['Net Profit %'])
                    averages[interval]['Closed Trades'] += int(result['Closed Trades'])
                    averages[interval]['Percent Profitable'] += float(result['Percent Profitable'])
                    averages[interval]['Profit Factor'] += float(result['Profit Factor'])
                    averages[interval]['Max Drawdown'] += float(result['Max Drawdown'])
                    averages[interval]['Max Drawdown %'] += float(result['Max Drawdown %'])
                    averages[interval]['Avg Trade'] += float(result['Avg Trade'])
                    averages[interval]['Avg Trade %'] += float(result['Avg Trade %'])
                    averages[interval]['Avg # Bars In Trade'] += int(result['Avg # Bars In Trade'])
                    averages[interval]['Counter'] += 1
                except Exception as e:
                    log.exception(e)

            # Focus the next chart
            if number_of_charts > 1:
                max_tries = 10
                tries = 0
                while tries < max_tries:
                    try:
                        action = ActionChains(browser)
                        action.send_keys(Keys.TAB)
                        action.perform()
                        tries = max_tries
                    except Exception as e:
                        log.exception(e)
                        snapshot(browser)
                    finally:
                        tries += 1

        first_symbol = False
        # calculate symbol averages
        if symbol_average['Counter'] > 0:
            symbol_average['Net Profit'] = symbol_average['Net Profit'] / symbol_average['Counter']
            symbol_average['Net Profit %'] = symbol_average['Net Profit %'] / symbol_average['Counter']
            symbol_average['Closed Trades'] = symbol_average['Closed Trades'] / symbol_average['Counter']
            symbol_average['Percent Profitable'] = symbol_average['Percent Profitable'] / symbol_average['Counter']
            symbol_average['Profit Factor'] = symbol_average['Profit Factor'] / symbol_average['Counter']
            symbol_average['Max Drawdown'] = symbol_average['Max Drawdown'] / symbol_average['Counter']
            symbol_average['Max Drawdown %'] = symbol_average['Max Drawdown %'] / symbol_average['Counter']
            symbol_average['Avg Trade'] = symbol_average['Avg Trade'] / symbol_average['Counter']
            symbol_average['Avg Trade %'] = symbol_average['Avg Trade %'] / symbol_average['Counter']
            symbol_average['Avg # Bars In Trade'] = symbol_average['Avg # Bars In Trade'] / symbol_average['Counter']
        del symbol_average['Counter']
        # log.info("{}: {}".format(symbol, symbol_average))
        symbol_averages[symbol] = symbol_average

    # calculate interval averages
    total_average = dict()
    total_average['Net Profit'] = 0
    total_average['Net Profit %'] = 0
    total_average['Closed Trades'] = 0
    total_average['Percent Profitable'] = 0
    total_average['Profit Factor'] = 0
    total_average['Max Drawdown'] = 0
    total_average['Max Drawdown %'] = 0
    total_average['Avg Trade'] = 0
    total_average['Avg Trade %'] = 0
    total_average['Avg # Bars In Trade'] = 0

    for interval in averages:
        averages[interval]['Net Profit'] = averages[interval]['Net Profit'] / averages[interval]['Counter']
        averages[interval]['Net Profit %'] = averages[interval]['Net Profit %'] / averages[interval]['Counter']
        averages[interval]['Closed Trades'] = averages[interval]['Closed Trades'] / averages[interval]['Counter']
        averages[interval]['Percent Profitable'] = averages[interval]['Percent Profitable'] / averages[interval]['Counter']
        averages[interval]['Profit Factor'] = averages[interval]['Profit Factor'] / averages[interval]['Counter']
        averages[interval]['Max Drawdown'] = averages[interval]['Max Drawdown'] / averages[interval]['Counter']
        averages[interval]['Max Drawdown %'] = averages[interval]['Max Drawdown %'] / averages[interval]['Counter']
        averages[interval]['Avg Trade'] = averages[interval]['Avg Trade'] / averages[interval]['Counter']
        averages[interval]['Avg Trade %'] = averages[interval]['Avg Trade %'] / averages[interval]['Counter']
        averages[interval]['Avg # Bars In Trade'] = averages[interval]['Avg # Bars In Trade'] / averages[interval]['Counter']
        del averages[interval]['Counter']

        # log.info("{}: {}".format(interval, averages[interval]))

        total_average['Net Profit'] += averages[interval]['Net Profit']
        total_average['Net Profit %'] += averages[interval]['Net Profit %']
        total_average['Closed Trades'] += averages[interval]['Closed Trades']
        total_average['Percent Profitable'] += averages[interval]['Percent Profitable']
        total_average['Profit Factor'] += averages[interval]['Profit Factor']
        total_average['Max Drawdown'] += averages[interval]['Max Drawdown']
        total_average['Max Drawdown %'] += averages[interval]['Max Drawdown %']
        total_average['Avg Trade'] += averages[interval]['Avg Trade']
        total_average['Avg Trade %'] += averages[interval]['Avg Trade %']
        total_average['Avg # Bars In Trade'] += averages[interval]['Avg # Bars In Trade']

    total_average['Net Profit'] = total_average['Net Profit'] / max(len(averages), 1)
    total_average['Net Profit %'] = total_average['Net Profit %'] / max(len(averages), 1)
    total_average['Closed Trades'] = total_average['Closed Trades'] / max(len(averages), 1)
    total_average['Percent Profitable'] = total_average['Percent Profitable'] / max(len(averages), 1)
    total_average['Profit Factor'] = total_average['Profit Factor'] / max(len(averages), 1)
    total_average['Max Drawdown'] = total_average['Max Drawdown'] / max(len(averages), 1)
    total_average['Max Drawdown %'] = total_average['Max Drawdown %'] / max(len(averages), 1)
    total_average['Avg Trade'] = total_average['Avg Trade'] / max(len(averages), 1)
    total_average['Avg Trade %'] = total_average['Avg Trade %'] / max(len(averages), 1)
    total_average['Avg # Bars In Trade'] = total_average['Avg # Bars In Trade'] / max(len(averages), 1)
    # log.info("Total: {}".format(total_average))

    return [results, symbol_averages, averages, total_average]


def get_strategy_statistic(browser, css):
    result = 0
    tries = 0
    while tries < config.getint('tradingview', 'create_alert_max_retries'):
        # noinspection PyBroadException
        try:
            el = find_element(browser, css, By.CSS_SELECTOR, False, 1)
            if not el:
                log.debug("NOT FOUND: {} = {}".format(By.CSS_SELECTOR, css))
                break
            text = repr(el.get_attribute('innerHTML'))
            negative = text.find("neg") >= 0
            # hex_color = Color.from_string(el.value_of_css_property('color')).hex
            # negative = hex_color == NEGATIVE_COLOR

            match = re.search(r"([\d|.]+)", text)
            if match:
                result = match.group(1)
                if result.find(".") >= 0:
                    result = float(result)
                    if negative:
                        result = result * -1.0
                else:
                    result = int(result)
                    if negative:
                        result = result * -1

            tries = config.getint('tradingview', 'create_alert_max_retries')
        except StaleElementReferenceException:
            tries += 1
        except Exception as e:
            log.exception(e)
            log.info("{} = {}".format(By.CSS_SELECTOR, css))
            tries += 1
    # log.info(result)
    return result


def format_strategy(browser, inputs, properties, input_locations, property_locations, retry_number=0):
    try:
        # open dialog
        wait_and_click(browser, css_selectors['btn_strategy_dialog'])
        
        # click and set inputs
        wait_and_click(browser, css_selectors['indicator_dialog_tab_inputs'])
        set_indicator_dialog_values(browser, inputs, input_locations)

        # click and set properties
        wait_and_click(browser, css_selectors['indicator_dialog_tab_properties'])
        set_indicator_dialog_values(browser, properties, property_locations)

        # click OK
        wait_and_click(browser, css_selectors['btn_indicator_dialog_ok'])
    except Exception as e:
        log.exception(e)
        snapshot(browser)
        retry_format_strategy(browser, inputs, properties, input_locations, property_locations, retry_number)


def set_indicator_dialog_values(browser, inputs, input_locations):
    # get input titles
    cells = find_elements(browser, css_selectors['indicator_dialog_tab_cells'])
    titles = []
    for i, cell in enumerate(cells):
        title = re.sub(r"[\W]", '', cell.text.replace(' ', '_')).lower()
        # log.info("{}. {}".format(i, title))
        titles.append(title)

    for key in inputs:
        value = inputs[key]
        index = -1
        for i, title in enumerate(titles):
            if (title == key) or ((not EXACT_CONDITIONS) and title.startswith(key)):
                index = i

        if index >= 0:
            # log.info("Found {} at index {} with value {} ({})".format(key, index, value, type(value)))
            # check first if it is a set of values, e.g. 100 USD
            if isinstance(value, dict):
                for sub_index, sub_key in enumerate(value):
                    sub_value = value[sub_key]
                    set_indicator_dialog_value(browser, input_locations, key, value, index, sub_key, sub_value, sub_index)
            else:
                set_indicator_dialog_value(browser, input_locations, key, value, index)
    # log.info(input_locations)
    return True


def set_indicator_dialog_value(browser, locations, key, value, index, sub_key='', sub_value='', sub_index=-1, retry_number=0):
    css = ''
    if key in locations:
        css = locations[key]
        if isinstance(css, dict):
            if sub_key and sub_key in css:
                css = css[sub_key]
            else:
                css = ''

    try:
        # we need to generate the css
        if not css:

            # check first if it is a set of values, e.g. 100 USD
            if sub_index >= 0:
                # css = css_selectors['indicator_dialog_tab_cell'].format(index + 2) + ' div[class^="inputGroup"] > div:nth-child({})'.format(sub_index + 1)
                css = css_selectors['indicator_dialog_tab_cell'].format(index + 2) + ' > div[class^="inner"] > div > div:nth-child({})'.format(sub_index + 1)
                # check if it is a boolean
                if isinstance(sub_value, bool):
                    css += ' input'
                else:
                    input_css = ' input'
                    element = find_element(browser, css + input_css, By.CSS_SELECTOR, False, 1)
                    if element:
                        css += input_css
                    else:
                        css += ' div[class^="selected"]'
                # save the css for future use in this run
                if not (key in locations):
                    locations[key] = dict()
                locations[key][sub_key] = css

            # check if it is a boolean
            elif isinstance(value, bool):
                css = css_selectors['indicator_dialog_tab_cell'].format(index + 1) + ' input'
                locations[key] = css
            else:
                css = css_selectors['indicator_dialog_tab_cell'].format(index + 2)
                input_css = ' input'
                element = find_element(browser, css + input_css, By.CSS_SELECTOR, False, 1)
                if element:
                    css += input_css
                else:
                    css += ' div[class^="selected"]'
                # save the css for future use in this run
                locations[key] = css
            # log.info("Generated css = {}".format(css))

        if css:
            # log.info(css)
            val = value
            if sub_index >= 0:
                val = sub_value
            # if key == 'recalculate':
            #     log.info("key = {}; value = {}; index = {}".format(key, value, index))
            #     log.info("sub_key = {}; sub_value = {}; sub_index = {}".format(sub_key, sub_value, sub_index))
            #     log.info(css)

            element = find_element(browser, css, By.CSS_SELECTOR, False)
            if isinstance(element, WebElement):
                # check if it is an input box
                if element.tag_name == 'input':
                    if element.get_attribute("type") == "checkbox":
                        # if key == 'recalculate':
                        #     log.info(val)
                        #     log.info(is_checkbox_checked(element))
                        if is_checkbox_checked(element) != val:
                            wait_and_click(browser, css + " + div")
                    else:
                        clear(element)
                        set_value(browser, element, val, True)

                # assume it is a select box
                else:
                    # click on the select box
                    element.click()
                    # get it's options
                    select_options = find_elements(browser, css_selectors['indicator_dialog_select_options'])
                    for option in select_options:
                        option_value = option.text.strip()
                        if option_value == str(val) or ((not EXACT_CONDITIONS) and option_value.startswith(str(val))):
                            # select the option
                            option.click()
                            break
            else:
                log.error("No element found for {}".format(css))
                # log.info("key = {}; value = {}; index = {}".format(key, value, index))
                # if sub_index >= 0:
                #     log.info("sub_key = {}; sub_value = {}; sub_index = {}".format(sub_key, sub_value, sub_index))
        else:
            log.error("Unable to generate CSS")
            # log.info("key = {}; value = {}; index = {}".format(key, value, index))
            # if sub_index >= 0:
            #     log.info("sub_key = {}; sub_value = {}; sub_index = {}".format(sub_key, sub_value, sub_index))
    except Exception as e:
        log.exception(e)
        # log.info("css = {}".format(css))
        # log.info("key = {}; value = {}; index = {}".format(key, value, index))
        # if sub_index >= 0:
        #     log.info("sub_key = {}; sub_value = {}; sub_index = {}".format(sub_key, sub_value, sub_index))
        retry_set_indicator_dialog_value(browser, locations, key, value, sub_key, sub_value, sub_index, retry_number)


def retry_set_indicator_dialog_value(browser, locations, key, value, sub_key, sub_value, sub_index, retry_number):
    max_retries = config.getint('tradingview', 'create_alert_max_retries')
    if config.has_option('tradingview', 'get_indicator_values_max_retries'):
        max_retries = config.getint('tradingview', 'get_indicator_values_max_retries')
    if retry_number < max_retries:
        return set_indicator_dialog_value(browser, locations, key, value, sub_key, sub_value, sub_index, retry_number)


def retry_format_strategy(browser, inputs, properties, input_locations, property_locations, retry_number):
    max_retries = config.getint('tradingview', 'create_alert_max_retries')
    if config.has_option('tradingview', 'get_indicator_values_max_retries'):
        max_retries = config.getint('tradingview', 'get_indicator_values_max_retries')
    if retry_number < max_retries:
        return format_strategy(browser, inputs, properties, input_locations, property_locations, retry_number + 1)


def select_strategy(browser, strategy_config, chart_index, retry_number=0):
    pane_index = -1
    indicator_index = -1
    if 'pane_index' in strategy_config and str(strategy_config['pane_index']).isdigit():
        pane_index = strategy_config['pane_index']
    # use css
    try:
        css = 'div.chart-container.active tr:nth-child({}) .study .pane-legend-title__description'.format((pane_index+1) * 2 - 1)
        studies = find_elements(browser, css)
        for i, study in enumerate(studies):
            study_name = studies[i].text
            log.debug('Found '.format(study_name))
            if study_name.startswith(strategy_config['name']):
                indicator_index = i
                try:
                    if str(study_name).lower().index('loading'):
                        time.sleep(0.1)
                        return retry_select_strategy(browser, strategy_config, chart_index, retry_number)
                    if str(study_name).lower().index('compiling'):
                        time.sleep(0.1)
                        return retry_select_strategy(browser, strategy_config, chart_index, retry_number)
                    if str(study_name).lower().index('error'):
                        time.sleep(0.1)
                        return retry_select_strategy(browser, strategy_config, chart_index, retry_number)
                except ValueError:
                    pass
                break
    except StaleElementReferenceException:
        log.debug('StaleElementReferenceException in studies')
        return retry_select_strategy(browser, strategy_config, chart_index, retry_number)
    except TimeoutException:
        log.warning('timeout in finding studies')
        refresh(browser)
        return retry_select_strategy(browser, strategy_config, chart_index, retry_number)
    except Exception as e:
        log.exception(e)
        return retry_select_strategy(browser, strategy_config, chart_index, retry_number)

    return indicator_index


def retry_select_strategy(browser, strategy_config, chart_index, retry_number):
    max_retries = config.getint('tradingview', 'create_alert_max_retries') * 10
    if config.has_option('tradingview', 'get_indicator_values_max_retries'):
        max_retries = config.getint('tradingview', 'get_indicator_values_max_retries')
    if retry_number < max_retries:
        return select_strategy(browser, strategy_config, chart_index, retry_number + 1)


def generate_atomic_values(items, strategies, depth=0):
    recursive_depth = depth + 1
    # log.info(items)
    result = []
    for item in items:
        # log.info("{} is of type {}".format(repr(item), str(type(item))))
        if isinstance(items[item], dict):
            # log.info(items[item])
            sub_results = []
            generate_atomic_values(items[item], sub_results, recursive_depth)
            # log.info(sub_results)
            for sub_result in sub_results:
                tmp = dict(items)
                tmp[item] = sub_result
                tmp_result = generate_atomic_values(tmp, strategies, recursive_depth)
                # log.info(tmp_result)
                # log.info(tmp)
                atomic = True
                for tmp_item in tmp:
                    if isinstance(tmp[tmp_item], dict):
                        # log.info("dict! {}".format(tmp[tmp_item]))
                        # log.info(tmp_item)
                        for key in tmp[tmp_item]:
                            # log.info(tmp[tmp_item][key])
                            if isinstance(tmp[tmp_item][key], list):
                                # log.info("list! {}".format(tmp[tmp_item][key]))
                                atomic = False
                                break
                        if not atomic:
                            break
                    if isinstance(tmp[tmp_item], list):
                        # log.info("list! {}".format(tmp[tmp_item]))
                        atomic = False
                        break
                # log.info("atomic? {} : {}".format(atomic, tmp))
                if atomic and tmp not in strategies:
                    strategies.append(tmp)

                result.append(tmp_result)
        elif isinstance(items[item], list):
            for value in items[item]:
                tmp = dict(items)
                tmp[item] = value
                tmp_result = generate_atomic_values(tmp, strategies, recursive_depth)
                # log.info(tmp_result)
                atomic = True
                for tmp_item in tmp:
                    if isinstance(tmp[tmp_item], list) or isinstance(tmp[tmp_item], dict):
                        atomic = False
                        break
                if atomic and tmp not in strategies:
                    strategies.append(tmp)
                result.append(tmp_result)
        else:
            result = [items[item]]
    return result


def get_config_values(items):
    if isinstance(items, list) or isinstance(items, dict):
        for key in items:
            items[key] = generate_config_values(items[key])
            # log.info(items[key])
    return items


def generate_config_values(value):
    result = []
    delimeter_range = ' - '
    delimeter_increment = '&'
    increment = None

    # if the value is a list, generate values recursively
    if isinstance(value, list):
        for item in value:
            result.append(generate_config_values(item))
    if isinstance(value, dict):
        for item in value:
            value[item] = generate_config_values(value[item])
        result = value
    elif isinstance(value, str) and value.find(delimeter_range) > 0:
        decimal_places = 0

        # log.info(value)
        # log.info(value.find(delimeter_increment))
        if value.find(delimeter_increment) > 0:
            [value, increment] = value.split(delimeter_increment)
            value = value.strip()
            increment = increment.strip()
            decimal_places = increment[::-1].find('.')
            try:
                if decimal_places > 0:
                    increment = float(increment)
                else:
                    increment = int(increment)
            except Exception as e:
                log.exception(e)

        [start, end] = value.split(delimeter_range)
        if not increment:
            increment = 1
            decimal_places = max(start[::-1].find('.'), end[::-1].find('.'))
            if decimal_places > 0:
                increment = '0.'
                for i in range(decimal_places - 1):
                    increment += '0'
                increment += '1'
                increment = float(increment)

        try:
            if start.find('.') >= 0:
                start = float(start)
            else:
                start = int(start)
            if end.find('.') >= 0:
                end = float(end)
            else:
                end = int(end)
        except Exception as e:
            log.exception(e)

        # log.info("start = {}".format(start))
        # log.info("end = {}".format(end))
        # log.info("decimal_places = {}".format(decimal_places))
        if not (isinstance(start, int) or isinstance(start, float)):
            raise ValueError("Invalid range value: '{}'".format(start))
        if not (isinstance(end, int) or isinstance(end, float)):
            raise ValueError("Invalid range value: '{}'".format(end))
        if not (isinstance(increment, int) or isinstance(increment, float)):
            raise ValueError("Invalid increment value: '{}'".format(increment))

        for number in numpy.arange(start, end, increment):
            if decimal_places > 0:
                result.append(round(number, decimal_places))
            else:
                result.append(number)
        result.append(end)
    else:
        result = value
    return result


def wait_until_indicator_is_loaded(browser, indicator_name, pane_index):
    result = False
    tries = 0
    max_tries = 10
    while tries < max_tries:
        try:
            css = 'div.chart-container.active tr:nth-child({}) .study .pane-legend-title__description'.format((pane_index+1) * 2 - 1)
            studies = find_elements(browser, css)
            for i, study in enumerate(studies):
                study_name = studies[i].text
                if study_name.startswith(indicator_name):
                    if str(study_name).lower().find('loading') >= 0 or str(study_name).lower().find('compiling') >= 0 or str(study_name).lower().find('error') >= 0:
                        time.sleep(0.05)
                    else:
                        result = True
                        tries = max_tries
                        break
        except StaleElementReferenceException:
            pass
        except TimeoutException:
            log.warning('timeout in finding studies')
            # return False which will force a browser refresh
        except Exception as e:
            log.exception(e)
        finally:
            tries += 1

    return result


def summary(total_alerts):
    if total_alerts > 0:
        elapsed = timing.clock() - timing.start
        avg = '%s' % float('%.5g' % (elapsed / total_alerts))
        log.info("{} alerts and/or signals set with an average process time of {} seconds".format(str(total_alerts), avg))
    elif total_alerts == 0:
        log.info("No alerts or signals set")
