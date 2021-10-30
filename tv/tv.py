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
import copy
import datetime
import getpass
import json
import shutil
import math
import numbers
import os
import re
import time
import errno

import dill
import numpy

from urllib.parse import unquote
from PIL import Image
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, NoAlertPresentException, \
    TimeoutException, InvalidArgumentException, WebDriverException, InvalidSessionIdException, \
    SessionNotCreatedException, JavascriptException, ElementClickInterceptedException
from selenium.webdriver import DesiredCapabilities, ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from multiprocessing import Pool
from kairos import timing
from kairos import tools
from kairos.tools import format_number, wait_for_element_is_stale, unicode_to_float_int
from fastnumbers import fast_real

TEST = False
processing_errors = []

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
DELAY_KEYSTROKE = 0.05
DELAY_WATCHLIST = 0.5
DELAY_TIMEFRAME = 0.5
DELAY_SCREENER_SEARCH = 2
DELAY_EXTRACT_SYMBOLS = 1
DELAY_READ_INDICATOR_VALUE = 0.2
RUN_IN_BACKGROUND = False
MULTI_THREADING = False
ALERT_NUMBER = 0
SEARCH_FOR_WARNING = True
REFRESH_START = timing.time()
REFRESH_INTERVAL = 3600  # Refresh the browser each hour
ALREADY_LOGGED_IN = False
VERIFY_MARKET_LISTING = True

# performance
READ_FROM_DATA_WINDOW = True
WAIT_UNTIL_CHART_IS_LOADED = True
READ_ALL_VALUES_AT_ONCE = True
CHANGE_SYMBOL_WITH_SPACE = False

MODIFIER_KEY = Keys.LEFT_CONTROL
OS = tools.get_operating_system()
# if OS == 'macos':
#     MODIFIER_KEY = Keys.COMMAND

SELECT_ALL = MODIFIER_KEY + 'a'
CUT = MODIFIER_KEY + 'x'
PASTE = MODIFIER_KEY + 'v'
COPY = MODIFIER_KEY + 'c'

TV_UID = ''
TV_PWD = ''

NEGATIVE_COLOR = '#DD2E02'
WEBDRIVER_INSTANCE = 0

css_selectors = dict(
    # ALERTS
    # username='span.tv-header__dropdown-text.tv-header__dropdown-text--username.js-username.tv-header__dropdown-text--ellipsis.apply-overflow-tooltip.common-tooltip-fixed',
    account='button.tv-header__user-menu-button--logged',
    username='a[data-name="header-user-menu-profile"] span[class^="username"]',
    anonymous_account='button.tv-header__user-menu-button--anonymous',
    anonymous_signin='div[data-name="header-user-menu-sign-in"]',
    show_email_and_username='span.js-show-email',
    input_username='input[name="username"]',
    input_password='input[name="password"]',
    btn_login_by_email='span.tv-signin-dialog__toggle-email',
    btn_timeframe='#header-toolbar-intervals > div:last-child',
    options_timeframe='div[class^="dropdown-"] div[class^="item"]',
    btn_watchlist_menu='body > div.js-rootresizer__contents > div.layout__area--right > div > div.widgetbar-tabs > div > div:nth-child(1) > div > div > div:nth-child(1)',
    btn_watchlist_menu_menu='div[data-name="watchlists-button"]',
    options_watchlist='div[class^="watchlistMenu"] span[class^="title"]',
    input_watchlist_add_symbol='div[data-name="add-symbol-button"] > span',
    btn_input_symbol='div[id="header-toolbar-symbol-search"]',
    dlg_symbol_search_input='div[data-name="symbol-search-items-dialog"] input[data-role="search"]',
    input_symbol='div[id="header-toolbar-symbol-search"] div',
    asset='div[data-name="legend-series-item"] div[data-name="legend-source-title"]:nth-child(1)',
    btn_alert_menu='div[data-name="alerts-settings-button"]',
    item_clear_alerts='div.charts-popup-list > a.item:last-child',
    item_clear_inactive_alerts='div[data-name="menu-inner"] > div:nth-child(3) > div:nth-child(1)',
    item_restart_inactive_alerts='div[data-name="menu-inner"] > div:nth-child(1) > div:nth-child(1)',
    btn_dlg_clear_alerts_confirm='div.tv-dialog > div.tv-dialog__section--actions > div[data-name="yes"]',
    item_alerts='table.alert-list > tbody > tr.alert-item',
    alerts_counter='div.widgetbar-widget-alerts_manage span[title*="active alerts used from"]',
    btn_create_alert='#header-toolbar-alerts',
    btn_create_alert_from_alert_menu='div[data-name="set-alert-button"]',
    btn_alert_cancel='div.tv-dialog__close.js-dialog__close',
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
    clickable_dlg_create_alert_send_push='input[type="checkbox"][name="send-push"] + span + span.tv-control-checkbox__ripple',
    # Show Popup
    clickable_dlg_create_alert_show_popup='input[type="checkbox"][name="show-popup"] + span + span.tv-control-checkbox__ripple',
    # Send Email
    clickable_dlg_create_alert_send_email='input[type="checkbox"][name="send-email"] + span + span.tv-control-checkbox__ripple',
    # Webhook
    clickable_dlg_create_alert_webhook='input[type="checkbox"][name="webhook-toggle"] + span + span.tv-control-checkbox__ripple',
    dlg_create_alert_webhook='input[type="url"][name="webhook-url"]',
    # Toggle more actions
    btn_toggle_more_actions='div.tv-alert-dialog__fieldset-wrapper-toggle.js-fieldset-wrapper-toggle',
    # Play Sound
    clickable_dlg_create_alert_play_sound='div.tv-alert-dialog__fieldset-value-item.js-sound-switch label',
    # Sound options
    dlg_create_alert_ringtone='div.js-sound-settings > div.tv-alert-dialog__group-item.tv-alert-dialog__group-item--left > span',
    options_dlg_create_alert_ringtone='div.js-sound-settings span.tv-control-select__dropdown.tv-dropdown-behavior__body.i-opened span.tv-control-select__option-wrap',
    dlg_create_alert_sound_duration='div.js-sound-settings > div.tv-alert-dialog__group-item.tv-alert-dialog__group-item--right > span',
    options_dlg_create_alert_sound_duration='div.js-sound-settings span.tv-control-select__dropdown.tv-dropdown-behavior__body.i-opened span.tv-control-select__option-wrap',
    # Send Email-to-SMS
    clickable_dlg_create_alert_send_email_to_sms='input[type="checkbox"][name="send-sms"] + span + span.tv-control-checkbox__ripple',
    # Send SMS
    clickable_dlg_create_alert_send_sms='input[type="checkbox"][name="send-sms"] + span + span.tv-control-checkbox__ripple',
    btn_dlg_create_alert_submit='div[data-name="submit"] > span.tv-button__loader',
    # Set Alert name
    dlg_create_alert_name='input[type="text"][name="alert-name"]',
    # Acknowledge repainting
    btn_create_alert_warning_continue_anyway_got_it='div[data-name="alerts-trigger-warning-dialog-pine-repainting"] label[class^="checkbox"]',
    btn_create_alert_warning_continue_anyway='div[data-name="alerts-trigger-warning-dialog-pine-repainting"] button[name="continue"]',
    btn_alerts='div[data-name="alerts"]',
    btn_calendar='div[data-name="calendar"]',
    btn_watchlist='div[data-name="base"]',
    btn_watchlist_submenu='div.widgetbar-page.active div[data-name="watchlists-button"',
    div_watchlist_item='div[data-symbol-full]',
    div_watchlist_item_by_symbol='div[data-symbol-full="{}"]',
    signout='div[data-name="header-user-menu-sign-out"]',
    checkbox_dlg_create_alert_open_ended='div.tv-alert-dialog__fieldset-value-item--open-ended input',
    clickable_dlg_create_alert_open_ended='div.tv-alert-dialog__fieldset-value-item--open-ended span.tv-control-checkbox__label',
    btn_screenshot='#header-toolbar-screenshot',
    btn_twitter_url='div[data-name="tweet-chart-image"]',
    btn_image_url='div[data-name="open-image-in-new-tab"]',
    img_chart='img[class="tv-snapshot-image"]',
    btn_watchlist_sort_symbol='div.widgetbar-widget-watchlist span[data-column-type="short_name"]',
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
    btn_strategy_dialog='div.icon-button.js-backtesting-open-format-dialog',
    strategy_id='#bottom-area > div.bottom-widgetbar-content.backtesting > div.backtesting-head-wrapper > div:nth-child(1) > div > span',
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
    btn_indicator_dialog_ok='#overlap-manager-root button[name="submit"]',
    active_chart_asset='div.chart-container.active div.pane-legend-line.main div.pane-legend-title__description > div',
    active_chart_interval='div[id="header-toolbar-intervals"] div[class*="isActive"] > div > div',
    chart_container='div.chart-container div.chart-gui-wrapper canvas:nth-child(2)',
    # User Menu
    btn_user_menu='button.tv-header__user-menu-button--logged',
    btn_logout='div[data-name="header-user-menu-sign-out"]',
    active_widget_bar='div.widgetbar-page.active',
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
    checkbox_dlg_create_alert_webhook='webhook-toggle',
    # checkbox_dlg_create_alert_send_sms='send-true-sms',  # option removed by TradingView
    checkbox_dlg_create_alert_send_push='send-push'
)

tv_start = timing.time()
config = tools.get_config()
mode = 'a'  # append
if config.getboolean('logging', 'clear_on_start_up'):
    mode = 'w'  # overwrite
log = tools.create_log(mode)
log.setLevel(20)
# WARNING: debug level will log all HTTP requests
if config.has_option('logging', 'level'):
    log.setLevel(config.getint('logging', 'level'))

path_to_chromedriver = r"" + config.get('webdriver', 'path')
if os.path.exists(path_to_chromedriver):
    path_to_chromedriver = path_to_chromedriver.replace('.exe', '')
else:
    log.error("File {} does not exist".format(path_to_chromedriver))
    log.exception(FileNotFoundError)
    exit(0)

download_path = ''
if config.has_option('webdriver', 'download_path'):
    download_path = r"" + str(config.get('webdriver', 'download_path'))
    if not os.path.exists(download_path):
        # noinspection PyBroadException
        try:
            os.mkdir(download_path)
        except Exception as screenshot_error:
            log.warning('No download_path specified or unable to create it.')
            download_path = ''

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
            log.warning('No screenshot directory specified or unable to create it.')
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
if config.has_option('delays', 'read_indicator_value'):
    DELAY_READ_INDICATOR_VALUE = config.getfloat('delays', 'read_indicator_value')
if config.has_option('performance', 'read_from_data_window'):
    READ_FROM_DATA_WINDOW = config.getboolean('performance', 'read_from_data_window')
if config.has_option('performance', 'wait_until_chart_is_loaded'):
    WAIT_UNTIL_CHART_IS_LOADED = config.getboolean('performance', 'wait_until_chart_is_loaded')
if config.has_option('performance', 'read_all_values_at_once'):
    READ_ALL_VALUES_AT_ONCE = config.getboolean('performance', 'read_all_values_at_once')
if config.has_option('performance', 'change_symbol_with_space'):
    CHANGE_SYMBOL_WITH_SPACE = config.getboolean('performance', 'change_symbol_with_space')

if config.has_option('tradingview', 'exact_conditions'):
    EXACT_CONDITIONS = config.getboolean('tradingview', 'exact_conditions')
if config.has_option('tradingview', 'verify_market_listing'):
    VERIFY_MARKET_LISTING = config.getboolean('tradingview', 'verify_market_listing')

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
    log.debug('refreshing browser')
    browser.refresh()
    # Switching to Alert
    close_alerts(browser)
    # Close the watchlist menu if it is open
    if find_element(browser, css_selectors['btn_watchlist_submenu'], By.CSS_SELECTOR, False, False, 0.5):
        wait_and_click(browser, css_selectors['btn_watchlist'])


def element_exists(browser, locator, delay=CHECK_IF_EXISTS_TIMEOUT, locator_strategy=By.CSS_SELECTOR):
    result = False
    try:
        element = find_element(browser, locator, locator_strategy, delay)
        result = type(element) is WebElement
    except NoSuchElementException:
        log.debug('No such element. SELECTOR=' + locator)
        # print the session_id and url in case the element is not found
        # noinspection PyProtectedMember
        log.debug("In case you want to reuse session, the session_id and _url for current browser session are: {},{}".format(browser.session_id, browser.command_executor._url))
    except TimeoutException:
        log.debug('No such element. SELECTOR=' + locator)
    except Exception as element_exists_error:
        log.error(element_exists_error)
        log.debug("Check your locator: {}".format(locator))
        # noinspection PyProtectedMember
        log.debug("In case you want to reuse session, the session_id and _url for current browser session are: {},{}".format(browser.session_id, browser.command_executor._url))
    finally:
        log.debug("{} ({})".format(str(result), locator))
        return result


def wait_and_click(browser, locator, delay=CHECK_IF_EXISTS_TIMEOUT, locator_strategy=By.CSS_SELECTOR):
    return WebDriverWait(browser, delay).until(
        ec.element_to_be_clickable((locator_strategy, locator))).click()


def wait_and_click_by_xpath(browser, xpath, delay=CHECK_IF_EXISTS_TIMEOUT):
    WebDriverWait(browser, delay).until(
        ec.element_to_be_clickable((By.XPATH, xpath))).click()


def wait_and_click_by_text(browser, tag, search_text, css_class='', delay=CHECK_IF_EXISTS_TIMEOUT, position=0, postfix=''):
    if type(css_class) is str and len(css_class) > 0:
        xpath = '//{0}[contains(text(), "{1}") and @class="{2}"]{3}'.format(tag, search_text, css_class, postfix)
    else:
        xpath = '//{0}[contains(text(), "{1}")]{2}'.format(tag, search_text, postfix)
    if position == 0:
        WebDriverWait(browser, delay).until(
            ec.element_to_be_clickable((By.XPATH, xpath))).click()
    else:
        find_elements(browser, xpath, By.XPATH)[position].click()


def wait_and_get(browser, css, delay=CHECK_IF_EXISTS_TIMEOUT):
    element = WebDriverWait(browser, delay).until(
        ec.element_to_be_clickable((By.CSS_SELECTOR, css)))
    return element


def wait_and_visible(browser, css, delay=CHECK_IF_EXISTS_TIMEOUT):
    element = WebDriverWait(browser, delay).until(
        ec.visibility_of_element_located((By.CSS_SELECTOR, css)))
    return element


def find_element(browser, locator, locator_strategy=By.CSS_SELECTOR, except_on_timeout=True, visible=False, delay=CHECK_IF_EXISTS_TIMEOUT):
    if except_on_timeout:
        if visible:
            element = WebDriverWait(browser, delay).until(
                ec.visibility_of_element_located((locator_strategy, locator)))
        else:
            element = WebDriverWait(browser, delay).until(
                ec.presence_of_element_located((locator_strategy, locator)))
        return element
    else:
        try:
            if visible:
                element = WebDriverWait(browser, delay).until(
                    ec.visibility_of_element_located((locator_strategy, locator)))
            else:
                element = WebDriverWait(browser, delay).until(
                    ec.presence_of_element_located((locator_strategy, locator)))
            return element
        except TimeoutException as e:
            log.debug(e)
            log.debug("Check your {} locator: {}".format(locator_strategy, locator))
            # print the session_id and url in case the element is not found
            if browser is webdriver.Remote:
                # noinspection PyProtectedMember
                log.debug("In case you want to reuse session, the session_id and _url for current browser session are: {},{}".format(browser.session_id, browser.command_executor._url))


def find_elements(browser, locator, locator_strategy=By.CSS_SELECTOR, except_on_timeout=True, visible=False, delay=CHECK_IF_EXISTS_TIMEOUT):
    if except_on_timeout:
        if visible:
            elements = WebDriverWait(browser, delay).until(
                ec.visibility_of_all_elements_located((locator_strategy, locator)))
        else:
            elements = WebDriverWait(browser, delay).until(
                ec.presence_of_all_elements_located((locator_strategy, locator)))
        return elements
    else:
        try:
            if visible:
                elements = WebDriverWait(browser, delay).until(
                    ec.visibility_of_all_elements_located((locator_strategy, locator)))
            else:
                elements = WebDriverWait(browser, delay).until(
                    ec.presence_of_all_elements_located((locator_strategy, locator)))
            return elements
        except TimeoutException as e:
            log.debug(e)
            log.debug("Check your {} locator: {}".format(locator_strategy, locator))
            # print the session_id and url in case the element is not found
            # noinspection PyProtectedMember
            log.debug("In case you want to reuse session, the session_id and _url for current browser session are: {},{}".format(browser.session_id, browser.command_executor._url))
            return None


def hover(browser, element, click=False, delay=DELAY_BREAK_MINI):
    action = ActionChains(browser)
    action.move_to_element(element)
    if click:
        time.sleep(delay)
        action.click(element)
    action.perform()


def close_cookies_message(browser):
    xpath = '//h2[contains(text(), "cookies")]/following-sibling::div/button'
    try:
        wait_and_click_by_xpath(browser, xpath, 2)
        log.info("Cookie banner found")
    except TimeoutException as e:
        log.debug(e)
        log.info("Cookie banner not found")


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
    match = re.search(r"(\d+)\s(\w\w\w)", timeframe)
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


def set_delays(chart=None):
    global WAIT_TIME_IMPLICIT
    global PAGE_LOAD_TIMEOUT
    global CHECK_IF_EXISTS_TIMEOUT
    global DELAY_BREAK_MINI
    global DELAY_BREAK
    global DELAY_SUBMIT_ALERT
    global DELAY_CLEAR_INACTIVE_ALERTS
    global DELAY_CHANGE_SYMBOL
    global DELAY_KEYSTROKE
    global DELAY_READ_INDICATOR_VALUE

    # set delays as defined within the chart with a fallback to the config file
    if chart and 'wait_time_implicit' in chart and isinstance(chart['wait_time_implicit'], numbers.Real):
        WAIT_TIME_IMPLICIT = chart['wait_time_implicit']
    elif config.has_option('webdriver', 'wait_time_implicit'):
        WAIT_TIME_IMPLICIT = config.getfloat('webdriver', 'wait_time_implicit')

    if chart and 'page_load_timeout' in chart and isinstance(chart['page_load_timeout'], numbers.Real):
        PAGE_LOAD_TIMEOUT = chart['page_load_timeout']
    elif config.has_option('webdriver', 'page_load_timeout'):
        PAGE_LOAD_TIMEOUT = config.getfloat('webdriver', 'page_load_timeout')

    if chart and 'check_if_exists_timeout' in chart and isinstance(chart['check_if_exists_timeout'], numbers.Real):
        CHECK_IF_EXISTS_TIMEOUT = chart['check_if_exists_timeout']
    elif config.has_option('webdriver', 'check_if_exists_timeout'):
        CHECK_IF_EXISTS_TIMEOUT = config.getfloat('webdriver', 'check_if_exists_timeout')

    if chart and 'delays' in chart and isinstance(chart['delays'], dict):
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
        if 'read_indicator_value' in delays and isinstance(delays['read_indicator_value'], numbers.Real):
            DELAY_READ_INDICATOR_VALUE = delays['read_indicator_value']
        elif config.has_option('delays', 'read_indicator_value'):
            DELAY_READ_INDICATOR_VALUE = config.getfloat('delays', 'read_indicator_value')


def set_options(chart=None):
    global READ_FROM_DATA_WINDOW
    global WAIT_UNTIL_CHART_IS_LOADED
    global READ_ALL_VALUES_AT_ONCE
    global CHANGE_SYMBOL_WITH_SPACE
    global VERIFY_MARKET_LISTING

    if chart and 'performance' in chart and isinstance(chart['performance'], dict):
        options = chart['performance']
        # performance options
        if 'read_from_data_window' in options and isinstance(options['read_from_data_window'], bool):
            READ_FROM_DATA_WINDOW = options['read_from_data_window']
        if 'wait_until_chart_is_loaded' in options and isinstance(options['wait_until_chart_is_loaded'], bool):
            WAIT_UNTIL_CHART_IS_LOADED = options['wait_until_chart_is_loaded']
        if 'read_all_values_at_once' in options and isinstance(options['read_all_values_at_once'], bool):
            READ_ALL_VALUES_AT_ONCE = options['read_all_values_at_once']
        if 'change_symbol_with_space' in options and isinstance(options['change_symbol_with_space'], bool):
            CHANGE_SYMBOL_WITH_SPACE = options['change_symbol_with_space']

    if chart and 'verify_market_listing' in chart and isinstance(chart['verify_market_listing'], bool):
        VERIFY_MARKET_LISTING = chart['verify_market_listing']


def wait_until_indicators_are_loaded(browser):
    indicator_loading = True
    log.info("indicators loading")
    while indicator_loading:
        indicator_loading = False
        # get css selector that has the loading animation
        elem_loading = find_elements(browser, css_selectors['span_indicator_loading'])
        # check if any of the elements is loaded
        for elem in elem_loading:
            indicator_loading = elem.is_displayed()
            if indicator_loading:
                break
    log.info("indicators loaded")


def is_indicator_loaded(browser, chart_index, pane_index, indicator_index, name=""):
    # get css selector that has the loading animation for the indicator
    elem_loading = find_elements(find_elements(
        find_elements(find_elements(browser, 'chart-container', By.CLASS_NAME)[chart_index], 'pane',
                      By.CLASS_NAME)[pane_index], 'div[data-name="legend-source-item"]', By.CSS_SELECTOR)[
                      indicator_index], 'div[class^="valuesWrapper"] > span[class^="loader"]', By.CSS_SELECTOR)
    # check if any of the elements is loaded
    indicator_loaded = True
    if len(elem_loading) == 0:
        if name != "":
            name = "{} at index ".format(name)
        log.warn("unable to find 'loading' elements of indicator {}{} on pane {} on chart {}".format(name, indicator_index, pane_index, chart_index))
    for elem in elem_loading:
        if elem.is_displayed():
            indicator_loaded = False
            break
    return indicator_loaded or len(elem_loading) == 0


def move_to_data_window_indicator(browser, indicator, retry_number=0):
    max_retries = config.getint('tradingview', 'create_alert_max_retries')
    if config.has_option('tradingview', 'indicator_values_max_retries'):
        max_retries = config.getint('tradingview', 'indicator_values_max_retries')

    # 1. find the correct indicator
    xpath = '//div[not(contains(@class, "hidden"))]/div[@class="chart-data-window-header"]/span[starts-with(text(), "{}")][1]'.format(indicator['name'])
    if element_exists(browser, xpath, CHECK_IF_EXISTS_TIMEOUT, By.XPATH):
        try:
            ActionChains(browser).move_to_element(find_element(browser, '{}/parent::*/parent::*/div[@class="chart-data-window-body"]/div[last()]'.format(xpath), By.XPATH)).perform()
            return True
        except StaleElementReferenceException:
            if retry_number < max_retries:
                time.sleep(DELAY_BREAK_MINI)
                return move_to_data_window_indicator(browser, indicator, retry_number+1)
        except JavascriptException:
            if retry_number < max_retries:
                time.sleep(DELAY_BREAK_MINI)
                return move_to_data_window_indicator(browser, indicator, retry_number+1)
        except TimeoutException:
            return False
        except Exception as e:
            log.exception(e)
            snapshot(browser)
    else:
        log.exception("{} not found. Please, verify that the indicator on the chart starts with '{}'".format(indicator['name'], indicator['name']))
        exit(0)


def wait_until_indicator_values_are_loaded(browser, indicator):
    if indicator and 'verify_indicator_loaded' in indicator and indicator['verify_indicator_loaded']:
        wait_until_data_window_indicator_is_loaded(browser, indicator)


def wait_until_data_window_indicator_is_loaded(browser, indicator, retry_number=0):
    max_retries = config.getint('tradingview', 'create_alert_max_retries')
    if config.has_option('tradingview', 'indicator_values_max_retries'):
        max_retries = config.getint('tradingview', 'indicator_values_max_retries')

    # wait until marked value is loaded
    xpath_check_element = '//div[not(contains(@class, "hidden"))]/div[@class="chart-data-window-header"]/span[starts-with(text(), "{}")][1]/parent::*/parent::*/div[@class="chart-data-window-body"]/div[last()]/parent::*/parent::*/div[@class="chart-data-window-body"]/div[{}]/div[2]'.format(indicator['name'], indicator['verify_indicator_loaded'] + 1)
    element = False
    value = 'n/a'
    i = 0
    while ((not element) or value == 'n/a') and i < 10:
        i = i + 1
        try:
            element = find_element(browser, xpath_check_element, By.XPATH)
            value = element.text
        except StaleElementReferenceException as e:
            element = False
            value = 'n/a'
            time.sleep(DELAY_BREAK)
            log.debug(e)
        except TimeoutException as e:
            log.debug(e)
            if retry_number < max_retries:
                wait_until_data_window_indicator_is_loaded(browser, indicator, retry_number+1)
            else:
                log.exception("{} not found. Please, verify that the indicator on the chart starts with '{}'".format(indicator['name'], indicator['name']))
                exit(0)
            element = False
        except Exception as e:
            log.exception(e)
            element = False
            if retry_number < max_retries:
                wait_until_data_window_indicator_is_loaded(browser, indicator, retry_number+1)


def get_data_window_indicator_value(browser, indicator, index, retry_number=0):
    max_retries = config.getint('tradingview', 'create_alert_max_retries')
    if config.has_option('tradingview', 'indicator_values_max_retries'):
        max_retries = config.getint('tradingview', 'indicator_values_max_retries')

    xpath_value = '//div[not(contains(@class, "hidden"))]/div[@class="chart-data-window-header"]/span[starts-with(text(), "{}")][1]/parent::*/parent::*/div[@class="chart-data-window-body"]/div[last()]/parent::*/parent::*/div[@class="chart-data-window-body"]/div[{}]/div[2]/span'.format(indicator['name'], index + 1)
    element = False
    value = ''
    while not (element and value):
        try:
            element = find_element(browser, xpath_value, By.XPATH)
            value = element.text
        except StaleElementReferenceException as e:
            element = False
            log.debug(e)
            # continue
        except Exception as e:
            log.exception(e)
            element = False
            if retry_number < max_retries * 10:
                time.sleep(0.05)
                return get_data_window_indicator_value(browser, indicator, index, retry_number+1)
            else:
                value = 'NAN'
                log.info(value)
    return value


def get_data_window_indicator_value_by_text(browser, indicator, text, retry_number=0):
    max_retries = config.getint('tradingview', 'create_alert_max_retries')
    if config.has_option('tradingview', 'indicator_values_max_retries'):
        max_retries = config.getint('tradingview', 'indicator_values_max_retries')

    xpath_value = '//div[not(contains(@class, "hidden"))]/div[@class="chart-data-window-header"]/span[starts-with(text(), "{}")][1]/parent::*/parent::*/div[@class="chart-data-window-body"]/div[last()]/parent::*/parent::*/div[@class="chart-data-window-body"]/div/div[text()="{}"]/following-sibling::div'.format(indicator['name'], text)
    element = False
    value = ''
    first = True
    while not (element and value):
        try:
            element = find_element(browser, xpath_value, By.XPATH)
            if not first:
                browser.execute_script("arguments[0].scrollIntoView(true);", element)
            first = False
            value = element.text
            if value == 'n/a':
                if retry_number < max_retries * 10:
                    time.sleep(DELAY_BREAK_MINI)
                    return get_data_window_indicator_value_by_text(browser, indicator, text, retry_number + 1)
        except StaleElementReferenceException as e:
            log.debug(e)
            element = False
            if retry_number < max_retries * 20:
                time.sleep(DELAY_BREAK_MINI)
            # continue
        except Exception as e:
            log.exception(e)
            element = False
            if retry_number < max_retries * 10:
                time.sleep(DELAY_BREAK_MINI)
                return get_data_window_indicator_value_by_text(browser, indicator, text, retry_number+1)
    return value


def get_data_window_indicator_values(browser, indicator, retry_number=0):
    result = []
    try:
        xpath_values = '//div[not(contains(@class, "hidden"))]/div[@class="chart-data-window-header"]/span[starts-with(text(), "{}")][1]/parent::*/parent::*/div[@class="chart-data-window-body"]/div[last()]/parent::*/parent::*/div[@class="chart-data-window-body"]/div/div[2]'.format(indicator['name'])
        elements = find_elements(browser, xpath_values, By.XPATH)
        for i in range(len(elements)):
            result.append(get_data_window_indicator_value(browser, indicator, i))
    except Exception as e:
        log.exception(e)
        return retry_get_data_window_indicator_values(browser, indicator, retry_number)

    return result


def get_indicator_values(browser, indicator, symbol, previous_result, retry_number=0):
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
            css = 'div.chart-container.active tr:nth-child({}) div[data-name="legend-source-item"] div[data-name="legend-source-title"]:nth-child(1)'.format((pane_index+1) * 2 - 1)
            studies = find_elements(browser, css)
            for i, study in enumerate(studies):
                study_name = str(study.text)
                log.debug('Found {}'.format(study_name))
                if study_name.startswith(indicator['name']):
                    indicator_index = i
                    break
                try:
                    if str(study_name).lower().index('loading'):
                        time.sleep(0.1)
                        return retry_get_indicator_values(browser, indicator, symbol, previous_result, retry_number)
                    if str(study_name).lower().index('compiling'):
                        time.sleep(0.1)
                        return retry_get_indicator_values(browser, indicator, symbol, previous_result, retry_number)
                    if str(study_name).lower().index('error'):
                        time.sleep(0.1)
                        return retry_get_indicator_values(browser, indicator, symbol, previous_result, retry_number)
                except ValueError:
                    pass
        except StaleElementReferenceException:
            log.debug('StaleElementReferenceException in studies')
            return retry_get_indicator_values(browser, indicator, symbol, previous_result, retry_number)
        except TimeoutException:
            log.warning('timeout in finding studies')
            # return False which will force a browser refresh
            result = False
        except Exception as e:
            log.exception(e)
            return retry_get_indicator_values(browser, indicator, symbol, previous_result, retry_number)

    try:
        if 0 <= indicator_index < len(studies):
            css = '#header-toolbar-symbol-search'
            element = find_element(browser, css)
            action = ActionChains(browser)
            action.move_to_element_with_offset(element, 5, 5)
            action.perform()

            # make sure that all the values have loaded
            extracted = False
            while not extracted:
                visible_values = 0
                result = []
                elem_values = find_elements(find_elements(find_elements(find_elements(browser, 'chart-container', By.CLASS_NAME)[chart_index], 'pane', By.CLASS_NAME)[pane_index], 'div[data-name="legend-source-item"]', By.CSS_SELECTOR)[indicator_index], 'div[class^="valuesAdditionalWrapper"] > div > div', By.CSS_SELECTOR)
                for e in elem_values:
                    if e.is_displayed():
                        visible_values += 1
                        # if a value isn't loaded (yet) it will have an empty string
                        if e.text == '':
                            time.sleep(DELAY_BREAK_MINI)
                        else:
                            result.append(str(e.text).translate({0x2c: '.', 0xa0: None, 0x2212: '-'}))
                # check if the amount of elements equals the size of of the result dictionary
                extracted = len(result) == visible_values

    except StaleElementReferenceException:
        log.debug('StaleElementReferenceException in values')
        return retry_get_indicator_values(browser, indicator, symbol, previous_result, retry_number)
    except TimeoutException:
        log.warning('timeout in getting values', )
        # return False which will force a browser refresh
        result = False
    except Exception as e:
        log.exception(e)
        return retry_get_indicator_values(browser, indicator, symbol, previous_result, retry_number)

    # Check if we at least have a value, if not then the chart isn't loaded yet
    only_na_values = True
    for value in result:
        if value != 'n/a':
            only_na_values = False
            break

    # Check if there is a result and if the result differs from the previous result, otherwise we might have accidentally copied the values from the previous chart
    if not result or (isinstance(result, list) and len(result) == 0) or only_na_values or result == previous_result:
        # if only_na_values:
        #     time.sleep(0.1)
        return retry_get_indicator_values(browser, indicator, symbol, previous_result, retry_number)

    return result


def retry_get_data_window_indicator_values(browser, indicator, retry_number=0):
    max_retries = config.getint('tradingview', 'create_alert_max_retries') * 10
    if config.has_option('tradingview', 'indicator_values_max_retries'):
        max_retries = config.getint('tradingview', 'indicator_values_max_retries')
    if retry_number < max_retries:
        return get_data_window_indicator_values(browser, indicator, retry_number + 1)


def retry_get_indicator_values(browser, indicator, symbol, previous_result, retry_number=0):
    max_retries = config.getint('tradingview', 'create_alert_max_retries') * 10
    if config.has_option('tradingview', 'indicator_values_max_retries'):
        max_retries = config.getint('tradingview', 'indicator_values_max_retries')
    if retry_number < max_retries:
        return get_indicator_values(browser, indicator, symbol, previous_result, retry_number + 1)


def is_indicator_triggered(browser, indicator, values, previous_symbol_values):
    result = False
    try:
        if 'trigger' in indicator:
            comparison = '='
            lhs = ''
            rhs = ''

            if 'type' in indicator['trigger']:
                comparison = indicator['trigger']['type']
            if 'left-hand-side' in indicator['trigger']:
                if 'index' in indicator['trigger']['left-hand-side'] and type(indicator['trigger']['left-hand-side']['index']) == int:
                    ignore = []
                    if 'ignore' in indicator['trigger']['left-hand-side'] and isinstance(indicator['trigger']['left-hand-side']['ignore'], list):
                        ignore = indicator['trigger']['left-hand-side']['ignore']
                    index = int(indicator['trigger']['left-hand-side']['index'])
                    if not values:
                        value = get_data_window_indicator_value(browser, indicator, index)
                        if not (value in ignore):
                            lhs = value
                    elif values and index < len(values):
                        try:
                            if not (values[index] in ignore):
                                lhs = values[index]
                        except IndexError:
                            log.exception('YAML value trigger -> left-hand-side -> index is out of range. Index is {} but must be between 0 and {}'.format(str(index), str(len(values)-1)))
                if lhs == '' and 'value' in indicator['trigger']['left-hand-side'] and indicator['trigger']['left-hand-side']['value'] != '':
                    lhs = indicator['trigger']['left-hand-side']['value']
            if 'right-hand-side' in indicator['trigger']:
                if 'index' in indicator['trigger']['right-hand-side'] and type(indicator['trigger']['right-hand-side']['index']) == int:
                    ignore = []
                    if 'ignore' in indicator['trigger']['right-hand-side'] and isinstance(indicator['trigger']['right-hand-side']['ignore'], list):
                        ignore = indicator['trigger']['right-hand-side']['ignore']
                    index = int(indicator['trigger']['right-hand-side']['index'])
                    if not values:
                        value = get_data_window_indicator_value(browser, indicator, index)
                        if not (value in ignore):
                            rhs = value
                    elif values and index < len(values):
                        try:
                            if not (values[index] in ignore):
                                rhs = values[index]
                        except IndexError:
                            log.exception('YAML value trigger -> right-hand-side -> index is out of range. Index is {} but must be between 0 and {}'.format(str(index), str(len(values)-1)))
                if rhs == '' and 'value' in indicator['trigger']['right-hand-side'] and indicator['trigger']['right-hand-side']['value'] != '':
                    rhs = indicator['trigger']['right-hand-side']['value']
            # log.info('{} {} {} ?'.format(repr(lhs), comparison, repr(rhs)))
            if (not (lhs is None or lhs == '')) and (not (rhs is None or rhs == '')):
                lhs = unicode_to_float_int(lhs)
                rhs = unicode_to_float_int(rhs)

                if type(lhs) != type(rhs):
                    log.warning("trying again. Unable to compare {} of {} with {} of {}".format(repr(lhs), repr(type(lhs)), repr(rhs), repr(type(rhs))))
                    if values:
                        values = get_data_window_indicator_values(browser, indicator)
                    return is_indicator_triggered(browser, indicator, values, previous_symbol_values)

                if previous_symbol_values[0] == lhs and previous_symbol_values[1] == rhs:
                    log.warning("{}: detected the exact same values ({}, {}) as previous market. Verifying ...".format(repr(indicator['name']), repr(previous_symbol_values[0]), repr(previous_symbol_values[1])))
                    time.sleep(DELAY_BREAK_MINI)
                    if values:
                        values = get_data_window_indicator_values(browser, indicator)
                    return is_indicator_triggered(browser, indicator, values, ['', ''])

            try:
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
            except Exception as e:
                log.debug(e)

            log.debug('{} {} {} returned {}'.format(repr(lhs), comparison, repr(rhs), repr(result)))
            previous_symbol_values = [lhs, rhs]
        else:
            log.debug('No trigger information found, returning True')
            result = True
    except Exception as e:
        log.exception(e)
    return result, previous_symbol_values


def save_data_as_json(data, save_as):
    filename = "{}_{}.json".format(save_as, datetime.datetime.today().strftime('%Y%m%d_%H%M'))
    if not os.path.exists('output'):
        os.mkdir('output')
    filename = os.path.join('output', filename)
    with open(filename, 'w+', encoding="utf-8") as file:
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
        log.info("opening chart " + chart['url'])

        # set wait times defined in chart
        set_delays(chart)
        set_options(chart)
        log.info("WAIT_TIME_IMPLICIT = " + str(WAIT_TIME_IMPLICIT))
        log.info("PAGE_LOAD_TIMEOUT = " + str(PAGE_LOAD_TIMEOUT))
        log.info("CHECK_IF_EXISTS_TIMEOUT = " + str(CHECK_IF_EXISTS_TIMEOUT))
        log.info("DELAY_BREAK_MINI = " + str(DELAY_BREAK_MINI))
        log.info("DELAY_BREAK = " + str(DELAY_BREAK))
        log.info("DELAY_SUBMIT_ALERT = " + str(DELAY_SUBMIT_ALERT))
        log.info("DELAY_CHANGE_SYMBOL = " + str(DELAY_CHANGE_SYMBOL))
        log.info("DELAY_CLEAR_INACTIVE_ALERTS = " + str(DELAY_CLEAR_INACTIVE_ALERTS))
        log.info("DELAY_KEYSTROKE = " + str(DELAY_KEYSTROKE))
        log.info("DELAY_READ_INDICATOR_VALUE = " + str(DELAY_READ_INDICATOR_VALUE))
        log.info("READ_FROM_DATA_WINDOW = " + str(READ_FROM_DATA_WINDOW))
        log.info("WAIT_UNTIL_CHART_IS_LOADED = " + str(WAIT_UNTIL_CHART_IS_LOADED))
        log.info("READ_ALL_VALUES_AT_ONCE = " + str(READ_ALL_VALUES_AT_ONCE))
        log.info("CHANGE_SYMBOL_WITH_SPACE = " + str(CHANGE_SYMBOL_WITH_SPACE))
        log.info("VERIFY_MARKET_LISTING = " + str(VERIFY_MARKET_LISTING))
        print('')

        url = unquote(chart['url'])
        browser.execute_script("window.open('" + url + "');")
        for handle in browser.window_handles[1:]:
            browser.switch_to.window(handle)

        wait_and_click(browser, css_selectors['btn_calendar'], 30)
        wait_and_click(browser, css_selectors['btn_watchlist'])
        time.sleep(DELAY_WATCHLIST)

        # get the symbols for each watchlist
        dict_watchlist = dict()
        for i, watchlist in enumerate(chart['watchlists']):
            watchlist = chart['watchlists'][i]
            # open list of watchlists element
            log.debug("collecting symbols from watchlist {}".format(watchlist))
            wait_and_click(browser, css_selectors['btn_watchlist_menu_menu'])

            # load watchlist
            watchlist_exists = False
            el_options = find_elements(browser, css_selectors['options_watchlist'])
            for option in el_options:
                if option.text == watchlist:
                    option.click()
                    watchlist_exists = True
                    log.debug("watchlist '{}' found".format(watchlist))
                    break

            if watchlist_exists:

                # move to first element in the watchlist
                previous_first_element_symbol = "NA"
                first_element_symbol = ""
                stop = False
                while not stop:
                    element = find_element(browser, "{}:nth-child(1)".format(css_selectors['div_watchlist_item']))
                    action = ActionChains(browser)
                    action.move_to_element(element)
                    action.perform()
                    time.sleep(DELAY_BREAK*2)
                    first_element_symbol = element.get_attribute('data-symbol-full')
                    if first_element_symbol == previous_first_element_symbol:
                        stop = True

                    previous_first_element_symbol = first_element_symbol

                # click on first symbol
                selector = css_selectors['div_watchlist_item_by_symbol'].format(first_element_symbol)
                wait_and_click(browser, selector)

                previous_last_element_symbol = "NA"
                last_element_symbol = ""
                symbols = []
                stop = False
                while not stop:
                    # 1. find all elements and extract symbol
                    # extract symbols from watchlist
                    try:
                        dict_symbols = find_elements(browser, css_selectors['div_watchlist_item'], By.CSS_SELECTOR,
                                                     True, False, 30)
                        for symbol in dict_symbols:
                            last_element_symbol = symbol.get_attribute('data-symbol-full')
                            symbols.append(last_element_symbol)
                            if len(symbols) >= config.getint('tradingview', 'max_symbols_per_watchlist'):
                                break

                        # 2. move to the last found element
                        selector = css_selectors['div_watchlist_item_by_symbol'].format(last_element_symbol)
                        element = find_element(browser, selector)
                        action = ActionChains(browser)
                        action.move_to_element(element)
                        action.perform()

                        if previous_last_element_symbol == last_element_symbol:
                            stop = True
                        previous_last_element_symbol = last_element_symbol

                    except Exception as e:
                        log.exception(e)
                        snapshot(browser)

                # symbols = list(sorted(set(symbols)))
                symbols = list(set(symbols))
                dict_watchlist[chart['watchlists'][i]] = symbols
                log.info("{}: {} markets found".format(watchlist, len(symbols)))

        # close the watchlist menu to save some loading time
        wait_and_click(browser, css_selectors['btn_watchlist'])
        if 'backtest' in chart:
            # open data window tab
            # check if data window is open
            date = datetime.datetime.strptime(time.strftime('%Y-%m-%dT%H:%M:%S%z', time.localtime()), '%Y-%m-%dT%H:%M:%S%z')
            if not element_exists(browser, 'div.widgetbar-page.active > div.widgetbar-widget.widgetbar-widget-datawindow'):
                wait_and_click_by_xpath(browser, '//div[@data-name="data-window"]')

            summaries = dict()
            summaries['chart'] = chart['url']
            summaries['datetime'] = date.strftime('%Y-%m-%d %H:%M:%S %z')

            # Sort if the user defined one for all strategies. This overrides sorting on a per strategy basis.
            sort = dict()
            for indicator in chart['backtest']:
                if 'sort' in indicator:
                    sort = indicator['sort']
                    log.info(sort)
                    continue

                data = dict()
                if 'data' in indicator and indicator['data']:
                    for key in indicator['data']:
                        options = indicator['data'][key]
                        if key in data:
                            log.exception("tag {} has been defined twice under 'data' within your YAML. Make sure that tags are unique among the combined set of tags under 'data' and 'calculate.'".format(key))
                            exit(0)

                        try:
                            data[key] = {'value': '', 'decimals': 0, 'show': True}
                            if 'decimals' in options and isinstance(options['decimals'], int):
                                data[key]['decimals'] = options['decimals']
                            if 'show' in options and isinstance(options['show'], bool):
                                data[key]['show'] = options['show']
                        except Exception as e:
                            log.exception(e)
                            snapshot(browser, True)
                else:
                    log.exception("missing tag 'data' for indicator {} within your YAML. Please define which data you wish to extract.".format(indicator['name']))
                    exit(0)
                if 'calculate' in indicator and indicator['calculate']:
                    for key in indicator['calculate']:
                        options = indicator['calculate'][key]
                        if key in data:
                            log.exception("tag {} has been defined under 'calculate' while already been defined under 'data' within your YAML. Make sure that tags are unique among the combined set of tags under 'data' and 'calculate.'".format(key))
                            exit(0)

                        try:
                            data[key] = {'value': '', 'sum': '', 'decimals': 0, 'show': True}
                            if 'decimals' in options and isinstance(options['decimals'], int):
                                data[key]['decimals'] = options['decimals']
                            if 'show' in options and isinstance(options['show'], bool):
                                data[key]['show'] = options['show']
                            if 'sum' in options and options['sum']:
                                data[key]['sum'] = options['sum']
                            else:
                                log.exception("missing tag 'sum' under {} or it's value is undefined within your YAML. Make sure that the tag exists and has a value.".format(key))
                                exit(0)
                        except Exception as e:
                            log.exception(e)
                            snapshot(browser, True)

                indicator['full_name'] = indicator['name']
                if not indicator['name'] in summaries:
                    summaries[indicator['name']] = dict()
                    summaries[indicator['name']]['id'] = indicator['name']
                    default_chart_inputs = dict()

                    xpath = '//div[@data-name="legend-source-item"]/div/div/div[starts-with(text(), "{}")]'.format(indicator['name'])
                    indicator_element = find_element(browser, xpath, By.XPATH)
                    try:
                        indicator['full_name'] = indicator_element.text
                        # open the indicator settings
                        open_indicator_settings(browser, indicator['name'])
                        # get the default indicator inputs
                        default_chart_inputs = get_indicator_dialog_values(browser)
                        # close the indicator settings dialog
                        close_indicator_settings(browser)
                    except StaleElementReferenceException:
                        pass
                    except Exception as e:
                        log.exception(e)
                        snapshot(browser)
                    log.info("default_inputs: {}".format(default_chart_inputs))
                    summaries[indicator['name']]['default_inputs'] = default_chart_inputs
                else:
                    # ensure fall back to default inputs and properties
                    refresh(browser)

                # generate input/property sets
                atomic_inputs = []
                if 'inputs' in indicator:
                    inputs = get_config_values(indicator['inputs'])
                    generate_atomic_values(inputs, atomic_inputs)
                number_of_tests = max(len(atomic_inputs), 1)
                if number_of_tests > 1:
                    log.info("{} tests will be run for each watchlist".format(number_of_tests))
                else:
                    log.info("{} test will be run for each watchlist".format(number_of_tests))

                sort_by = False
                if 'sort_by' in indicator:
                    sort_by = indicator['sort_by']
                reverse = False
                if 'sort_asc' in indicator:
                    reverse = not indicator['sort_asc']

                open_data_window_tab(browser)
                move_to_data_window_indicator(browser, indicator)

                # test the strategy and sort the results
                for watchlist in chart['watchlists']:
                    symbols = dict_watchlist[watchlist]
                    test_data = test_indicators(browser, indicator, symbols, data, atomic_inputs)
                    # sort if the user defined one for the indicator
                    if sort_by:
                        test_data = back_test_sort_watchlist(test_data, sort_by, reverse)

                    if watchlist in summaries[indicator['name']]:
                        summaries[indicator['name']][watchlist] += test_data
                    else:
                        summaries[indicator['name']][watchlist] = test_data

            # Sort if the user defined one for all strategies. This overrides sorting on a per strategy basis.
            if sort:
                log.info('sort')
                if 'sort_by' in sort:
                    sort_by = sort['sort_by']
                    reverse = False
                    if 'sort_asc' in sort:
                        reverse = not sort['sort_asc']
                    back_test_sort(summaries, sort_by, reverse)

            # Save the data
            filename = save_as
            match = re.search(r"([\w\-_]*)", save_as)
            if match:
                filename = match.group(1)
            elif save_as == "":
                filename = "run"
            save_data_as_json(json.dumps(summaries, indent=4), filename)

        if 'strategies' in chart:
            date = datetime.datetime.strptime(time.strftime('%Y-%m-%dT%H:%M:%S%z', time.localtime()), '%Y-%m-%dT%H:%M:%S%z')
            btn_strategy_inactive = find_element(browser, css_selectors['tab_strategy_tester_inactive'], By.CSS_SELECTOR, False, True)
            if btn_strategy_inactive:
                btn_strategy_inactive.click()
                btn_performance_tab = find_element(browser, css_selectors['tab_strategy_tester_performance_summary'], By.CSS_SELECTOR, False, True)
                if btn_performance_tab:
                    btn_performance_tab.click()

            summaries = dict()
            summaries['chart'] = chart['url']
            summaries['datetime'] = date.strftime('%Y-%m-%d %H:%M:%S %z')

            # Sort if the user defined one for all strategies. This overrides sorting on a per strategy basis.
            sort = dict()
            for strategy in chart['strategies']:
                if 'sort' in strategy:
                    sort = strategy['sort']
                    log.info(sort)
                    continue
                log.info("running strategy {}".format(strategy['name']))
                if not strategy['name'] in summaries:
                    summaries[strategy['name']] = dict()
                    summaries[strategy['name']]['id'] = "unknown"
                    strategy_element = find_element(browser, css_selectors['strategy_id'])
                    if strategy_element:
                        summaries[strategy['name']]['id'] = strategy_element.text
                    default_chart_inputs, default_chart_properties = get_strategy_default_values(browser)
                    log.info("default_inputs: {}".format(default_chart_inputs))
                    log.info("default_properties: {}".format(default_chart_properties))
                    summaries[strategy['name']]['default_inputs'] = default_chart_inputs
                    summaries[strategy['name']]['default_properties'] = default_chart_properties
                else:
                    # ensure fall back to default inputs and properties
                    refresh(browser)

                # generate input/property sets
                atomic_inputs = []
                atomic_properties = []
                if 'inputs' in strategy:
                    inputs = get_config_values(strategy['inputs'])
                    generate_atomic_values(inputs, atomic_inputs)
                if 'properties' in strategy:
                    properties = get_config_values(strategy['properties'])
                    generate_atomic_values(properties, atomic_properties)
                log.info("{} tests will be run for each watchlist".format(max(1, len(atomic_inputs)) * max(1, len(atomic_properties))))

                sort_by = False
                if 'sort_by' in strategy:
                    sort_by = strategy['sort_by']
                reverse = False
                if 'sort_asc' in strategy:
                    reverse = not strategy['sort_asc']

                # test the strategy and sort the results
                for watchlist in chart['watchlists']:
                    symbols = dict_watchlist[watchlist]
                    test_data = back_test(browser, strategy, symbols, atomic_inputs, atomic_properties)
                    # sort if the user defined one for the strategy
                    if sort_by:
                        test_data = back_test_sort_watchlist(test_data, sort_by, reverse)

                    if watchlist in summaries[strategy['name']]:
                        summaries[strategy['name']][watchlist] += test_data
                    else:
                        summaries[strategy['name']][watchlist] = test_data

            # Sort if the user defined one for all strategies. This overrides sorting on a per strategy basis.
            if sort:
                log.info('sort')
                if 'sort_by' in sort:
                    sort_by = sort['sort_by']
                    reverse = False
                    if 'sort_asc' in sort:
                        reverse = not sort['sort_asc']
                    back_test_sort(summaries, sort_by, reverse)

            # Save the results
            filename = save_as
            match = re.search(r"([\w\-_]*)", save_as)
            if match:
                filename = match.group(1)
            elif save_as == "":
                filename = "run"
            save_data_as_json(json.dumps(summaries, indent=4), filename)

        export_data = 'export_data' in chart and 'enabled' in chart['export_data'] and chart['export_data']['enabled']
        if 'alerts' in chart or 'signals' in chart or export_data:
            # time.sleep(5)
            # set the time frame
            for timeframe in chart['timeframes']:
                set_timeframe(browser, timeframe)
                time.sleep(DELAY_TIMEFRAME)

                # iterate over each symbol per watchlist
                for watchlist in chart['watchlists']:
                    log.info("opening watchlist " + watchlist)
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


def is_market_listed(browser):
    """
    Checks if a market is listed
    NOTE: requires the chart and the data window tab to be open
    :param browser:
    :return: bool, whether the market is listed
    """
    listed = False
    try:
        xpath = '//div[not(contains(@class, "hidden"))]/div[@class="chart-data-window-header"]/span[contains(text(), ",")][1]'
        listed = element_exists(browser, xpath, CHECK_IF_EXISTS_TIMEOUT, By.XPATH)
    except StaleElementReferenceException:
        return is_market_listed(browser)
    except Exception as e:
        log.exception(e)
        snapshot(browser)
    return listed


def process_symbols(browser, chart, symbols, timeframe, counter_alerts, total_alerts):
    # open data window when necessary
    open_data_window_tab(browser)
    symbols = list(sorted(set(symbols)))

    # open each symbol within the watchlist
    last_indicator_name = ''
    delisted_markets = []
    previous_symbol_values = [None, None]
    for k, symbol in enumerate(symbols):
        # change symbol
        change_symbol(browser, symbol, CHANGE_SYMBOL_WITH_SPACE)
        wait_until_chart_is_loaded(browser)
        # check if market is listed
        if (not VERIFY_MARKET_LISTING) or is_market_listed(browser):
            # process signals
            [counter_alerts, total_alerts, last_indicator_name, previous_symbol_values] = process_symbol(browser, chart, symbols[k], timeframe, last_indicator_name, counter_alerts, total_alerts, previous_symbol_values)
        else:
            delisted_markets.append(symbol)

    # close data window
    if element_exists(browser, 'div.widgetbar-page.active > div.widgetbar-widget.widgetbar-widget-datawindow'):
        wait_and_click_by_xpath(browser, '//div[@data-name="data-window"]')

    if len(delisted_markets) > 0:
        verb = 's are'
        if len(delisted_markets) == 1:
            verb = ' is'
        log.warn("the following market{} delisted: {}".format(verb, ', '.join(delisted_markets)))

    return counter_alerts, total_alerts


def get_number_of_alerts_on_alerts_tab(browser):
    # set alerts counter
    # open alerts tab if unopened
    alerts_on_alerts_tab = 0
    try:
        if not find_element(browser, css_selectors['btn_alert_menu'], By.CSS_SELECTOR, False, True):
            wait_and_click(browser, css_selectors['btn_alerts'])
        element = find_element(browser, css_selectors['alerts_counter'], except_on_timeout=False)
        if element:
            element_text = element.get_attribute('textContent').strip()
            match = re.search("(\\d+)", element_text)
            if match:
                alerts_on_alerts_tab = int(match.group(1))

        # close alerts tab if opened
        if find_element(browser, css_selectors['btn_alert_menu'], By.CSS_SELECTOR, False, True):
            wait_and_click(browser, css_selectors['btn_alerts'])
    except Exception as e:
        log.exception(e)
    return alerts_on_alerts_tab


def change_symbol(browser, symbol, use_space=False):
    # change symbol
    try:
        # Try to browse through the watchlist using space instead of setting the symbol value
        if use_space:
            action = ActionChains(browser)
            action.send_keys(Keys.SPACE)
            action.perform()
        else:
            # might be useful for multi threading set the symbol by going to different url like this:
            # https://www.tradingview.com/chart/?symbol=BINANCE%3AAGIBTC
            wait_and_click(browser, css_selectors['btn_input_symbol'])
            dlg_symbol_search_input = find_element(browser, css_selectors['dlg_symbol_search_input'])
            set_value(browser, dlg_symbol_search_input, symbol)
            dlg_symbol_search_input.send_keys(Keys.ENTER)

    except Exception as err:
        log.debug('unable to change to symbol')
        log.exception(err)
        snapshot(browser)


def read_price(browser, tries=0):
    # open, high, close, low, change = 'undefined', 'undefined', 'undefined', 'undefined', 'undefined'
    result = []
    max_tries = 100
    try:
        current_price_values = find_elements(browser, 'div[data-name="legend-series-item"] div[class^="valueValue"]')
        for i, element in enumerate(current_price_values):
            value = str(element.text)
            if value:
                result.append(str(value).translate({0x2c: '.', 0xa0: None, 0x2212: '-'}))
        if len(result) != 5:
            result = read_price(browser, tries+1)
    except StaleElementReferenceException as e:
        pass
        if tries >= max_tries:
            log.exception(e)
        else:
            return read_price(browser, tries+1)
    except Exception as e:
        log.exception(e)
    assert(len(result) == 5)
    return result


def process_symbol(browser, chart, symbol, timeframe, last_indicator_name, counter_alerts, total_alerts, previous_symbol_values, retry_number=0):
    log.info(symbol)

    previous_values = []
    first_signal = True
    is_a_signal_triggered = False
    export_data_config = []
    export_data_always = False
    export_data_on_signal = False
    if 'export_data' in chart and 'enabled' in chart['export_data'] and chart['export_data']['enabled']:
        export_data_config = chart['export_data']
        export_data_on_signal = 'on_signal_only' in export_data_config and export_data_config['on_signal_only']
        export_data_always = not export_data_on_signal

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
                        log.warning('charts: multi_time_frame_layout not set in yaml, defaulting to multi_time_frame_layout = no')
                if type(interval) is str and len(interval) > 0 and not multi_time_frame_layout:
                    url += '&interval=' + str(interval)
                data['url'] = url

                signal_triggered = True
                for m, indicator in enumerate(indicators):
                    indicator = indicators[m]
                    values = []
                    max_bars = 1

                    if first_signal or (last_indicator_name != indicator['name']):
                        first_signal = False
                        if READ_FROM_DATA_WINDOW:
                            # Stop processing the symbol if we cannot move to the indicator on the data window.
                            # For example, when there is not enough data because it is a new market.
                            if not move_to_data_window_indicator(browser, indicator):
                                signal_triggered = False
                                continue

                            wait_until_indicator_values_are_loaded(browser, indicator)
                        else:
                            time.sleep(DELAY_READ_INDICATOR_VALUE)
                        if 'max_bars' in indicator and indicator['max_bars']:
                            max_bars = max(max_bars, int(indicator['max_bars']))

                    bar = 0
                    indicator_triggered = False
                    while bar < max_bars and not indicator_triggered:
                        # move the cursor to the current bar
                        if bar == 1:
                            try:
                                wait_and_click(browser, 'div.control-bar__btn--back-present', 0.5)
                            except TimeoutException:
                                pass
                            except Exception as e:
                                log.exception(e)
                                snapshot(browser)

                            css = 'div.js-btn-reset'
                            reset_chart_button = find_element(browser, css)
                            hover(browser, reset_chart_button, True)
                            ActionChains(browser).move_to_element_with_offset(find_element(browser, 'div[id="header-toolbar-screenshot"]'), 14, 80).click().perform()
                            ActionChains(browser).send_keys(Keys.ESCAPE).perform()
                            prices = read_price(browser)
                            current_open = prices[0]

                            # press left until the first change
                            max_tries = 100
                            for i in range(max_tries):
                                prices = read_price(browser)
                                bar_open = prices[0]
                                if bar_open == current_open:
                                    action = ActionChains(browser)
                                    action.send_keys(Keys.ARROW_LEFT)
                                    action.perform()
                                else:
                                    # log.info("Previous bar (-1) found after {} left arrow presses (open = {})".format(i+1, bar_open))
                                    break
                            previous_values = []
                        elif bar > 1:
                            # press left
                            action = ActionChains(browser)
                            action.send_keys(Keys.ARROW_LEFT)
                            action.perform()
                            previous_values = []

                        if READ_ALL_VALUES_AT_ONCE or not READ_FROM_DATA_WINDOW:
                            # read all the indicator values
                            if previous_values:
                                values = previous_values
                            elif READ_FROM_DATA_WINDOW:
                                # read from the data window tab
                                # log.info('reading from data window')
                                values = get_data_window_indicator_values(browser, indicator)
                            else:
                                # read from the chart
                                # log.info('reading from chart')
                                values = get_indicator_values(browser, indicator, symbol, previous_symbol_values)
                            # log.info(values)
                            if (not values) and retry_number < config.getint('tradingview', 'create_alert_max_retries'):
                                return retry_process_symbol(browser, chart, symbol, timeframe, last_indicator_name, counter_alerts, total_alerts, previous_symbol_values, retry_number)
                            previous_values = values

                        # log.info(values)
                        indicator_triggered, previous_symbol_values = is_indicator_triggered(browser, indicator, values, previous_symbol_values)
                        bar += 1

                    # after the first run, clear the previous_symbol_values
                    previous_symbol_values = ['', '']
                    last_indicator_name = indicator['name']

                    # if the indicator didn't get triggered we might just as well stop here
                    if not indicator_triggered:
                        signal_triggered = False
                        break
                    else:
                        bar -= 1
                        if bar == 0:
                            log.debug("{} triggered at the current bar".format(indicator['name']))
                        else:
                            log.debug("{} triggered at -{} bars".format(indicator['name'], bar))

                    signal['indicators'][m]['values'] = values
                    signal['indicators'][m]['triggered'] = indicator_triggered
                    signal['indicators'][m]['bar'] = bar
                    triggered.append(indicator_triggered)
                    if 'data' in indicator:
                        for item in indicator['data']:
                            for _key in item:
                                if not (_key in data):
                                    if isinstance(item[_key], list):
                                        indices = item[_key]
                                        data[_key] = []
                                        if values:
                                            for index in indices:
                                                try:
                                                    data[_key].append(values[index])
                                                except IndexError as e:
                                                    text = ""
                                                    if not READ_FROM_DATA_WINDOW:
                                                        text = " and is visible"
                                                    log.exception(
                                                        "Cannot read index {} as defined at {} in your YAML (index out of bounds). Make sure your indicator has a value at index {}{}.".format(index, _key, index, text))
                                                    log.exception(e)
                                                    snapshot(browser)
                                                    exit(0)
                                                except Exception as e:
                                                    log.exception(e)
                                                    snapshot(browser)
                                                    exit(0)
                                        else:
                                            for index in indices:
                                                data[_key].append(get_data_window_indicator_value(browser, indicator, index))
                                    else:
                                        index = item[_key]
                                        if values:
                                            try:
                                                data[_key] = values[index]
                                            except IndexError:
                                                text = ""
                                                if not READ_FROM_DATA_WINDOW:
                                                    text = "and is visible"
                                                log.exception("Cannot read index {} as defined at {} in your YAML (index out of bounds). Make sure your indicator has a value at {} {}.".format(index, _key, index, text))
                                                log.exception("data[{}] = {}".format(_key, values))
                                                snapshot(browser)
                                                exit(0)
                                            except Exception as e:
                                                log.exception(e)
                                                snapshot(browser)
                                                exit(0)
                                        else:
                                            data[_key] = get_data_window_indicator_value(browser, indicator, index)

                    # use tab to put focus on the next layout
                    # TODO replace 'element.send_keys" with
                    #  action = ActionChains(browser)
                    #  action.send_keys(Keys.TAB)
                    #  action.perform()
                    html = find_element(browser, 'html', By.TAG_NAME)
                    html.send_keys(Keys.TAB)

                if signal_triggered:
                    is_a_signal_triggered = True
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
                            log.warning('charts: include_screenshots_of_charts not set in yaml, defaulting to default screenshot')
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
                    triggered_signals.append(data)

        if 'alerts' in chart:
            interval = get_interval(timeframe)
            for alert in chart['alerts']:
                alerts_on_alerts_tab = get_number_of_alerts_on_alerts_tab(browser)
                if alerts_on_alerts_tab >= config.getint('tradingview', 'max_alerts') and config.getboolean('tradingview', 'clear_inactive_alerts'):
                    # try clean inactive alerts first
                    # open alerts tab
                    if not find_element(browser, css_selectors['btn_alert_menu'], By.CSS_SELECTOR, False, True):
                        wait_and_click(browser, css_selectors['btn_alerts'])
                    time.sleep(DELAY_CLEAR_INACTIVE_ALERTS)
                    wait_and_click(browser, css_selectors['btn_alert_menu'])
                    wait_and_click(browser, css_selectors['item_clear_inactive_alerts'])
                    wait_and_click(browser, css_selectors['btn_dlg_clear_alerts_confirm'])
                    time.sleep(DELAY_BREAK * 8)

                alerts_on_alerts_tab = get_number_of_alerts_on_alerts_tab(browser)
                if alerts_on_alerts_tab >= config.getint('tradingview', 'max_alerts'):
                    log.warning("Maximum alerts reached. You can set this to a higher number in the kairos.cfg. Exiting program.")
                    return [counter_alerts, total_alerts]
                try:
                    screenshot_url = ''
                    if config.has_option('logging', 'screenshot_timing') and config.get('logging', 'screenshot_timing') == 'alert':
                        screenshot_url = take_screenshot(browser, symbol, interval)[0]
                    create_alert(browser, alert, timeframe, interval, symbol, screenshot_url)
                    counter_alerts += 1
                except Exception as err:
                    log.error("Could not set alert: {} {}".format(symbol, alert['name']))
                    log.exception(err)
                    snapshot(browser)

        # export data
        if export_data_config and (export_data_always or is_a_signal_triggered and export_data_on_signal):
            export_chart_data(browser, export_data_config, symbol)

        if 'signals' in chart or 'alerts' in chart:
            total_alerts += 1
    except Exception as e:

        log.exception(e)
        return retry_process_symbol(browser, chart, symbol, timeframe, last_indicator_name, counter_alerts, total_alerts, previous_symbol_values, retry_number)
    return [counter_alerts, total_alerts, last_indicator_name, previous_symbol_values]


def retry_process_symbol(browser, chart, symbol, timeframe, last_indicator_name, counter_alerts, total_alerts, previous_symbol_values, retry_number=0):
    if retry_number < config.getint('tradingview', 'create_alert_max_retries'):
        log.info('trying again ({})'.format(str(retry_number + 1)))
        refresh(browser)
        try:
            # might be useful for multi threading set the symbol by going to different url like this:
            # https://www.tradingview.com/chart/?symbol=BINANCE%3AAGIBTC
            input_symbol = find_element(browser, css_selectors['input_symbol'])
            set_value(browser, input_symbol, symbol)
            input_symbol.send_keys(Keys.ENTER)
        except Exception as err:
            log.debug('Unable to change to symbol')
            log.exception(err)
            snapshot(browser)
        return process_symbol(browser, chart, symbol, timeframe, last_indicator_name, counter_alerts, total_alerts, previous_symbol_values, retry_number + 1)
    else:
        log.error('Max retries reached.')
        if symbol not in processing_errors:
            processing_errors.append(symbol)
        snapshot(browser)
        return False


def export_chart_data(browser, export_data_config, symbol):
    try:
        # open dialog
        css = 'div.layout__area--topleft div[data-role="button"]'
        wait_and_click(browser, css)
        css = 'div[class^="popupMenu"] div[data-name="menu-inner"] > div:nth-child(7)'
        wait_and_click(browser, css)
        # time.sleep(DELAY_BREAK*4)

        # make sure the correct symbol is loaded
        correct = False
        i = 0
        selected = ''
        while not correct and i < 20:
            i += 1
            css = 'span[id="chart-select"] > span:nth-child(1) > span > span'
            el_selected_chart = find_element(browser, css)
            selected = str(el_selected_chart.get_attribute("innerHTML")).strip()
            if selected.startswith(symbol):
                correct = True
            else:
                time.sleep(DELAY_BREAK_MINI)
        # if the correct symbol isn't loaded
        if not correct:
            msg = "Export chart data dialog: selected ticker '{}' differs from expected ticker '{}'".format(selected, symbol)
            raise Exception(msg)
        log.info("selected = {}".format(selected))
        # set correct chart
        if 'chart_index' in export_data_config and export_data_config['chart_index']:
            chart_number = int(export_data_config['chart_index'])+1
            css = 'span[id="chart-select"]'
            wait_and_click(browser, css)
            css = 'div[data-name="menu-inner"] div[role="option"]:nth-child({})'.format(chart_number)
            el_correct_option = find_element(browser, css)
            hover(browser, el_correct_option, True)
            time.sleep(DELAY_BREAK_MINI)

        # set correct time format
        if 'timeformat' in export_data_config and export_data_config['timeformat']:
            timeformat = export_data_config['timeformat']
            css = 'span[id="time-format-select"]'
            wait_and_click(browser, css)
            css = 'div[data-name="menu-inner"] div[role="option"] > div > div'
            el_options = find_elements(browser, css)
            found = False
            for option in el_options:
                option_tv = str(option.get_attribute("innerHTML")).strip()
                if (option_tv == timeformat) or ((not EXACT_CONDITIONS) and option_tv.startswith(timeformat)):
                    hover(browser, option, True)
                    found = True
                    break
            if not found:
                log.warning("Option {} not found in 'Export chart data ...' dialog. Defaulting to UNIX timestamp.".format(timeformat))

        # click on export
        # time.sleep(DELAY_BREAK*4)
        css = 'div[data-name="chart-export-dialog"] button[name="submit"]'
        wait_and_click(browser, css)

    except Exception as e:
        log.exception(e)


def wait_until_chart_is_loaded(browser):
    if WAIT_UNTIL_CHART_IS_LOADED:
        #########################################################################################################
        # Wait until the chart is loaded.
        # NOTE: indicators are also checked if they are loaded before reading their values
        #########################################################################################################
        # xpath_loading = "//*[matches(text(),'(loading|compiling|error)','i')]"
        xpath_loading = "//*[matches(text(),'(loading|compiling)','i')]"
        elem_loading = find_elements(browser, xpath_loading, By.XPATH, False, True, DELAY_BREAK_MINI)
        while elem_loading and len(elem_loading) > 0:
            elem_loading = find_elements(browser, xpath_loading, By.XPATH, False, DELAY_BREAK_MINI)
    else:
        time.sleep(DELAY_CHANGE_SYMBOL)


def snapshot(browser, quit_program=False, chart_only=True, name='', debug=False):
    global MAX_SCREENSHOTS_ON_ERROR
    if (config.has_option('logging', 'screenshot_on_error') and config.getboolean('logging', 'screenshot_on_error') and MAX_SCREENSHOTS_ON_ERROR > 0) or debug:
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
            if chart_only:
                im = im.crop((int(x), int(y), int(width), int(height)))
            im.save(filename)
            if debug:
                log.info(str(filename))
            else:
                log.error(str(filename))
        except Exception as take_screenshot_error:
            log.exception(take_screenshot_error)
        if quit_program:
            write_console_log(browser)
            exit(errno.EFAULT)


def take_screenshot(browser, symbol, interval, chart_only=True, tpl_strftime="%Y%m%d", retry_number=0):
    """
    Use selenium for a screenshot, or alternatively use TradingView's screenshot feature
    :param browser:
    :param symbol:
    :param interval:
    :param chart_only:
    :param tpl_strftime:
    :param retry_number:
    :return:
    """
    screenshot_url = ''
    filename = ''

    try:
        if config.has_option('tradingview', 'tradingview_screenshot') and config.getboolean('tradingview', 'tradingview_screenshot'):
            # get current window/tab
            previous_window = browser.current_window_handle
            windows = browser.window_handles
            # open image in new tab
            wait_and_click(browser, css_selectors['btn_screenshot'])
            wait_and_click(browser, css_selectors['btn_image_url'])

            # wait in increments of 0.1 seconds until tab has opened
            i = 0
            while windows == browser.window_handles and i < 300:
                time.sleep(0.1)
                i += 1
            if i == 300:
                raise Exception("Twitter did not open in new window")

            # switch to the newly opened browser tab
            for window in browser.window_handles:
                if window not in windows:
                    browser.switch_to.window(window)
            # extract the url
            elem_image = find_element(browser, css_selectors['img_chart'])
            screenshot_url = elem_image.get_attribute('src')
            # close the newly opened tab
            browser.close()
            browser.switch_to_window(previous_window)
            log.debug(screenshot_url)

        elif screenshot_dir != '':
            chart_dir = ''
            match = re.search(r"^.*chart.(\w+).*", browser.current_url)
            if re.Match:
                today_dir = os.path.join(screenshot_dir, datetime.datetime.today().strftime(tpl_strftime))
                if not os.path.exists(today_dir):
                    os.mkdir(today_dir)
                chart_dir = os.path.join(today_dir, match.group(1))
                if not os.path.exists(chart_dir):
                    os.mkdir(chart_dir)
                chart_dir = os.path.join(chart_dir, )
            filename = symbol.replace(':', '_') + '_' + str(interval) + '.png'
            filename = os.path.join(chart_dir, filename)
            elem_chart = find_element(browser, 'layout__area--center', By.CLASS_NAME)
            time.sleep(DELAY_SCREENSHOT)
            result = browser.save_screenshot(filename)
            log.info(result)

            if chart_only:
                location = elem_chart.location
                size = elem_chart.size
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
        return retry_take_screenshot(browser, symbol, interval, chart_only, tpl_strftime, retry_number)
    if screenshot_url == '' and filename == '':
        return retry_take_screenshot(browser, symbol, interval, chart_only, tpl_strftime, retry_number)

    return [screenshot_url, filename]


def retry_take_screenshot(browser, symbol, interval, chart_only, tpl_strftime, retry_number=0):

    if retry_number + 1 == config.getint('tradingview', 'create_alert_max_retries'):
        log.info('trying again ({})'.format(str(retry_number + 1)))
        refresh(browser)
        try:
            input_symbol = find_element(browser, css_selectors['input_symbol'])
            set_value(browser, input_symbol, symbol)
            input_symbol.send_keys(Keys.ENTER)
        except Exception as e:
            log.exception(e)
    elif retry_number < config.getint('tradingview', 'create_alert_max_retries'):
        log.info('trying again ({})'.format(str(retry_number + 1)))
        return take_screenshot(browser, symbol, interval, chart_only, tpl_strftime, retry_number + 1)
    else:
        log.warning('max retries reached')
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
    # noinspection PyGlobalUndefined
    global alert_dialog
    global SEARCH_FOR_WARNING
    try:
        indicators_present = False
        i = 0
        while not indicators_present and i < 20:
            html = find_element(browser, 'html')
            html.send_keys(Keys.ALT + "a")
            el_options = find_elements(browser, css_selectors['options_dlg_create_alert_first_row_first_item'], By.CSS_SELECTOR, False, False, 0.5)
            indicators_present = el_options is not None
            if not indicators_present:
                try:
                    wait_and_click(browser, css_selectors['btn_alert_cancel'], 0.1)
                except TimeoutException as e:
                    log.debug(e)
                time.sleep(1)
            i += 1

        if not indicators_present:
            log.error("Alert Dialog not loaded")

        # open the alert dialog
        # wait_and_click(browser, css_selectors['btn_create_alert'])

        # get the alert dialog element
        try:
            alert_dialog = find_element(browser, 'form.js-alert-form', By.CSS_SELECTOR, True, True, 2)
            log.debug(str(len(alert_config['conditions'])) + ' yaml conditions found')
        except TimeoutException:
            # open the alert dialog
            wait_and_click(browser, css_selectors['btn_create_alert'], 2)
            # time.sleep(1)
            alert_dialog = find_element(browser, 'form.js-alert-form', By.CSS_SELECTOR, True, True, 4)
        except Exception as e:
            log.exception(e)
            snapshot(browser)
            return retry(browser, alert_config, timeframe, interval, symbol, screenshot_url, retry_number)

        # 1st row, 1st condition
        current_condition = 0
        css_1st_row_left = css_selectors['dlg_create_alert_first_row_first_item']
        try:
            wait_and_click(alert_dialog, css_1st_row_left, 30)
        except Exception as alert_err:
            log.exception(alert_err)
            snapshot(browser)
            return retry(browser, alert_config, timeframe, interval, symbol, screenshot_url, retry_number)

        el_options = find_elements(alert_dialog, css_selectors['options_dlg_create_alert_first_row_first_item'])
        if not select(browser, alert_config, current_condition, el_options, symbol):
            return retry(browser, alert_config, timeframe, interval, symbol, screenshot_url, retry_number)

        # 1st row, 2nd condition (if applicable)
        if len(alert_config['conditions']) > 1:
            css_1st_row_right = css_selectors['exists_dlg_create_alert_first_row_second_item']
            if element_exists(alert_dialog, css_1st_row_right, 0.5):
                current_condition += 1
                wait_and_click(alert_dialog, css_selectors['dlg_create_alert_first_row_second_item'])
                el_options = find_elements(alert_dialog, css_selectors['options_dlg_create_alert_first_row_second_item'])
                if not select(browser, alert_config, current_condition, el_options, symbol):
                    return False

            # 2nd row, 1st condition
            current_condition += 1
            css_2nd_row = css_selectors['dlg_create_alert_second_row']
            wait_and_click(alert_dialog, css_2nd_row)
            el_options = find_elements(alert_dialog, css_selectors['options_dlg_create_alert_second_row'])
            if not select(browser, alert_config, current_condition, el_options, symbol):
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
        if 'options' in alert_config and alert_config['options']:
            button_name = 'N/A'
            try:
                button_name = str(alert_config['options']).strip()
                wait_and_click(alert_dialog, css_selectors['checkbox_dlg_create_alert_frequency'].format(button_name))
            except TimeoutException as e:
                log.exception("Unable to find button called '{}'.\nPlease, check if the value provided in your yaml (still) exists on TV.".format(button_name))
                log.exception(e)
                snapshot(browser, True)

        # Expiration
        if 'expiration' in alert_config and alert_config['expiration']:
            set_expiration(browser, alert_dialog, alert_config)

        # Toggle 'more actions'
        wait_and_click(alert_dialog, css_selectors['btn_toggle_more_actions'])

        # Show popup
        show_popup = 'show_popup' in alert_config and alert_config['show_popup']
        checkbox = find_element(alert_dialog, name_selectors['checkbox_dlg_create_alert_show_popup'], By.NAME)
        if is_checkbox_checked(checkbox) != show_popup:
            wait_and_click(alert_dialog, css_selectors['clickable_dlg_create_alert_show_popup'])

        # Sound
        play_sound = 'sound' in alert_config and 'play' in alert_config['sound'] and alert_config['sound']['play']
        checkbox = find_element(alert_dialog, name_selectors['checkbox_dlg_create_alert_play_sound'], By.NAME)
        if is_checkbox_checked(checkbox) != play_sound:
            wait_and_click(alert_dialog, css_selectors['clickable_dlg_create_alert_play_sound'])
        if is_checkbox_checked(checkbox):
            # set ringtone
            wait_and_click(alert_dialog, css_selectors['dlg_create_alert_ringtone'])
            el_options = find_elements(alert_dialog, css_selectors['options_dlg_create_alert_ringtone'])
            for option in el_options:
                option_value = str(option.get_attribute("textContent")).strip()
                if option_value == str(alert_config['sound']['ringtone']).strip():
                    option.click()
            # set duration
            wait_and_click(alert_dialog, css_selectors['dlg_create_alert_sound_duration'])
            el_options = find_elements(alert_dialog, css_selectors['options_dlg_create_alert_sound_duration'])
            for option in el_options:
                option_value = str(option.get_attribute("textContent")).strip()
                if option_value == str(alert_config['sound']['duration']).strip():
                    option.click()

        # Communication options
        # Send Email
        try:
            send_email = 'send' in alert_config and 'email' in alert_config['send'] and alert_config['send']['email']
            checkbox = find_element(alert_dialog, name_selectors['checkbox_dlg_create_alert_send_email'], By.NAME)
            if is_checkbox_checked(checkbox) != send_email:
                wait_and_click(alert_dialog, css_selectors['clickable_dlg_create_alert_send_email'])
            # Send Email-to-SMS (the checkbox is indeed called 'send-sms'!)
            send_email_to_sms = 'send' in alert_config and 'email-to-sms' in alert_config['send'] and alert_config['send']['email-to-sms']
            checkbox = find_element(alert_dialog, name_selectors['checkbox_dlg_create_alert_email_to_sms'], By.NAME)
            if is_checkbox_checked(checkbox) != send_email_to_sms:
                wait_and_click(alert_dialog, css_selectors['clickable_dlg_create_alert_send_email_to_sms'])
            # Notify on App
            notify_on_app = 'send' in alert_config and 'notify-on-app' in alert_config['send'] and alert_config['send']['notify-on-app']
            checkbox = find_element(alert_dialog, name_selectors['checkbox_dlg_create_alert_send_push'], By.NAME)
            if is_checkbox_checked(checkbox) != notify_on_app:
                wait_and_click(alert_dialog, css_selectors['clickable_dlg_create_alert_send_push'])

            # Webhook
            webhook = 'webhook' in alert_config and alert_config['webhook'] != ''
            checkbox = find_element(alert_dialog, name_selectors['checkbox_dlg_create_alert_webhook'], By.NAME)
            if is_checkbox_checked(checkbox) != webhook:
                wait_and_click(alert_dialog, css_selectors['clickable_dlg_create_alert_webhook'])
            if webhook:
                element = find_element(alert_dialog, css_selectors['dlg_create_alert_webhook'])
                set_value(browser, element, "")
                set_value(browser, element, alert_config['webhook'], False, True)

            # Alert name
            if 'name' in alert_config and alert_config['name'] != '':
                element = find_element(alert_dialog, css_selectors['dlg_create_alert_name'])
                set_value(browser, element, "")
                set_value(browser, element, alert_config['name'], False, True)

            # Construct message
            if 'message' in alert_config and alert_config['message'] != '':
                chart = browser.current_url + '?symbol=' + symbol
                show_multi_chart_layout = 'show_multi_chart_layout' in alert_config and alert_config['show_multi_chart_layout']
                if type(interval) is str and len(interval) > 0 and not show_multi_chart_layout:
                    chart += '&interval=' + str(interval)
                textarea = find_element(alert_dialog, 'description', By.NAME)
                """
                # This has stopped working. :( The text is visible but not set.           
                generated = textarea.text
                """
                generated = ''
                text = str(alert_config['message']['text']).replace('/r', '')
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
                    if len(screenshot_urls) > 0:
                        text += ' screenshots_to_include: ' + str(screenshot_urls).replace("'", "")
                except ValueError as value_error:
                    log.exception(value_error)
                    snapshot(browser)
                except KeyError:
                    log.debug('charts: include_screenshots_of_charts not set in yaml, defaulting to default screenshot')
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
                wait_and_click(browser, css_selectors['btn_create_alert_warning_continue_anyway_got_it'])
                wait_and_click(browser, css_selectors['btn_create_alert_warning_continue_anyway'])
                log.debug('warning found and closed')
            except TimeoutException:
                # we are getting a timeout exception because there likely was no warning
                log.debug('no warning found when setting the alert.')
                SEARCH_FOR_WARNING = False
    except TimeoutError:
        log.warning('time out')
        # on except, refresh and try again
        return retry(browser, alert_config, timeframe, interval, symbol, screenshot_url, retry_number)
    except Exception as exc:
        log.exception(exc)
        snapshot(browser)
        # on except, refresh and try again
        return retry(browser, alert_config, timeframe, interval, symbol, screenshot_url, retry_number)

    return True


def select(browser, alert_config, current_condition, el_options, ticker_id):
    log.debug('setting condition {0} to {1}'.format(str(current_condition + 1), alert_config['conditions'][current_condition]))
    value = str(alert_config['conditions'][current_condition])

    if value == "%SYMBOL":
        value = ticker_id.split(':')[1]

    found = False
    for option in el_options:
        option_tv = str(option.get_attribute("innerHTML")).strip()
        if (option_tv == value) or ((not EXACT_CONDITIONS) and option_tv.startswith(value)):
            hover(browser, option, True)
            found = True
            break
    if not found:
        log.error("Invalid condition ({}): '{}' in yaml definition '{}'. Did the title/name of the indicator/condition change?".format(str(current_condition + 1), alert_config['conditions'][current_condition], alert_config['name']))
    return found


def clear(element):
    element.clear()
    element.send_keys(SELECT_ALL)
    element.send_keys(Keys.DELETE)
    time.sleep(DELAY_BREAK_MINI * 0.5)


def send_keys(element, string, interval=DELAY_KEYSTROKE):
    if interval == 0:
        element.send_keys(string)
    else:
        for char in string:
            element.send_keys(char)
            time.sleep(interval)


def set_value(browser, element, string, use_clipboard=False, use_send_keys=False, interval=DELAY_KEYSTROKE):
    """
    element.parent.execute_script("
        var elm = arguments[0], text = arguments[1];
        if (!('value' in elm))
          throw new Error('Expected an <input> or <textarea>');
        elm.focus();
        elm.value = text;
        elm.dispatchEvent(new Event('change'));
        ", element, string)
    """
    if use_send_keys:
        send_keys(element, string, interval)
    else:
        browser.execute_script("arguments[0].value = arguments[1];".format(string), element, string)
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
            change_symbol(browser, symbol)
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
    clear(input_date)
    set_value(browser, input_date, date_value, False, True)
    input_time = find_element(_alert_dialog, 'alert_exp_time', By.NAME)
    time.sleep(DELAY_BREAK_MINI)
    clear(input_time)
    set_value(browser, input_time, time_value, False, True)
    send_keys(input_time, Keys.TAB)
    time.sleep(DELAY_BREAK_MINI)


def accept_cookies(browser):
    try:
        css = 'article h2'
        element = find_element(browser, css, By.CSS_SELECTOR, False, True, 2)
        if element and str(element.get_attribute('textContent')).find('cookies'):
            css = 'article h2 + p + div > button'
            element = find_element(browser, css, By.CSS_SELECTOR, False, True, 2)
            if element and str(element.get_attribute('textContent')) == 'Accept':
                element.click()
    except Exception as e:
        log.exception(e)


def login(browser, uid='', pwd='', retry_login=False):
    global TV_UID
    global TV_PWD
    global ALREADY_LOGGED_IN
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
                wait_and_click(browser, css_selectors['account'], 5)
                elem_username = wait_and_visible(browser, css_selectors['username'], 5)
                if type(elem_username) is WebElement:
                    if elem_username.get_attribute('textContent') != '' and elem_username.get_attribute('textContent') == uid:
                        ALREADY_LOGGED_IN = True
                        log.info("already logged in")
                        return True
                    else:
                        log.info("logged in under a different username. Logging out.")
                        wait_and_click(browser, css_selectors['account'])
                        wait_and_click(browser, css_selectors['signout'])
            except ElementClickInterceptedException as e:
                log.debug(e)
                wait_and_click(browser, css_selectors['btn_alerts'], 5)
                return login(browser, uid, pwd, False)
            except TimeoutException as e:
                log.debug(e)
            except Exception as e:
                log.exception(e)

        except Exception as e:
            log.exception(e)
            snapshot(browser, True)

    # close cookie banner (if any)
    accept_cookies(browser)

    try:
        wait_and_click(browser, css_selectors['anonymous_account'])
        wait_and_click(browser, css_selectors['anonymous_signin'])

        # check if we need to click "Login by email/username"
        try:
            wait_and_click(browser, css_selectors['btn_login_by_email'], 2)
        except TimeoutException:
            pass
        except Exception as e:
            log.exception(e)

        input_username = find_element(browser, css_selectors['input_username'])
        if input_username.get_attribute('value') == '' or retry_login:
            while uid == '':
                uid = input("type your TradingView username and press enter: ")

        input_password = find_element(browser, css_selectors['input_password'])
        if input_password.get_attribute('value') == '' or retry_login:
            while pwd == '':
                pwd = getpass.getpass("type your TradingView password and press enter: ")

        # set credentials on website login page
        if uid != '' and pwd != '':
            set_value(browser, input_username, uid)
            time.sleep(DELAY_BREAK_MINI)
            set_value(browser, input_password, pwd)
            time.sleep(DELAY_BREAK_MINI)
        # if there are no user credentials then exit
        else:
            log.info("no credentials provided.")
            write_console_log(browser)
            exit(0)

        send_keys(input_password, Keys.ENTER)
    except Exception as e:
        log.error(e)
        snapshot(browser, True)

    # close the widget pane if it is open
    try:
        if find_element(browser, css_selectors['active_widget_bar'], delay=2, except_on_timeout=False, visible=True):
            # close the menu/widget pane
            wait_and_click(browser, css_selectors['btn_alerts'])
            # check if we closed one pane but opened the alerts pane instead
            if find_element(browser, css_selectors['active_widget_bar'], delay=2, except_on_timeout=False, visible=True):
                # close the alerts pane
                wait_and_click(browser, css_selectors['btn_alerts'])
    except Exception as e:
        log.exception(e)

    try:
        wait_and_click(browser, css_selectors['account'], 5)
        elem_username = wait_and_get(browser, css_selectors['username'])
        if type(elem_username) is WebElement and elem_username.get_attribute('textContent') != '' and elem_username.get_attribute('textContent') == uid:
            TV_UID = uid
            TV_PWD = pwd
            log.info("logged in successfully at tradingview.com as {}".format(elem_username.get_attribute('textContent')))
        else:
            if elem_username.get_attribute('textContent') == '' or elem_username.get_attribute('textContent') == 'Guest':
                log.warning("not logged in at tradingview.com")
            elif elem_username.get_attribute('textContent') != uid:
                log.warning("logged in under a different username at tradingview.com")
            error = find_element(browser, 'body > div.tv-dialog__modal-wrap > div > div > div > div.tv-dialog__error.tv-dialog__error--dark')
            if error:
                print(error.get_attribute('innerText'))
                login(browser, '', '', True)
    except Exception as e:
        log.error(e)
        snapshot(browser, True)


def assign_user_data_directory():
    lockfile = 'lockfile'
    if OS != 'windows':
        lockfile = 'SingletonSocket'

    user_data_directory = config.get('webdriver', 'user_data_directory').strip()
    user_data_base_dir, tail = os.path.split(user_data_directory)
    kairos_data_directory = os.path.join(user_data_base_dir, 'kairos')
    if kairos_data_directory == user_data_directory:
        log.critical("{} is reserved as a backup to create new user data directories from. Please, set a different user data directory under [webdriver] -> kairos_data_directory and restart Kairos.")
        exit(1)
    if not os.path.exists(kairos_data_directory):
        if os.path.isfile(os.path.join(user_data_directory, lockfile)) or os.path.islink(os.path.join(user_data_directory, lockfile)):
            log.critical("Your user data directory is locked. Please close your browser and restart Kairos.")
            exit(1)
        # create new user data directory for Kairos
        log.info("creating base user data directory 'kairos'. Please be patient while data is being copied ...")
        shutil.copytree(user_data_directory, kairos_data_directory)
        return kairos_data_directory, True
        # tools.chmod_r(kairos_data_directory, 0o777)

    # user_data_directory = kairos_data_directory
    if config.has_option('webdriver', 'share_user_data') and config.getboolean('webdriver', 'share_user_data'):
        log.debug("{} in use? {}".format(user_data_directory, os.path.exists(os.path.join(user_data_directory, lockfile))))
        user_data_directory_found = False
        browser = config.get('webdriver', 'webbrowser', fallback='chrome').lower()

        # find an unused kairos user data directory
        user_data_base_dir, tail = os.path.split(user_data_directory)
        try:
            with os.scandir(user_data_base_dir) as user_data_directories:
                # number_of_kairos_user_data_directories = 0
                for entry in user_data_directories:
                    if entry.name.startswith('kairos_'):
                        # number_of_kairos_user_data_directories += 1
                        path = os.path.join(user_data_base_dir, entry.name)
                        if not tools.path_in_use(path, log, browser) and not user_data_directory_found:
                            user_data_directory = path
                            user_data_directory_found = True
                            break

                # make a copy of the default user data directory if it is not found
                i = 0
                while not user_data_directory_found and i < 100:
                    path = os.path.join(user_data_base_dir, "kairos_{}".format(i))
                    if not os.path.exists(path):
                        user_data_directory_found = True
                        log.info("creating user data directory 'kairos_{}'. Please be patient while data is being copied ...".format(i))
                        shutil.copytree(kairos_data_directory, path)
                        if OS == 'linux':
                            tools.chmod_r(path, 0o777)
                        user_data_directory = path
                    i += 1
        except Exception as e:
            log.exception(e)

    user_data_base_dir, name = os.path.split(user_data_directory)
    log.info("{} assigned".format(name))
    return r"" + str(user_data_directory), False


def check_driver(driver):
    driver_version = ""
    browser_version = driver.capabilities['browserVersion']

    if driver.name in driver.capabilities:
        for key, value in driver.capabilities[driver.name].items():
            match = re.search(r"version", key, re.IGNORECASE)
            if match:
                match = re.search(r"([\d+.]+\d+) ", value)
                if match:
                    driver_version = match.group(1).rstrip()
                break
    else:
        log.warning("browser name '{}' not found in driver".format(driver.name))
    log.info("browser version: {}".format(browser_version))
    log.info("driver version: {}".format(driver_version))


def create_browser(run_in_background):
    global log
    capabilities = DesiredCapabilities.CHROME.copy()
    initial_setup = False

    options = webdriver.ChromeOptions()
    # options.add_argument("--incognito")
    if config.has_option('webdriver', 'web_browser_path'):
        web_browser_path = r"" + str(config.get('webdriver', 'web_browser_path'))
        options.binary_location = web_browser_path
    if config.has_option('webdriver', 'user_data_directory') and config.get('webdriver', 'user_data_directory').strip() != "":
        kairos_data_directory, initial_setup = assign_user_data_directory()
        match = re.search(r".*(\d+)", kairos_data_directory)
        if match:
            instance = match.group(1)
            fn = tools.debug.file_name
            match = re.search(r".*(\..*)", tools.debug.file_name)
            if match:
                fn = fn.replace(match.group(1), "_{}{}".format(instance, match.group(1)))
            tools.shutdown_logging()
            tools.debug.file_name = fn
            log = tools.create_log()

        options.add_argument('--user-data-dir=' + kairos_data_directory)
        match = re.search(r".*(\d+)", kairos_data_directory)
        if match:
            global WEBDRIVER_INSTANCE
            WEBDRIVER_INSTANCE = int(match.group(1))
    if config.has_option('webdriver', 'options'):
        config_options = config.get('webdriver', 'options').split(',')
        for option in config_options:
            log.info(option.strip())
            options.add_argument(option.strip())
    else:
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-notifications')
        options.add_argument('--noerrdialogs')
        options.add_argument('--disable-session-crashed-bubble')
        # options.add_argument('--disable-infobars')
        # options.add_argument('--disable-restore-session-state')
        options.add_argument('--window-size=' + RESOLUTION)
        # suppress the INFO:CONSOLE messages
        options.add_argument("--log-level=3")
        # fix gpu_process_transport)factory.cc(980) error on Windows when in 'headless' mode, see:
        # https://stackoverflow.com/questions/50143413/errorgpu-process-transport-factory-cc1007-lost-ui-shared-context-while-ini
        if OS == 'windows':
            options.add_argument('--disable-gpu')
        if OS == 'linux':
            options.add_argument('--no-sandbox')
            options.add_argument("--disable-dev-shm-usage")
        # run chrome in the background
        if run_in_background:
            options.add_argument('--headless')

    if download_path:
        prefs = {
            "profile.default_content_setting_values.notifications": 2,
            "download.default_directory": download_path,
            "safebrowsing.enabled": "false"
        }
    else:
        prefs = {
            "profile.default_content_setting_values.notifications": 2,
            "safebrowsing.enabled": "false"
        }
    options.add_experimental_option('prefs', prefs)

    exclude_switches = [
        'enable-automation',
    ]
    options.add_experimental_option('excludeSwitches', exclude_switches)

    browser = None
    chromedriver_file = r"" + str(config.get('webdriver', 'path'))
    if not os.path.exists(chromedriver_file):
        log.error("File {} does not exist. Did setup your kairos.cfg correctly?".format(chromedriver_file))
        raise FileNotFoundError
    chromedriver_file.replace('.exe', '')

    if OS == 'linux' and \
            config.has_option('webdriver', 'use_proxy_display') and config.getboolean('webdriver', 'use_proxy_display'):
        from pyvirtualdisplay import Display
        display = Display(visible=False, size=(1920, 1024))
        display.start()

    # use open chrome browser
    # options = webdriver.ChromeOptions()
    # options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

    try:
        # noinspection PyUnboundLocalVariable
        log_path = r"--log-path=.\chromedriver_{}.log".format(int(WEBDRIVER_INSTANCE))

        # Create webdriver.remote
        # Note, we cannot serialize webdriver.Chrome
        if MULTI_THREADING:
            browser = webdriver.Remote(command_executor=EXECUTOR, options=options, desired_capabilities=capabilities)
        else:
            browser = webdriver.Chrome(
                executable_path=chromedriver_file,
                options=options,
                desired_capabilities=capabilities,
                service_args=["--verbose", log_path])

        check_driver(browser)

        browser.implicitly_wait(WAIT_TIME_IMPLICIT)
        browser.set_page_load_timeout(PAGE_LOAD_TIMEOUT)
        if initial_setup:
            log.info("creating shared session for kairos user data directory")
            login(browser)
            log.info("restarting kairos ... ")
            global ALREADY_LOGGED_IN
            ALREADY_LOGGED_IN = True
            destroy_browser(browser, False)
            return create_browser(run_in_background)
    except InvalidArgumentException as e:
        if e.msg.index("user data directory is already in use") >= 0:
            log.critical("your web browser's user data directory is in use. Please, close your web browser and restart Kairos.")
            exit(0)
        else:
            log.exception(e)
    except SessionNotCreatedException as e:
        index = 0
        if 'session not created: ' in e.msg:
            index = len('session not created: ')
        error = e.msg[index:]

        if "chrome" in error.lower():
            subject = "Outdated Chromedriver"
            text = "Could not run due to an outdated Chromedriver.\nPlease update your Chromedriver."
            log.error("Please update Chromedriver. {}".format(error))
        else:
            subject = "Outdated Geckodriver"
            text = "Could not run due to run due to an outdated Geckodriver.\nPlease update your Geckodriver."
            log.error("Please update Geckodriver. {}".format(error))

        # Send email
        import mail
        # TODO: make sure to send it only once per day
        mail.send_admin_message(subject, text)
        exit(0)
    except Exception as e:
        log.exception(e)
        exit(1)

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
        log.info("logged out of TradingView")
    except Exception as e:
        log.exception(e)
        snapshot(browser)


def destroy_browser(browser, close_log=True):
    try:
        if type(browser) is webdriver.Chrome:
            close_all_popups(browser)
            share_user_data = config.has_option('webdriver', 'share_user_data') and config.getboolean('webdriver', 'share_user_data')
            if not ALREADY_LOGGED_IN and not share_user_data:
                logout(browser)
            write_console_log(browser)
            if close_log:
                tools.shutdown_logging()
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
    log.info("Running on a {} operating system".format(OS))
    counter_alerts = 0
    total_alerts = 0
    browser = None

    global RUN_IN_BACKGROUND
    global MULTI_THREADING
    global WEBDRIVER_INSTANCE
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

                if not has_charts:
                    set_delays()
                    set_options()
                    log.info("WAIT_TIME_IMPLICIT = " + str(WAIT_TIME_IMPLICIT))
                    log.info("PAGE_LOAD_TIMEOUT = " + str(PAGE_LOAD_TIMEOUT))
                    log.info("CHECK_IF_EXISTS_TIMEOUT = " + str(CHECK_IF_EXISTS_TIMEOUT))
                    log.info("DELAY_BREAK_MINI = " + str(DELAY_BREAK_MINI))
                    log.info("DELAY_BREAK = " + str(DELAY_BREAK))
                    log.info("DELAY_SUBMIT_ALERT = " + str(DELAY_SUBMIT_ALERT))
                    log.info("DELAY_CHANGE_SYMBOL = " + str(DELAY_CHANGE_SYMBOL))
                    log.info("DELAY_CLEAR_INACTIVE_ALERTS = " + str(DELAY_CLEAR_INACTIVE_ALERTS))
                    log.info("DELAY_KEYSTROKE = " + str(DELAY_KEYSTROKE))
                    log.info("DELAY_READ_INDICATOR_VALUE = " + str(DELAY_READ_INDICATOR_VALUE))
                    log.info("READ_FROM_DATA_WINDOW = " + str(READ_FROM_DATA_WINDOW))
                    log.info("WAIT_UNTIL_CHART_IS_LOADED = " + str(WAIT_UNTIL_CHART_IS_LOADED))
                    log.info("READ_ALL_VALUES_AT_ONCE = " + str(READ_ALL_VALUES_AT_ONCE))
                    log.info("CHANGE_SYMBOL_WITH_SPACE = " + str(CHANGE_SYMBOL_WITH_SPACE))
                    log.info("VERIFY_MARKET_LISTING = " + str(VERIFY_MARKET_LISTING))
                    print('')
                try:
                    screeners_yaml = tv['screeners']
                    for screener_yaml in screeners_yaml:
                        if (not ('enabled' in screener_yaml)) or screener_yaml['enabled']:
                            log.info("create/update watchlist '{}' from screener. Please be patient, this may take several minutes ...".format(screener_yaml['name']))
                            max_runs = 3
                            counter = 0
                            markets = []
                            while counter < max_runs:
                                try:
                                    counter += 1
                                    markets = get_screener_markets(browser, screener_yaml)
                                except Exception as e:
                                    if counter == max_runs:
                                        log.exception(e)
                                    pass
                            if markets:
                                if update_watchlist(browser, screener_yaml['name'], markets):
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
                        clean_alerts(browser, css_selectors['item_clear_alerts'])
                    elif config.getboolean('tradingview', 'restart_inactive_alerts'):
                        clean_alerts(browser, css_selectors['item_restart_inactive_alerts'])
                    elif config.getboolean('tradingview', 'clear_inactive_alerts'):
                        clean_alerts(browser, css_selectors['item_clear_inactive_alerts'])

                    # close the alert menu
                    wait_and_click(browser, css_selectors['btn_alerts'])
                except Exception as e:
                    log.exception(e)

                # iterate over all items that have an 'alerts' or 'signals' property
                for file, items in tv.items():
                    if type(items) is list:
                        for item in items:
                            if 'alerts' in item or 'signals' in item or 'strategies' in item or 'backtest' in item or 'export_data' in item:
                                [counter_alerts, total_alerts] = open_chart(browser, item, save_as, counter_alerts, total_alerts)

                if len(processing_errors) > 0:
                    subject = 'Kairos error report'
                    text = 'Unfortunately, Kairos could not screen the following markets.\n\n' + ', '.join(processing_errors) + '\n\nPlease review your log for additional clues.\n'
                    # Send email
                    # noinspection PyUnresolvedReferences
                    from tv import mail
                    mail.send_admin_message(subject, text)

                log.info(summary(total_alerts, counter_alerts))
                print()
                if len(triggered_signals) > 0:
                    # noinspection PyUnresolvedReferences
                    from tv import mail
                    mail.post_process_signals(triggered_signals)
                    if export_signals_immediately:
                        if 'summary' in tv:
                            mail.send_mail(browser, tv['summary'], triggered_signals, False)
                            # we've send the signals, let's make sure they aren't send a 2nd time
                            triggered_signals.clear()
                        else:
                            log.warning('No summary configuration found in {}. Unable to create a summary and to export data.'.format(str(file)))
                elif export_signals_immediately:
                    log.info('No signals triggered. Nothing to send')
                destroy_browser(browser)
    except Exception as exc:
        log.exception(exc)
        summary(total_alerts, counter_alerts)
        destroy_browser(browser)
    return triggered_signals


def clean_alerts(browser, selector=css_selectors['item_clear_alerts']):
    # make sure we are opening the alert menu by closing/opening the calendar menu first
    try:
        wait_and_click(browser, css_selectors['btn_calendar'])
        wait_and_click(browser, css_selectors['btn_alerts'])
        wait_and_click(browser, css_selectors['btn_alert_menu'])
    except Exception as e:
        log.exception(e)

    # try to press the clean/reset all/inactive alerts &  confirm
    try:
        wait_and_click(browser, selector, 2)
        wait_and_click(browser, css_selectors['btn_dlg_clear_alerts_confirm'], 2)
        time.sleep(DELAY_BREAK * 2)
    except TimeoutException as e:
        log.debug(e)
    except Exception as e:
        log.exception(e)

    # close alert menu
    try:
        wait_and_click(browser, css_selectors['btn_alerts'])
    except Exception as e:
        log.exception(e)


def get_screener_markets(browser, screener_yaml):
    markets = []

    close_all_popups(browser)
    url = unquote(screener_yaml['url'])
    browser.get(url)
    time.sleep(DELAY_BREAK*2)
    loaded = False
    max_runs = 100
    counter = 0
    while not loaded and counter < max_runs:
        time.sleep(0.1)
        el_select = find_element(browser, css_selectors['select_screener'])
        hover(browser, el_select, True)
        loaded = element_exists(browser, css_selectors['options_screeners'])
        counter += 1

    el_options = find_elements(browser, css_selectors['options_screeners'])
    found = False
    for i in range(len(el_options)):
        option = el_options[i]
        try:
            log.debug(option.text)
            if str(option.text) == screener_yaml['name']:
                option.click()
                found = True
                break
        except StaleElementReferenceException:
            el_options = find_elements(browser, css_selectors['options_screeners'])
        i += 1

    if not found:
        log.warning("screener '{}' doesn't exist.".format(screener_yaml['name']))
        return False

    if 'search' in screener_yaml and screener_yaml['search'] != '':
        search_box = find_element(browser, css_selectors['input_screener_search'])
        set_value(browser, search_box, screener_yaml['search'], True)
        time.sleep(DELAY_SCREENER_SEARCH)

    el_total_found = find_element(browser, 'tv-screener-table__field-value--total', By.CLASS_NAME)
    total_found = 0
    try:
        match = re.search(r"(\d+)", el_total_found.text)
        total_found = int(match.group(1))
    except StaleElementReferenceException:
        pass
    log.debug("found {} markets for screener '{}'".format(total_found, screener_yaml['name']))

    while len(markets) < total_found:
        rows = find_elements(browser, class_selectors['rows_screener_result'], By.CLASS_NAME, True, False, 30)
        i = 0
        while i < len(rows):
            try:
                market = rows[i].get_attribute('data-symbol')
                action = ActionChains(browser)
                action.move_to_element_with_offset(rows[i], 5, 5)
                action.perform()
            except StaleElementReferenceException:
                WebDriverWait(browser, 5).until(
                    ec.presence_of_element_located((By.CLASS_NAME, class_selectors['rows_screener_result'])))
                # try again
                browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                rows = find_elements(browser, class_selectors['rows_screener_result'], By.CLASS_NAME)
                market = rows[i].get_attribute('data-symbol')
            markets.append(market)
            i += 1
        markets = list(sorted(set(markets)))

    log.debug('extracted {} markets'.format(str(len(markets))))
    return markets


def update_watchlist(browser, name, markets):
    try:
        if not find_element(browser, css_selectors['btn_watchlist_submenu'], except_on_timeout=False):
            wait_and_click(browser, css_selectors['btn_watchlist'])
            time.sleep(DELAY_BREAK)
        wait_and_click(browser, css_selectors['btn_watchlist_submenu'])
        time.sleep(DELAY_BREAK)

        # create new watchlist
        wait_and_click_by_text(browser, 'div', 'Create new list')

        # set watchlist name
        input_watchlist_name = find_element(browser, 'div[data-name="rename-dialog"] input')
        set_value(browser, input_watchlist_name, name, False, True)
        input_watchlist_name.send_keys(Keys.ENTER)
        time.sleep(DELAY_BREAK)

        # open 'Add symbol' dialogue
        wait_and_click(browser, 'div[data-name="add-symbol-button"]')
        # make sure we are searching all markets
        wait_and_click_by_xpath(browser, '//*[normalize-space(text()) = "All"]/parent::span')

        # add the markets to the watchlist
        for market in markets:
            # set value of search box with symbol
            # apparently setting exchange:symbol and hitting enter still works (for now)
            css = 'div[data-name="watchlist-symbol-search-dialog"] input[data-role="search"]'
            input_symbol = find_element(browser, css)
            set_value(browser, input_symbol, market)
            time.sleep(DELAY_BREAK)
            input_symbol.send_keys(Keys.ENTER)
            time.sleep(DELAY_BREAK_MINI)

            # when setting exchange:symbol and hitting enter no longer works, try the solution below
            """
            # find the right symbol and exchange
            exchange, symbol = market.split(':')
            css_row = 'div[data-role="list-item"][data-active="false"]'
            css_symbol = 'div[data-name="list-item-title"] > span'
            css_exchange = 'div[class^="exchangeName"]'
            css_add = 'span[class^="button"]'

            resolved = False
            errors = 0
            while not resolved:
                try:
                    rows = find_elements(browser, css_row)
                    for row in rows:
                        row_symbol = find_element(row, css_symbol).get_attribute('textContent').strip()
                        row_exchange = find_element(row, css_exchange).get_attribute('textContent').strip()
                        if row_symbol == symbol and row_exchange == exchange:
                            wait_and_click(row, css_add)
                except StaleElementReferenceException:
                    errors += 1
                    continue
                except Exception as e:
                    errors += 1
                    log.exception(e)
                resolved = True
                if errors > 10:
                    snapshot(browser, True)
            """

        # close the 'Add symbol' dialogue
        wait_and_click(browser, 'div[data-name="watchlist-symbol-search-dialog"] span[data-name="close"][data-role="button"]')

        # remove double watchlist
        remove_watchlists(browser, name)
        return True
    except Exception as e:
        log.exception(e)
        snapshot(browser)


def remove_watchlists(browser, name):
    # After a watchlist is imported, TV opens it. Since we cannot delete a watchlist while opened, we can safely assume that any watchlist of the same name that can be deleted is old and should be deleted
    wait_and_click(browser, css_selectors['btn_watchlist_submenu'])
    time.sleep(DELAY_BREAK)
    css_options = 'div[class^="watchlistMenu"] div[class^="item"]:not(div[class*="active"])'
    el_options = find_elements(browser, css_options)
    time.sleep(DELAY_BREAK)
    i = 0
    while i < len(el_options):
        try:
            element_name = None
            element = find_element(el_options[i], 'span[class^="title"]', except_on_timeout=False)
            if element:
                element_name = element.get_attribute('textContent').strip()
            if element_name == name:
                hover(browser, el_options[i])
                wait_and_click(el_options[i], 'span[data-name="remove-button"]')
                # handle confirmation dialog
                wait_and_click(browser, 'div[data-name="confirm-dialog"] button[name="yes"]')
                # give TV time to remove the watchlist
                time.sleep(DELAY_BREAK * 2)
                log.debug('watchlist {} removed'.format(name))
        except StaleElementReferenceException:
            # open the watchlists menu again and update the options to prevent 'element is stale' error
            wait_and_click(browser, css_selectors['btn_watchlist_submenu'])
            time.sleep(DELAY_BREAK)
            el_options = find_elements(browser, css_options)
            time.sleep(DELAY_BREAK)
            i = 0
        except Exception as e:
            log.exception(e)
            snapshot(browser)
        i = i + 1


def open_performance_summary_tab(browser):
    try:
        # open strategy tab
        strategy_tab = find_element(browser, css_selectors['tab_strategy_tester_inactive'], By.CSS_SELECTOR, False, False,
                                    1)
        if isinstance(strategy_tab, WebElement):
            strategy_tab.click()

        # open performance summary tab
        max_tries = max(config.getint('tradingview', 'create_alert_max_retries'), 10)
        tries = 0
        while tries < max_tries:
            # noinspection PyBroadException
            try:
                strategy_performance_strategy_tab = find_element(browser,
                                                                 css_selectors['tab_strategy_tester_performance_summary'],
                                                                 By.CSS_SELECTOR, True, False, 2)
                if isinstance(strategy_performance_strategy_tab, WebElement):
                    strategy_performance_strategy_tab.click()
                tries = max_tries
            except Exception as e:
                log.exception(e)
                tries += 1

    except Exception as e:
        log.exception(e)


def open_data_window_tab(browser):
    try:
        if not element_exists(browser, 'div.widgetbar-page.active > div.widgetbar-widget.widgetbar-widget-datawindow'):
            wait_and_click_by_xpath(browser, '//div[@data-name="data-window"]')
    except Exception as e:
        log.exception(e)
        snapshot(browser, True)


def get_strategy_default_values(browser, retry_number=0):
    try:
        # open dialog
        wait_and_click(browser, css_selectors['btn_strategy_dialog'])
        # click and set inputs
        wait_and_click(browser, css_selectors['indicator_dialog_tab_inputs'])
        inputs = get_indicator_dialog_values(browser)
        # click and set properties
        wait_and_click(browser, css_selectors['indicator_dialog_tab_properties'])
        properties = get_indicator_dialog_values(browser)
        # click OK
        wait_and_click(browser, css_selectors['btn_indicator_dialog_ok'])
    except Exception as e:
        return retry_get_strategy_default_values(browser, e, retry_number)
    return inputs, properties


def retry_get_strategy_default_values(browser, e, retry_number=0):
    max_tries = config.getint('tradingview', 'create_alert_max_retries')
    if retry_number < max_tries:
        return get_strategy_default_values(browser, retry_number+1)
    else:
        log.exception(e)
        return {}, {}


def get_indicator_dialog_values(browser):
    # get input titles
    result = dict()
    try:
        cells = find_elements(browser, css_selectors['indicator_dialog_tab_cells'])
        for i, cell in enumerate(cells):
            css_class = cell.get_attribute("class")
            if str(css_class).find('last') > 0:
                title = re.sub(r"[\W]", '', cells[i-1].text.replace(' ', '_')).lower()
                value = cell.text

                css = css_selectors['indicator_dialog_tab_cell'].format(i + 1) + ' input'
                css_labels = css_selectors['indicator_dialog_tab_cell'].format(i + 1) + ' label > span > span'
                inputs = find_elements(browser, css, By.CSS_SELECTOR, False, False, 1)
                labels = find_elements(browser, css_labels, By.CSS_SELECTOR, False, False, 1)
                # one or more checkboxes
                if labels and inputs:
                    for j, label in enumerate(labels):
                        value = ""
                        title += "_" + re.sub(r"[\W]", '', label.text.replace(' ', '_')).lower()
                        if inputs[j].get_attribute('type') == "checkbox":
                            if is_checkbox_checked(inputs[j]):
                                value = 'yes'
                            else:
                                value = 'no'
                        result[title] = value
                    continue
                elif inputs:
                    value = ""
                    for input_element in inputs:
                        value += input_element.get_attribute("value") + " "
                    if value:
                        value += cell.text

                if value:
                    result[title] = value.strip()
            elif str(css_class).find('fill') > 0:
                # all elements that have class '...fill...' are checkboxes
                title = re.sub(r"[\W]", '', cell.text.replace(' ', '_')).lower()
                css = css_selectors['indicator_dialog_tab_cell'].format(i + 1) + ' input'
                input_element = find_element(browser, css, By.CSS_SELECTOR, False, False, 1)
                if input_element:
                    if input_element.get_attribute('type') == "checkbox":
                        if is_checkbox_checked(input_element):
                            value = 'yes'
                        else:
                            value = 'no'
                    else:
                        value = input_element.get_attribute("value")
                else:
                    value = cell.text
                if value:
                    result[title] = value.strip()
            else:
                continue
    except StaleElementReferenceException:
        pass
    except Exception as e:
        log.exception(e)
    return result


def test_indicators(browser, indicator, symbols, data, atomic_inputs):
    try:
        summaries = list()
        name = indicator['full_name']
        number_of_charts = 1
        try:
            css = 'div.chart-container'
            number_of_charts = find_elements(browser, css)
            number_of_charts = len(number_of_charts)
        except TimeoutException:
            pass
        log.info("Found {} charts on the layout".format(number_of_charts))

        # inputs have been defined
        if len(atomic_inputs) > 0:
            log.info("Back testing {} with {} input sets".format(name, len(atomic_inputs)))
            for i, inputs in enumerate(atomic_inputs):
                log.info("testing variant {}/{} with the following inputs: {}".format(i+1, len(atomic_inputs), inputs))
                strategy_summary = dict()
                strategy_summary['inputs'] = inputs
                strategy_summary['summary'] = dict()
                strategy_summary['summary']['total'], strategy_summary['summary']['interval'], strategy_summary['summary']['symbol'], strategy_summary['raw'] = \
                    test_indicator(browser, inputs, symbols, indicator, data, number_of_charts, i + 1, len(atomic_inputs))
                summaries.append(strategy_summary)
        # Run just one back test with default inputs
        else:
            log.info("Back testing {} with the default input set".format(name))
            strategy_summary = dict()
            strategy_summary['inputs'] = []
            strategy_summary['summary'] = dict()
            strategy_summary['summary']['total'], strategy_summary['summary']['interval'], strategy_summary['summary']['symbol'], strategy_summary['raw'] = \
                test_indicator(browser, [], symbols, indicator, data, number_of_charts, 1, 1)
            summaries.append(strategy_summary)

        return summaries

    except ValueError as e:
        log.exception(e)


def test_indicator(browser, inputs, symbols, indicator, data, number_of_charts, strategy_number, number_of_variants):
    global tv_start

    raw = []
    input_locations = dict()
    interval_totals = dict()
    symbol_totals = dict()
    intervals = []
    duration = 0

    values = dict()
    previous_elements = dict()
    for key in data:
        values[key] = ""
        previous_elements[key] = ""

    for i, symbol in enumerate(symbols[0:2]):
        timer_symbol = time.time()
        test_indicator_symbol(browser, inputs, symbol, indicator, data, number_of_charts, i == 0, raw, input_locations, interval_totals, symbol_totals, intervals, values, previous_elements)
        if i == 0:
            duration += (time.time() - timer_symbol) * (number_of_variants + 1 - strategy_number)
        else:
            duration += (time.time() - timer_symbol) * (len(symbols)-2) * (number_of_variants + 1 - strategy_number)
    log.info("expecting to finish in {}.".format(tools.display_time(duration)))
    for symbol in symbols[2::]:
        first_symbol = refresh_session(browser)
        test_indicator_symbol(browser, inputs, symbol, indicator, data, number_of_charts, first_symbol, raw, input_locations, interval_totals, symbol_totals, intervals, values, previous_elements)

    # Aggregate all the data to get totals
    totals = dict()
    for key in data:
        totals[key] = 0
        for interval in interval_totals:
            totals[key] = float(totals[key]) + float(interval_totals[interval][key])

    # Calculate data points and do the rounding of all aggregated data
    for interval in interval_totals:
        interval_totals[interval] = calculate_indicator_data_points(data, interval_totals[interval], interval)
        del interval_totals[interval]['counter']
        post_process_data_points(data, interval_totals[interval])
    for symbol_average in symbol_totals:
        symbol_totals[symbol_average] = calculate_indicator_data_points(data, symbol_totals[symbol_average])
        del symbol_totals[symbol_average]['counter']
        post_process_data_points(data, symbol_totals[symbol_average])
    totals = calculate_indicator_data_points(data, totals)
    post_process_data_points(data, totals)
    for dataset in raw:
        # data points have already been calculated for the raw data (i.e. per symbol, per timeframe)
        post_process_data_points(data, dataset)

    return [totals, interval_totals, symbol_totals, raw]


def test_indicator_symbol(browser, inputs, symbol, indicator, data, number_of_charts, first_symbol: bool, results, input_locations, interval_totals, symbol_totals, intervals, values, previous_elements, tries=0):
    max_tries = 5
    try:
        max_tries = config.getint('tradingview', 'create_alert_max_retries')

        change_symbol(browser, symbol, CHANGE_SYMBOL_WITH_SPACE)
        log.info(symbol)
        previous_values = copy.deepcopy(values)
        values = dict()
        symbol_total = dict()
        symbol_total['counter'] = 0
        for key in data:
            symbol_total[key] = 0

        for chart_index in range(number_of_charts):
            # move to correct chart
            charts = find_elements(browser, "div.chart-container")
            charts[chart_index].click()

            # first time chart setup
            # - set inputs
            # - get interval of chart
            # - create a dict() for each interval and add it to averages
            if first_symbol:
                log.debug("selecting and formatting strategy for chart {}".format(chart_index + 1))
                # set the strategy if there are inputs or properties defined
                if len(inputs) > 0:
                    # open the indicator's settings dialog of the active chart
                    open_indicator_settings(browser, indicator['name'], chart_index)
                    # set input values and click OK
                    set_indicator_dialog_values(browser, inputs, input_locations)
                    wait_and_click(browser, css_selectors['btn_indicator_dialog_ok'])

                elem_interval = find_element(browser, css_selectors['active_chart_interval'])
                interval = repr(elem_interval.get_attribute('innerHTML')).replace(', ', '')
                intervals.append(interval)

                if not (interval in interval_totals):
                    interval_totals[interval] = dict()
                    interval_totals[interval]['counter'] = 0
                    for key in data:
                        interval_totals[interval][key] = 0
            interval = intervals[chart_index]
            # snapshot(browser, False, True, "results\\{}_{}".format(symbol.replace(':', '_'), interval), True)

            # Extract data points from TV first
            valid_data = True
            for key in data:
                options = data[key]
                values[key] = ''
                if not ('sum' in options):
                    value = get_data_window_indicator_value_by_text(browser, indicator, key)
                    if value == previous_values[key] and chart_index == 0:
                        log.warn("'{} = {}' which is the same value as for the previous chart. Verifying value...".format(key, value))
                        time.sleep(DELAY_BREAK*2)
                        value = get_data_window_indicator_value_by_text(browser, indicator, key)
                    if value == 'n/a':
                        valid_data = False
                        value = 0
                    values[key] = format_number(value, options['decimals'])

            if not valid_data:
                log.info("{}: no values found. Indicator didn't trigger once.".format(interval))
                # snapshot(browser, False, True, "{}_{}".format(symbol.replace(':', '_'), interval), True)

            # Calculate additional data points from the extracted data
            values = calculate_indicator_data_points(data, values, interval)

            # Optional defined condition of when data should be added
            expression = '1'
            if 'condition' in indicator:
                expression = indicator['condition']
            for key in values:
                if not values[key]:
                    values[key] = 0
                expression = expression.replace(key, str(values[key]))
            condition_met = eval(expression)

            # Aggregate all the results if the condition is met
            if condition_met:
                interval_totals[interval]['counter'] += 1
                result = dict()
                result['symbol'] = symbol
                result['interval'] = interval.replace("'", "")
                for key in data:
                    result[key] = float(values[key])
                    symbol_total[key] = float(symbol_total[key]) + float(result[key])
                    interval_totals[interval][key] = float(interval_totals[interval][key]) + float(result[key])
                symbol_total['counter'] += 1
                results.append(result)

        symbol_totals[symbol] = symbol_total

    except Exception as e:
        log.exception(e)
        if tries < max_tries:
            test_indicator_symbol(browser, inputs, symbol, indicator, data, number_of_charts, first_symbol, results, input_locations, interval_totals, symbol_totals, intervals, values, previous_elements, tries)


def calculate_indicator_data_points(data, values, interval=False):
    calculated = False
    i = 0
    while not calculated and i < 5:
        i = i + 1
        calculated = True
        for key in data:
            options = data[key]
            if 'sum' in options:
                value = calculate_indicator_data_point(key, options['sum'], values, interval)
                if isinstance(value, int) or isinstance(value, float):
                    values[key] = value
                else:
                    calculated = False
    return values


def calculate_indicator_data_point(data_point, expression, values, interval=False):
    result = ''
    try:
        if interval:
            expression = expression.replace('%TIMEFRAME%', str(interval).replace("'", ""))
        for key in values:
            if key != data_point and values[key]:
                expression = expression.replace(key, str(values[key]))
        try:
            result = eval(expression)
        except NameError:
            result = ''
        except ZeroDivisionError:
            result = 0.0
    except Exception as e:
        log.exception(e)
    return result


def post_process_data_points(data, values):
    for key in data:
        options = data[key]
        show = options['show']
        decimals = options['decimals']
        if show:
            values[key] = format_number(values[key], decimals)
        else:
            del values[key]


def back_test(browser, strategy_config, symbols, atomic_inputs, atomic_properties):
    try:

        summaries = list()
        name = strategy_config['name']

        try:
            css = 'div.chart-container'
            number_of_charts = find_elements(browser, css)
            number_of_charts = len(number_of_charts)
        except TimeoutException:
            number_of_charts = 1
        log.info("Found {} charts on the layout".format(number_of_charts))

        number_of_strategies = max(len(atomic_properties), 1) * max(len(atomic_inputs), 1)
        # Both inputs and properties have been defined
        if len(atomic_properties) > 0 and len(atomic_inputs) > 0:
            log.info("Back testing {} with {} input sets and {} property sets.".format(name, len(atomic_inputs), len(atomic_properties)))
            for i, properties in enumerate(atomic_properties):
                for j, inputs in enumerate(atomic_inputs):
                    strategy_number = i*len(properties)+j+1
                    log.info("Strategy variant {}/{}".format(strategy_number, number_of_strategies))
                    strategy_summary = dict()
                    strategy_summary['inputs'] = inputs
                    strategy_summary['properties'] = properties
                    strategy_summary['summary'] = dict()
                    # strategy_summary['summary']['total'], strategy_summary['summary']['interval'], strategy_summary['summary']['symbol'], strategy_summary['raw']
                    strategy_summary['summary']['total'], strategy_summary['summary']['interval'], strategy_summary['summary']['symbol'], strategy_summary['raw'] = back_test_strategy(browser, inputs, properties, symbols, strategy_config, number_of_charts, strategy_number, number_of_strategies)
                    summaries.append(strategy_summary)

        # Inputs have been defined. Run back test for each input with default properties
        elif len(atomic_inputs) > 0:
            log.info("Back testing {} with {} input sets and default property set.".format(name, len(atomic_inputs)))
            for i, inputs in enumerate(atomic_inputs):
                log.info("Strategy variant {}/{}".format(i+1, number_of_strategies))
                strategy_summary = dict()
                strategy_summary['inputs'] = inputs
                strategy_summary['properties'] = []
                strategy_summary['summary'] = dict()
                strategy_summary['summary']['total'], strategy_summary['summary']['interval'], strategy_summary['summary']['symbol'], strategy_summary['raw'] = back_test_strategy(browser, inputs, [], symbols, strategy_config, number_of_charts, i, number_of_strategies)
                summaries.append(strategy_summary)
        # Properties have been defined. Run back test for property with default inputs
        elif len(atomic_properties) > 0:
            log.info("Back testing {} with default input set and {} properties sets.".format(name, len(atomic_properties)))
            for i, properties in enumerate(atomic_properties):
                log.info("Strategy variant {}/{}".format(i+1, number_of_strategies))
                strategy_summary = dict()
                strategy_summary['inputs'] = []
                strategy_summary['properties'] = properties
                strategy_summary['summary'] = dict()
                strategy_summary['summary']['total'], strategy_summary['summary']['interval'], strategy_summary['summary']['symbol'], strategy_summary['raw'] = back_test_strategy(browser, [], properties, symbols, strategy_config, number_of_charts, i, number_of_strategies)
                summaries.append(strategy_summary)
        # Run just one back test with default inputs and properties
        else:
            log.info("Back testing {} with default input set and default property set.".format(name))
            strategy_summary = dict()
            strategy_summary['inputs'] = []
            strategy_summary['properties'] = []
            strategy_summary['summary'] = dict()
            strategy_summary['summary']['total'], strategy_summary['summary']['interval'], strategy_summary['summary']['symbol'], strategy_summary['raw'] = back_test_strategy(browser, [], [], symbols, strategy_config, number_of_charts, 1, 1)
            summaries.append(strategy_summary)

        # close strategy tab
        strategy_tab = find_element(browser, css_selectors['tab_strategy_tester_inactive'], By.CSS_SELECTOR, False, False, 1)
        if isinstance(strategy_tab, WebElement):
            strategy_tab.click()

        return summaries

    except ValueError as e:
        log.exception(e)


def back_test_strategy(browser, inputs, properties, symbols, strategy_config, number_of_charts, strategy_number, number_of_variants):
    global tv_start

    raw = []
    input_locations = dict()
    property_locations = dict()
    interval_averages = dict()
    symbol_averages = dict()
    intervals = []

    duration = 0
    values = dict(
        performance_summary_profit_factor="",
        performance_summary_total_closed_trades="",
        performance_summary_net_profit="",
        performance_summary_net_profit_percentage="",
        performance_summary_percent_profitable="",
        performance_summary_max_drawdown="",
        performance_summary_max_drawdown_percentage="",
        performance_summary_avg_trade="",
        performance_summary_avg_trade_percentage="",
        performance_summary_avg_bars_in_trade="",
    )

    previous_elements = dict(
        performance_summary_profit_factor="",
        performance_summary_total_closed_trades="",
        performance_summary_net_profit="",
        performance_summary_net_profit_percentage="",
        performance_summary_percent_profitable="",
        performance_summary_max_drawdown="",
        performance_summary_max_drawdown_percentage="",
        performance_summary_avg_trade="",
        performance_summary_avg_trade_percentage="",
        performance_summary_avg_bars_in_trade="",
    )

    for i, symbol in enumerate(symbols[0:2]):
        timer_symbol = time.time()
        back_test_strategy_symbol(browser, inputs, properties, symbol, strategy_config, number_of_charts, i == 0, raw, input_locations, property_locations, interval_averages, symbol_averages, intervals, values, previous_elements)
        if i == 0:
            duration += (time.time() - timer_symbol) * (number_of_variants + 1 - strategy_number)
        else:
            duration += (time.time() - timer_symbol) * (len(symbols)-2) * (number_of_variants + 1 - strategy_number)
    log.info("expecting to finish in {}.".format(tools.display_time(duration)))
    for symbol in symbols[2::]:
        first_symbol = refresh_session(browser)
        back_test_strategy_symbol(browser, inputs, properties, symbol, strategy_config, number_of_charts, first_symbol, raw, input_locations, property_locations, interval_averages, symbol_averages, intervals, values, previous_elements)

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

    for interval in interval_averages:
        counter = max(interval_averages[interval]['Counter'], 1)
        interval_averages[interval]['Net Profit'] = format_number(float(interval_averages[interval]['Net Profit']) / counter)
        interval_averages[interval]['Net Profit %'] = format_number(float(interval_averages[interval]['Net Profit %']) / counter)
        interval_averages[interval]['Closed Trades'] = format_number(float(interval_averages[interval]['Closed Trades']) / counter)
        interval_averages[interval]['Percent Profitable'] = format_number(float(interval_averages[interval]['Percent Profitable']) / counter)
        interval_averages[interval]['Profit Factor'] = format_number(float(interval_averages[interval]['Profit Factor']) / counter)
        interval_averages[interval]['Max Drawdown'] = format_number(float(interval_averages[interval]['Max Drawdown']) / counter)
        interval_averages[interval]['Max Drawdown %'] = format_number(float(interval_averages[interval]['Max Drawdown %']) / counter)
        interval_averages[interval]['Avg Trade'] = format_number(float(interval_averages[interval]['Avg Trade']) / counter)
        interval_averages[interval]['Avg Trade %'] = format_number(float(interval_averages[interval]['Avg Trade %']) / counter)
        interval_averages[interval]['Avg # Bars In Trade'] = format_number(float(interval_averages[interval]['Avg # Bars In Trade']) / counter)
        del interval_averages[interval]['Counter']

        # log.info("{}: {}".format(interval, averages[interval]))

        total_average['Net Profit'] = format_number(float(total_average['Net Profit']) + float(interval_averages[interval]['Net Profit']))
        total_average['Net Profit %'] = format_number(float(total_average['Net Profit %']) + float(interval_averages[interval]['Net Profit %']))
        total_average['Closed Trades'] = format_number(float(total_average['Closed Trades']) + float(interval_averages[interval]['Closed Trades']))
        total_average['Percent Profitable'] = format_number(float(total_average['Percent Profitable']) + float(interval_averages[interval]['Percent Profitable']))
        total_average['Profit Factor'] = format_number(float(total_average['Profit Factor']) + float(interval_averages[interval]['Profit Factor']))
        total_average['Max Drawdown'] = format_number(float(total_average['Max Drawdown']) + float(interval_averages[interval]['Max Drawdown']))
        total_average['Max Drawdown %'] = format_number(float(total_average['Max Drawdown %']) + float(interval_averages[interval]['Max Drawdown %']))
        total_average['Avg Trade'] = format_number(float(total_average['Avg Trade']) + float(interval_averages[interval]['Avg Trade']))
        total_average['Avg Trade %'] = format_number(float(total_average['Avg Trade %']) + float(interval_averages[interval]['Avg Trade %']))
        total_average['Avg # Bars In Trade'] = format_number(float(total_average['Avg # Bars In Trade']) + float(interval_averages[interval]['Avg # Bars In Trade']))

    total_average['Net Profit'] = format_number(float(total_average['Net Profit']) / max(len(interval_averages), 1))
    total_average['Net Profit %'] = format_number(float(total_average['Net Profit %']) / max(len(interval_averages), 1))
    total_average['Closed Trades'] = format_number(float(total_average['Closed Trades']) / max(len(interval_averages), 1))
    total_average['Percent Profitable'] = format_number(float(total_average['Percent Profitable']) / max(len(interval_averages), 1))
    total_average['Profit Factor'] = format_number(float(total_average['Profit Factor']) / max(len(interval_averages), 1))
    total_average['Max Drawdown'] = format_number(float(total_average['Max Drawdown']) / max(len(interval_averages), 1))
    total_average['Max Drawdown %'] = format_number(float(total_average['Max Drawdown %']) / max(len(interval_averages), 1))
    total_average['Avg Trade'] = format_number(float(total_average['Avg Trade']) / max(len(interval_averages), 1))
    total_average['Avg Trade %'] = format_number(float(total_average['Avg Trade %']) / max(len(interval_averages), 1))
    total_average['Avg # Bars In Trade'] = format_number(float(total_average['Avg # Bars In Trade']) / max(len(interval_averages), 1))

    return [total_average, interval_averages, symbol_averages, raw]


def back_test_sort_watchlist(test_runs, sort_by, reverse=True):

    for i, test_run in enumerate(test_runs):
        raw = test_run["raw"]
        interval_averages = test_run["summary"]["interval"]
        symbol_averages = test_run["summary"]["symbol"]
        if sort_by:
            interval_averages_keys = sorted(interval_averages, key=lambda x: interval_averages[x][sort_by], reverse=reverse)
            symbol_averages_keys = sorted(symbol_averages, key=lambda x: symbol_averages[x][sort_by], reverse=reverse)
            raw = sorted(raw, key=lambda x: x[sort_by], reverse=reverse)
        else:
            # fall back to default sorting
            interval_averages_keys = sorted(interval_averages)
            symbol_averages_keys = sorted(symbol_averages)

        interval_averages_sorted = dict()
        for key in interval_averages_keys:
            interval_averages_sorted[key] = interval_averages[key]
        symbol_averages_sorted = dict()
        for key in symbol_averages_keys:
            symbol_averages_sorted[key] = symbol_averages[key]

        test_run["summary"]["interval"] = interval_averages_sorted
        test_run["summary"]["symbol"] = symbol_averages_sorted
        test_run["raw"] = raw

    if sort_by:
        result = sorted(test_runs, key=lambda x: x["summary"]["total"][sort_by], reverse=reverse)
    else:
        result = test_runs
    return result


def back_test_sort(json_data, sort_by, reverse=True):
    # log.info("{} {}".format(sort_by, reverse))
    try:
        for strategy in json_data:
            # log.info("{}: {}".format(strategy, type(json_data[strategy])))
            if isinstance(json_data[strategy], dict):
                for watchlist in json_data[strategy]:
                    if (watchlist not in ["id", "default_inputs", "default_properties"]) and isinstance(json_data[strategy][watchlist], list):
                        json_data[strategy][watchlist] = back_test_sort_watchlist(json_data[strategy][watchlist], sort_by, reverse)
        return json_data
    except Exception as e:
        log.exception(e)


def back_test_strategy_symbol(browser, inputs, properties, symbol, strategy_config, number_of_charts, first_symbol, results, input_locations, property_locations, interval_averages, symbol_averages, intervals, values, previous_elements, tries=0):
    try:
        log.info(symbol)
        if first_symbol:
            open_performance_summary_tab(browser)

        change_symbol(browser, symbol)

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
            # move to correct chart
            # charts = find_elements(browser, "div.chart-container")
            charts = find_elements(browser, css_selectors["chart_container"])
            next_chart_clicked = False
            while not next_chart_clicked:
                try:
                    charts[chart_index].click()
                    next_chart_clicked = True
                except ElementClickInterceptedException:
                    time.sleep(DELAY_BREAK)
                except StaleElementReferenceException:
                    charts = find_elements(browser, css_selectors["chart_container"])
                except Exception as e:
                    log.exception(e)

            # first time chart setup
            # - set inputs and properties of charts
            # - get interval of chart
            # - create a dict() for each interval and add it to averages
            if first_symbol:
                # log.debug("selecting and formatting strategy for chart {}".format(chart_index + 1))
                # set the strategy if there are inputs or properties defined
                if len(inputs) > 0 or len(properties) > 0:
                    # Select correct strategy on the chart, wait for it to be loaded and get current inputs and properties
                    select_strategy(browser, strategy_config, chart_index)
                    # open the strategy dialog and set the input & property values
                    format_strategy(browser, inputs, properties, input_locations, property_locations)
                elem_interval = find_element(browser, css_selectors['active_chart_interval'])
                interval = repr(elem_interval.get_attribute('innerHTML')).replace(', ', '')
                log.info(interval)
                intervals.append(interval)

                if not (interval in interval_averages):
                    interval_averages[interval] = dict()
                    interval_averages[interval]['Net Profit'] = 0
                    interval_averages[interval]['Net Profit %'] = 0
                    interval_averages[interval]['Closed Trades'] = 0
                    interval_averages[interval]['Percent Profitable'] = 0
                    interval_averages[interval]['Profit Factor'] = 0
                    interval_averages[interval]['Max Drawdown'] = 0
                    interval_averages[interval]['Max Drawdown %'] = 0
                    interval_averages[interval]['Avg Trade'] = 0
                    interval_averages[interval]['Avg Trade %'] = 0
                    interval_averages[interval]['Avg # Bars In Trade'] = 0
                    interval_averages[interval]['Counter'] = 0

            wait_until_indicator_is_loaded(browser, strategy_config['name'], strategy_config['pane_index'])
            interval = intervals[chart_index]

            # take_screenshot(browser, symbol, interval, False, '%Y%m%d_%H%M%S')
            # log.info("previous_element is {}".format(type(previous_element)))

            # Extract results
            over_the_threshold = True
            for i, key in enumerate(values):
                value = get_strategy_statistic(browser, key, previous_elements)
                if isinstance(value, Exception):
                    raise value

                # check if the total closed trades is over the threshold
                if key == 'performance_summary_total_closed_trades' and config.has_option('backtesting', 'threshold') and config.getint('backtesting', 'threshold') > value:
                    log.info("{}: {} data has been excluded due to the number of closed trades ({}) not reaching the threshold ({})".format(symbol, interval, value, config.getint('backtesting', 'threshold')))
                    over_the_threshold = False
                    values[key] = value
                    break
                # Update previous values with the current ones
                values[key] = value

            # previous_element[0] = find_element(browser, css_selectors['performance_summary_profit_factor'])
            # log.info("previous_element = {}".format(repr(previous_element[0])))
            if not over_the_threshold:
                continue
            ############################################################
            # DO NOT ADD INTERACTIONS WITH SELENIUM BELOW THIS COMMENT #
            # Exceptions may give incomplete results. Make sure that   #
            # all Selenium interaction is done above this comment.     #
            ############################################################

            # Save the results
            result = dict()
            result['Symbol'] = symbol
            result['Interval'] = interval.replace("'", "")
            result['Net Profit'] = format_number(float(values['performance_summary_net_profit']), 8)
            result['Net Profit %'] = format_number(float(values['performance_summary_net_profit_percentage']), 8)
            result['Closed Trades'] = format_number(float(values['performance_summary_total_closed_trades']), 8)
            result['Percent Profitable'] = format_number(float(values['performance_summary_percent_profitable']), 8)
            result['Profit Factor'] = format_number(float(values['performance_summary_profit_factor']), 8)
            result['Max Drawdown'] = format_number(float(values['performance_summary_max_drawdown']), 8)
            result['Max Drawdown %'] = format_number(float(values['performance_summary_max_drawdown_percentage']), 8)
            result['Avg Trade'] = format_number(float(values['performance_summary_avg_trade']), 8)
            result['Avg Trade %'] = format_number(float(values['performance_summary_avg_trade_percentage']), 8)
            result['Avg # Bars In Trade'] = format_number(float(values['performance_summary_avg_bars_in_trade']), 8)
            results.append(result)

            # add to averages
            if isinstance(result['Avg # Bars In Trade'], int):
                symbol_average['Net Profit'] = format_number(float(symbol_average['Net Profit']) + float(result['Net Profit']))
                symbol_average['Net Profit %'] = format_number(float(symbol_average['Net Profit %']) + float(result['Net Profit %']))
                symbol_average['Closed Trades'] += int(result['Closed Trades'])
                symbol_average['Percent Profitable'] = format_number(float(symbol_average['Percent Profitable']) + float(result['Percent Profitable']))
                symbol_average['Profit Factor'] = format_number(float(symbol_average['Profit Factor']) + float(result['Profit Factor']))
                symbol_average['Max Drawdown'] = format_number(float(symbol_average['Max Drawdown']) + float(result['Max Drawdown']))
                symbol_average['Max Drawdown %'] = format_number(float(symbol_average['Max Drawdown %']) + float(result['Max Drawdown %']))
                symbol_average['Avg Trade'] = format_number(float(symbol_average['Avg Trade']) + float(result['Avg Trade']))
                symbol_average['Avg Trade %'] = format_number(float(symbol_average['Avg Trade %']) + float(result['Avg Trade %']))
                symbol_average['Avg # Bars In Trade'] += int(result['Avg # Bars In Trade'])
                symbol_average['Counter'] += 1

                interval_averages[interval]['Net Profit'] = format_number(float(interval_averages[interval]['Net Profit']) + float(result['Net Profit']))
                interval_averages[interval]['Net Profit %'] = format_number(float(interval_averages[interval]['Net Profit %']) + float(result['Net Profit %']))
                interval_averages[interval]['Closed Trades'] += int(result['Closed Trades'])
                interval_averages[interval]['Percent Profitable'] = format_number(float(interval_averages[interval]['Percent Profitable']) + float(result['Percent Profitable']))
                interval_averages[interval]['Profit Factor'] = format_number(float(interval_averages[interval]['Profit Factor']) + float(result['Profit Factor']))
                interval_averages[interval]['Max Drawdown'] = format_number(float(interval_averages[interval]['Max Drawdown']) + float(result['Max Drawdown']))
                interval_averages[interval]['Max Drawdown %'] = format_number(float(interval_averages[interval]['Max Drawdown %']) + float(result['Max Drawdown %']))
                interval_averages[interval]['Avg Trade'] = format_number(float(interval_averages[interval]['Avg Trade']) + float(result['Avg Trade']))
                interval_averages[interval]['Avg Trade %'] = format_number(float(interval_averages[interval]['Avg Trade %']) + float(result['Avg Trade %']))
                interval_averages[interval]['Avg # Bars In Trade'] += int(result['Avg # Bars In Trade'])
                interval_averages[interval]['Counter'] += 1

        # calculate symbol averages
        counter = max(symbol_average['Counter'], 1)
        symbol_average['Net Profit'] = format_number(float(symbol_average['Net Profit']) / counter)
        symbol_average['Net Profit %'] = format_number(float(symbol_average['Net Profit %']) / counter)
        symbol_average['Closed Trades'] = format_number(float(symbol_average['Closed Trades']) / counter)
        symbol_average['Percent Profitable'] = format_number(float(symbol_average['Percent Profitable']) / counter)
        symbol_average['Profit Factor'] = format_number(float(symbol_average['Profit Factor']) / counter)
        symbol_average['Max Drawdown'] = format_number(float(symbol_average['Max Drawdown']) / counter)
        symbol_average['Max Drawdown %'] = format_number(float(symbol_average['Max Drawdown %']) / counter)
        symbol_average['Avg Trade'] = format_number(float(symbol_average['Avg Trade']) / counter)
        symbol_average['Avg Trade %'] = format_number(float(symbol_average['Avg Trade %']) / counter)
        symbol_average['Avg # Bars In Trade'] = format_number(float(symbol_average['Avg # Bars In Trade']) / counter)
        del symbol_average['Counter']
        # log.info("{}: {}".format(symbol, symbol_average))
        symbol_averages[symbol] = symbol_average

    except Exception as e:
        retry_back_test_strategy_symbol(browser, inputs, properties, symbol, strategy_config, number_of_charts, first_symbol, results, input_locations, property_locations, interval_averages, symbol_averages, intervals, values, previous_elements, tries, e)


def retry_back_test_strategy_symbol(browser, inputs, properties, symbol, strategy_config, number_of_charts, first_symbol, results, input_locations, property_locations, interval_averages, symbol_averages, intervals, values, previous_elements, tries, e):
    max_tries = config.getint('tradingview', 'create_alert_max_retries')
    if tries < max_tries:
        # log.debug("try {}".format(tries))
        if isinstance(e, InvalidSessionIdException) or isinstance(e, WebDriverException):
            log.exception(e)
            if str(e.msg).lower().find('session') >= 0:
                log.critical("invalid session id - RESTARTING")
                url = browser.current_url
                browser.quit()
                browser = create_browser(RUN_IN_BACKGROUND)
                browser.get(url)
                # Switching to Alert
                close_alerts(browser)
                # Close the watchlist menu if it is open
                if find_element(browser, css_selectors['btn_watchlist_submenu'], By.CSS_SELECTOR, False, False, 0.5):
                    wait_and_click(browser, css_selectors['btn_watchlist_menu'])
                first_symbol = True
            else:
                log.exception(e)
                refresh(browser)
        first_symbol = refresh_session(browser) or first_symbol
        if not isinstance(e, StaleElementReferenceException):
            log.exception(e)
            refresh(browser)
        return back_test_strategy_symbol(browser, inputs, properties, symbol, strategy_config, number_of_charts, first_symbol, results, input_locations, property_locations, interval_averages, symbol_averages, intervals, values, previous_elements, tries+1)
    else:
        log.exception(e)
        snapshot(browser, True, False)


def refresh_session(browser):
    global REFRESH_START
    interval_expired = timing.time() - REFRESH_START >= REFRESH_INTERVAL
    if interval_expired:
        refresh(browser)
        REFRESH_START = timing.time()
    return interval_expired


def get_strategy_statistic(browser, key, previous_elements):
    result = 0
    tries = 0
    css = css_selectors[key]
    while tries < config.getint('tradingview', 'create_alert_max_retries'):
        try:
            if isinstance(previous_elements[key], WebElement):
                try:
                    wait_for_element_is_stale(previous_elements[key])
                except TimeoutException as e:
                    log.info(e)
                    pass
                except Exception as e:
                    log.exception(e)

            el = find_element(browser, css, By.CSS_SELECTOR, False, False, 1)
            if not el:
                log.debug("NOT FOUND: {} = {}".format(By.CSS_SELECTOR, css))
                break
            text = repr(el.get_attribute('innerHTML')).replace('\\u2009', '')
            negative = text.find("neg") >= 0

            match = re.search(r"([\d|.]+)", text)
            if match:
                result = match.group(1)
                if negative:
                    result = "-{}".format(result)
            result = fast_real(result)
            if isinstance(result, float):
                result = "{:.10f}".format(result).rstrip('0')
            previous_elements[key] = el
            return result

        except StaleElementReferenceException:
            pass
        except InvalidSessionIdException as e:
            if str(e.msg).lower().find('invalid session id') >= 0:
                log.info("Handling of {} delegated to caller".format(e.msg))
                return e
            else:
                log.exception(e)
                return e
        except WebDriverException as e:
            if str(e.msg).lower().find('invalid session id') >= 0:
                log.info("Handling of {} delegated to caller".format(e.msg))
                return e
            else:
                log.exception(e)
                return e
        except Exception as e:
            # log.debug("{} = {}".format(By.CSS_SELECTOR, css))
            log.exception(e)
            return e
        tries += 1

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
    except StaleElementReferenceException:
        return retry_format_strategy(browser, inputs, properties, input_locations, property_locations, retry_number)
    except Exception as e:
        return e
        # refresh(browser)
        # if not retry_format_strategy(browser, inputs, properties, input_locations, property_locations, retry_number):
        #     log.exception(e)
        #     snapshot(browser, True)
    return True


def set_indicator_dialog_values(browser, inputs, input_locations):
    try:
        # get input titles
        cells = find_elements(browser, css_selectors['indicator_dialog_tab_cells'])
        titles = []
        for i, cell in enumerate(cells):
            title = re.sub(r"[\W]", '', cell.text.replace(' ', '_')).lower()
            titles.append(title)

        for key in inputs:
            value = inputs[key]
            index = -1
            for i, title in enumerate(titles):
                if (title == key) or ((not EXACT_CONDITIONS) and title.startswith(key)):
                    index = i

            if index >= 0:
                # check first if it is a set of values, e.g. 100 USD
                if isinstance(value, dict):
                    for sub_index, sub_key in enumerate(value):
                        sub_value = value[sub_key]
                        set_indicator_dialog_value(browser, input_locations, key, value, index, sub_key, sub_value, sub_index)
                else:
                    set_indicator_dialog_value(browser, input_locations, key, value, index)
    except Exception as e:
        log.exception(e)
        snapshot(browser, True)


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
                    element = find_element(browser, css + input_css, By.CSS_SELECTOR, False, False, 1)
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
                element = find_element(browser, css + input_css, By.CSS_SELECTOR, True, False, 1)
                if element:
                    css += input_css
                else:
                    css += ' div[class^="selected"]'
                # save the css for future use in this run
                locations[key] = css

        if css:
            val = value
            if sub_index >= 0:
                val = sub_value

            element = find_element(browser, css)
            if isinstance(element, WebElement):
                # check if it is an input box
                if element.tag_name == 'input':
                    if element.get_attribute("type") == "checkbox":
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
        else:
            log.error("Unable to generate CSS")
    except StaleElementReferenceException:
        retry_set_indicator_dialog_value(browser, locations, key, value, sub_key, sub_value, sub_index, retry_number)
    except Exception as e:
        return e
    return True


def retry_set_indicator_dialog_value(browser, locations, key, value, sub_key, sub_value, sub_index, retry_number):
    max_retries = config.getint('tradingview', 'create_alert_max_retries')
    if config.has_option('tradingview', 'indicator_values_max_retries'):
        max_retries = config.getint('tradingview', 'indicator_values_max_retries')
    if retry_number < max_retries:
        return set_indicator_dialog_value(browser, locations, key, value, sub_key, sub_value, sub_index, retry_number + 1)
    else:
        return False


def retry_format_strategy(browser, inputs, properties, input_locations, property_locations, retry_number):
    max_retries = config.getint('tradingview', 'create_alert_max_retries')
    if config.has_option('tradingview', 'indicator_values_max_retries'):
        max_retries = config.getint('tradingview', 'indicator_values_max_retries')
    if retry_number < max_retries:
        return format_strategy(browser, inputs, properties, input_locations, property_locations, retry_number + 1)
    else:
        return False


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
    except Exception as e:
        return e
        # log.exception(e)
        # refresh(browser)
        # return retry_select_strategy(browser, strategy_config, chart_index, retry_number)
    return indicator_index


def retry_select_strategy(browser, strategy_config, chart_index, retry_number):
    max_retries = config.getint('tradingview', 'create_alert_max_retries') * 10
    if config.has_option('tradingview', 'indicator_values_max_retries'):
        max_retries = config.getint('tradingview', 'indicator_values_max_retries')
    if retry_number < max_retries:
        return select_strategy(browser, strategy_config, chart_index, retry_number + 1)


def open_indicator_settings(browser, indicator_name, chart_index=0):
    try:
        # css = 'div.chart-container.active'
        # active_chart = find_element(browser, css)
        xpath = '//div[@data-name="legend-source-item"]/div/div/div[starts-with(text(), "{}")]'.format(indicator_name)
        indicator_elements = find_elements(browser, xpath, By.XPATH)
        hover(browser, indicator_elements[chart_index])
        # click the settings button
        xpath = '//div[@data-name="legend-source-item"]/div/div/div[starts-with(text(), "{}")]/parent::div/parent::div//div[@data-name="legend-settings-action"]'.format(indicator_name)
        setting_elements = find_elements(browser, xpath, By.XPATH)
        setting_elements[chart_index].click()
        # wait_and_click(setting_elements[chart_index], xpath, CHECK_IF_EXISTS_TIMEOUT, By.XPATH)
        # click the settings dialog's input tab
        xpath = '//div[text()="Inputs"]'
        wait_and_click(browser, xpath, CHECK_IF_EXISTS_TIMEOUT, By.XPATH)
    except Exception as e:
        log.exception(e)
        snapshot(browser, True)


def close_indicator_settings(browser):
    try:
        css = 'div[data-name="indicator-properties-dialog"] button[name="cancel"]'
        wait_and_click(browser, css)
    except TimeoutException:
        pass
    except Exception as e:
        log.exception(e)


def generate_atomic_values(items, strategies, depth=0):
    recursive_depth = depth + 1
    result = []
    for item in items:
        if isinstance(items[item], dict):
            sub_results = []
            generate_atomic_values(items[item], sub_results, recursive_depth)
            for sub_result in sub_results:
                tmp = dict(items)
                tmp[item] = sub_result
                tmp_result = generate_atomic_values(tmp, strategies, recursive_depth)
                atomic = True

                for tmp_item in tmp:
                    if isinstance(tmp[tmp_item], dict):
                        for key in tmp[tmp_item]:
                            if isinstance(tmp[tmp_item][key], list):
                                atomic = False
                                break
                        if not atomic:
                            break
                    if isinstance(tmp[tmp_item], list):
                        atomic = False
                        break

                if atomic and tmp not in strategies:
                    strategies.append(tmp)

                result.append(tmp_result)
        elif isinstance(items[item], list):
            for value in items[item]:
                tmp = dict(items)
                tmp[item] = value
                tmp_result = generate_atomic_values(tmp, strategies, recursive_depth)

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
    # if all we have at the end of the recursive method call is nothing, then the items is just a single variant, e.g. "{'obv': True, 'macd': False}"
    if depth == 0 and not strategies:
        strategies.append(items)
    return result


def get_config_values(items):
    if isinstance(items, list) or isinstance(items, dict):
        for key in items:
            items[key] = generate_config_values(items[key])
    return items


def generate_config_values(value):
    result = []
    delimiter_range = ' - '
    delimiter_increment = '&'
    increment = None

    # if the value is a list, generate values recursively
    if isinstance(value, list):
        for item in value:
            result.append(generate_config_values(item))
    if isinstance(value, dict):
        for item in value:
            value[item] = generate_config_values(value[item])
        result = value
    elif isinstance(value, str) and value.find(delimiter_range) > 0:
        decimal_places = 0

        if value.find(delimiter_increment) > 0:
            [value, increment] = value.split(delimiter_increment)
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

        [start, end] = value.split(delimiter_range)
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

        if not (isinstance(start, int) or isinstance(start, float)):
            raise ValueError("Invalid range value: '{}'".format(start))
        if not (isinstance(end, int) or isinstance(end, float)):
            raise ValueError("Invalid range value: '{}'".format(end))
        if not (isinstance(increment, int) or isinstance(increment, float)):
            raise ValueError("Invalid increment value: '{}'".format(increment))

        for number in numpy.arange(start, end, increment):
            if decimal_places > 0:
                result.append(float(round(number, decimal_places)))
            else:
                result.append(int(number))
        result.append(end)
        # if decimal_places > 0:
        #     result.append(float(round(end, decimal_places)))
        # else:
        #     result.append(int(end))
    else:
        result = value
        # log.error("unable to convert {} is of numpy type {} to a python type".format(value, type(value)))
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
        except Exception as e:
            return e
        tries += 1

    return result


def summary(total_alerts, counter_alerts):
    result = "No alerts or signals set"
    elapsed = timing.time() - timing.start

    avg = elapsed
    if total_alerts > 0:
        avg = '%s' % float('%.5g' % (elapsed / total_alerts))
    if counter_alerts > 0 and len(triggered_signals) > 0:
        result = "{} markets screened, {} alerts set and {} signals triggered with an average process time of {} seconds per market".format(str(total_alerts), str(counter_alerts), str(len(triggered_signals)), avg)
    elif counter_alerts > 0:
        result = "{} markets screened and {} alerts set with an average process time of {} seconds per market".format(str(total_alerts), str(counter_alerts), avg)
    elif len(triggered_signals) > 0:
        result = "{} markets screened and {} signals triggered with an average process time of {} seconds per market".format(str(total_alerts), len(triggered_signals), avg)
    return result
