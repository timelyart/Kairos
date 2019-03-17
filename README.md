# Kairos #
Web automation tool using Python, Selenium and Chrome's Web Driver.
Kairos aims to help you save time by automating repetitive tasks on TradingView such as refreshing alerts and creating new ones.

## Table of contents ##
* [Features](#features)
* [Prerequisites](#prerequisites)
* [Installing](#installing)
* [Post installation](#post-installation)
* [Defining TradingView alerts](#defining-tradingview-alerts)
* [Command line examples](#command-line-examples)
* [Troubleshooting](#troubleshooting)
* [Acknowledgements](#acknowledgements)
* [Author](#author)
* [End-User License Agreement](#end-user-license-agreement)

## Features ##
* Set alerts automatically on TradingView through web automation. 
* Define multiple charts with multiple alerts per chart on multiple time frames in one file.
* Add (limited) dynamic data to your alert messages. 
* Run from command line and in the background.
* Send a summary mail.
* Generate a TradingView watchlist from the summary mail.

## Prerequisites ##
* [Python 3.7](https://www.python.org/downloads/)
* [ChromeDriver](http://chromedriver.chromium.org/downloads) with [Chrome latest version](https://www.google.com/chrome/); or [geckodriver](https://github.com/mozilla/geckodriver/) with [Firefox](https://www.mozilla.org/en-US/firefox/) (for OS X)

_Note: when you install Python on Windows make sure that it's part of your PATH._

## Installing ##
Note: if you are running Linux / OS X then run listed commands with **sudo**. If you have multiple versions of Python then run listed commands with **python3** instead of **python**. 
* [Install Python 3](https://www.python.org/downloads/) - [OS X guide](https://www.macworld.co.uk/how-to/mac/python-coding-mac-3635912/) - [Windows guide](https://www.ics.uci.edu/~pattis/common/handouts/pythoneclipsejava/python.html)
* [Install Chrome latest version](https://www.google.com/chrome/) or [geckodriver](https://github.com/mozilla/geckodriver/) (OS X)
* [Download ChromeDriver](http://chromedriver.chromium.org/downloads) or [Firefox](https://www.mozilla.org/en-US/firefox/) (OS X)
* Open a terminal, or when on Windows an elevated command prompt
* Install and update setuptools:
```
pip install setuptools
pip install --upgrade setuptools
```
* Run the following command from the Kairos directory: 
```
python setup.py install
```

* Continue with the steps listed under section [Post installation](#post-installation)

## Post installation ##
* Open the Kairos directory
* Rename [_kairos.cfg](_kairos.cfg) to **kairos.cfg** and open it.
* Take good notice of the options that are available to you in the [kairos.cfg](kairos.cfg). Fill in the blanks and adjust to your preference and limitations.
* Rename [tv/_example.yaml](tv/_example.yaml) to **example.yaml** and open it.
* Edit the [example.yaml](tv/_example.yaml) to your liking. Study the section [Defining TradingView alerts](#defining-tradingview-alerts) to get a feeling for the structure of the document. Together with the inline documentation within the YAML file, it should give you a good idea on how to cater it to your preferences. If you have questions please contact me.
* Finally, run the following command from the Kairos directory:
```
python main.py example.yaml
```           
**_TIP: Run Kairos periodically using s scheduler. Use a separate file for each interval you wish to run, e.g. weekly.yaml, daily.yaml and 4hourly.yaml._**

## Defining TradingView alerts ##
Use the [example.yaml](tv/_example.yaml) as a base for your own [yaml](https://en.wikipedia.org/wiki/YAML) file.
NOTE: all values are case sensitive and should be exactly the same as when you manually create an alert. 

Steps:
* Create a chart and plot the indicators you would like to set alerts on
* Create a new yaml entry (use the template below) and set the chart's url
```
- url:
  timeframes: []
  watchlists: []
  alerts:
  - name:
    conditions: []
    options: "Once Per Bar Close"
    expiration: 86400
    show_popup: no
    sound:
      play: no
      ringtone: Hand Bell
      duration: 10 seconds
    send:
      email: yes
      email-to-sms: no
      sms: no
      notify-on-app: no
    message:
      prepend: no
      text:
```      
* Fill in the timeframe(s) and watchlist(s) you want to use
* Create a mock up alert and write down the options (case sensitive!) you select in order (going from left to right and from top to bottom)
* Fill in the rest of the template with your written down values

You can define in one file multiple charts with each chart having multiple alerts, like this:
```
charts:
- url:
  timeframes: []
  watchlists: []
  alerts:
  - name:
    conditions: []
    options: "Once Per Bar Close"
    expiration: 86400
    show_popup: no
    sound:
      play: no
      ringtone: Hand Bell
      duration: 10 seconds
    send:
      email: yes
      email-to-sms: no
      sms: no
      notify-on-app: no
    message:
      prepend: no
      text:
  - name:
    conditions: []
    options: "Only Once"
    expiration: 2
    show_popup: no
    sound:
      play: no
      ringtone: Hand Bell
      duration: 10 seconds
    send:
      email: yes
      email-to-sms: no
      sms: no
      notify-on-app: no
    message:
      prepend: no
      text:
- url:
  timeframes: []
  watchlists: []
  alerts:
  - name:
    conditions: []
    options: "Once Per Bar Close"
    expiration: 86400
    show_popup: no
    sound:
      play: no
      ringtone: Hand Bell
      duration: 10 seconds
    send:
      email: yes
      email-to-sms: no
      sms: no
      notify-on-app: no
    message:
      prepend: no
      text:      
```
## Command line examples ##
* Refresh your existing alerts (depends on the settings in your kairos.cfg so proceed with caution).
```
python main.py refresh.yaml
```
* Browse through your watchlist going from symbol to symbol at a regular interval. 
  1. Rename [_browse.yaml](tv/_browse.yaml) to **browse.yaml** and open it
  2. Fill in the blanks
  3. Run:
  ```
  python main.py browse.yaml
  ```
* Generate a summary mail from unread TradingView Alert mails
```
python main.py -s
```
## Troubleshooting ##
A lot can go wrong running web automation tools like Kairos. These are the most common ones:
* The web page / server hasn't handled the interaction (a click or some input) yet before the next interaction is tried   
* A popup is displayed over the point that Kairos wants to interact with, e.g. a tooltip or TradingView's 'too many devices message'.
* A form (e.g. an alert)was submitted but you don't see results.
* The markup of the web page has changed thereby breaking the flow Kairos.

These issues are all related and amount to Kairos unable to either find an element or to interact with an element. You will get errors (see debug.log) like:
* 'Message: unknown error: [...] is not clickable at point [...]'
* 'Time out' exceptions
* 'Not clickable' exceptions
* 'Not visible' exceptions

### Solutions ###
#### Run multiple times ###
If you are running Kairos for the first time, then Chrome hasn't cached anything yet. Try to run it a couple of times and ignore any errors. 
Of course, clearing the cache will, in all likelihood, spawn the same issues again.

#### Run on a different time of day###
At certain times during the day TradingView can become less responsive. Try to run Kairos on a different time.
If the issue persists, try to [Increase delays](#increase-delays) 

#### Increase delays ###
If you have run Kairos five times or so, and still encounter issues try to increase the **_break_mini_**, **_break_** and / or **_submit_alert_** in the [kairos.cfg](_kairos.cfg).

#### Report an issue ###
If, after increasing wait times, you still get errors then the markup of the web page may have changed.
Please send me an email (see [Author](#author)) with your debug.log file, used yaml file and your kairos.cfg. **Please make sure you have stripped your kairos.cfg of privacy sensitive data before sending it to me.**   

## Acknowledgements ##   
[DorukKorkmaz](https://github.com/dorukkorkmaz), for providing a starting point with his [TradingView scraper](https://github.com/DorukKorkmaz/tradingview-scraper).

[PaulMcG](https://stackoverflow.com/users/165216/paulmcg), for his [timing module](https://stackoverflow.com/questions/1557571/how-do-i-get-time-of-a-python-programs-execution/1557906#1557906)

## Author ##
[timelyart](https://github.com/timelyart)

[timelyart@protonmail.com](mailto:timelyart@protonmail.com)

## End-User License Agreement ##
This project comes with an End-User License Agreement (EULA) which you can read here:
[https://eulatemplate.com/live.php?token=F2am7Ud98HlFDECoTq2GYhIksQmn6T9A](https://eulatemplate.com/live.php?token=F2am7Ud98HlFDECoTq2GYhIksQmn6T9A) 
