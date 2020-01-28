# Kairos
Web automation tool using Python, Selenium and Chrome's Web Driver.
Kairos aims to help you save time by automating repetitive tasks on TradingView such as refreshing alerts and creating new ones.

Besides this document you can also find instructional videos [here](https://www.youtube.com/channel/UCvOH0PusMl0izmdwNDegBeA/videos). 

## Table of contents
* [Features](#features)
* [Prerequisites](#prerequisites)
* [Installing](#installing)
* [Post installation](#post-installation)
* [Configuring Kairos](#configuring-kairos)
* [Command line examples](#command-line-examples)
* [Troubleshooting](#troubleshooting)
* [Feedback](#feedback)
* [Acknowledgements](#acknowledgements)
* [Author](#author)
* [Donate](#donate)
* [License](#license)

## Features
* Set alerts automatically on TradingView through web automation. 
* Define multiple charts with multiple alerts per chart on multiple time frames in one file.
* Add (limited) dynamic data to your alert messages. 
* Run from command line and in the background.
* Send a summary mail.
* Generate a TradingView watchlist from the summary mail.
* Import generated TradingView watchlist.
* Send signals to a webhook/endpoint or a Google Sheet 

## Prerequisites
* [Python 3](https://www.python.org/downloads/)
* [ChromeDriver](http://chromedriver.chromium.org/downloads) with [Chrome latest version](https://www.google.com/chrome/); or [geckodriver](https://github.com/mozilla/geckodriver/) with [Firefox](https://www.mozilla.org/en-US/firefox/) (for OS X)

_Note: when you install Python on Windows make sure that it's part of your PATH._

## Installing ##
If you run Ubuntu 18.04 there is a list of commands here: [Ubuntu 18.04 - command line installation](#ubuntu-1804---command-line-installation).
### From archive (Linux, OS X and Windows)
_If you are running Linux / OS X then run listed commands with **sudo**_ 
* [Install Python 3](https://www.python.org/downloads/) - [OS X guide](https://www.macworld.co.uk/how-to/mac/python-coding-mac-3635912/) - [Windows guide](https://www.ics.uci.edu/~pattis/common/handouts/pythoneclipsejava/python.html)
* [Install Chrome latest version](https://www.google.com/chrome/) or [geckodriver](https://github.com/mozilla/geckodriver/) (OS X)
* [Download ChromeDriver](http://chromedriver.chromium.org/downloads) or [Firefox](https://www.mozilla.org/en-US/firefox/) (OS X)
* [Download](https://github.com/timelyart/Kairos/releases/latest) and extract the Kairos archive
* Open a terminal, or when on Windows an elevated command prompt
* Update setuptools:
```
pip install setuptools
pip install --upgrade setuptools
```
* Run the following command from the Kairos directory: 
```
python setup.py install
```
* Continue with the steps listed under section [Post installation](https://github.com/timelyart/Kairos#post-installation)

### From source
* Install / update setuptools:
```
pip install setuptools
pip install --upgrade setuptools
```
* Clone archive and install:
```
git clone --recursive https://github.com/timelyart/kairos.git
cd Kairos
python setup.py install
```
* Continue with the steps listed under section [Post installation](https://github.com/timelyart/Kairos#post-installation)

### Ubuntu 18.04 - command line installation
```
cd ~/
wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
echo 'deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main' | sudo tee /etc/apt/sources.list.d/google-chrome.list
sudo apt-get update
sudo apt-get install google-chrome-stable
sudo apt-get install unzip
sudo apt-get install python3.7
sudo apt-get install python3-setuptools
wget https://chromedriver.storage.googleapis.com/2.43/chromedriver_linux64.zip
unzip chromedriver_linux64.zip
sudo mv chromedriver /usr/bin/chromedriver
sudo chown root:root /usr/bin/chromedriver
sudo chmod +x /usr/bin/chromedriver
mkdir -p Git/repositories
cd Git/repositories/
git clone https://github.com/timelyart/Kairos.git
cd Kairos/
sudo python3 setup.py install
```
* Continue with the steps listed (below) under section [Post installation](https://github.com/timelyart/Kairos#post-installation)
## Post installation
* Open the Kairos directory
* Rename [_kairos.cfg](_kairos.cfg) to **kairos.cfg** and open it.
* Take good notice of the options that are available to you in the [kairos.cfg](_kairos.cfg). Fill in the blanks and adjust to your preference and limitations.
* Rename [_alert.yaml](yaml/_alert.yaml) to **alert.yaml** and open it.
* Edit the **alert.yaml** to your liking. Study the section [Defining TradingView alerts](https://github.com/timelyart/Kairos#defining-tradingview-alerts) to get a feeling for the structure of the document. Together with the inline documentation within the YAML file, it should give you a good idea on how to cater it to your preferences. If you have questions please contact me.
* Finally, run the following command from the Kairos directory:
```
python main.py alert_multiple.yaml
```           
**_TIP: Run Kairos periodically using s scheduler. Use a separate file for each interval you wish to run, e.g. weekly.yaml, daily.yaml and 4hourly.yaml._**

## Configuring Kairos
### Editing YAML files
When it comes to configuring Kairos, there are two type of files:

* The mandatory [kairos.cfg](_kairos.cfg) file which settings are used by Kairos every time you run it. Once you have set this up, you can forget about it.
* So-called [YAML](https://en.wikipedia.org/wiki/YAML) files which specify what Kairos should do in a particular run.

You may find that both file types have the same setting, i.e. _run-in-background_. In these cases the [YAML](https://en.wikipedia.org/wiki/YAML) file will take precedence over [kairos.cfg](_kairos.cfg). 

This may sound a little abstract and where to begin? Luckily, Kairos comes with a number of [templates/example files](yaml). 
* [refresh.yaml](yaml/refresh.yaml); re-activates inactive alerts when certain options are set in your [kairos.cfg](_kairos.cfg) file.
* [root.yaml](yaml/root.yaml), [branch_in_branch.yaml](yaml/branch_in_branch.yaml) and [branch.yaml](yaml/branch.yaml); shows how you can call other YAML files from within a YAML file.
* [_alert.yaml](yaml/_alert.yaml); is a template for creating alerts automatically in TradingView.
* [_alert_davo.yaml](yaml/_alert_davo.yaml); is a template for creating alerts with the Davo indicator.
* [_alert_multiple.yaml](yaml/_alert_multiple.yaml); is a template for defining multiple alerts in one file.
* [_browse.yaml](yaml/_browse.yaml); is a template for simply browsing automatically through a watchlist on TradingView.
* [_screener_to_watchlist.yaml](yaml/_screener_to_watchlist.yaml); is a template for creating watchlists using TradingView's screener.
* [_signal.yaml](yaml/_signal.yaml); is a template for scanning charts with indicators with specific values.
* [_signal_golden_cross.yaml](yaml/_signal_golden_cross.yaml); is a template for scanning charts on which a Golden Cross just occurred.
* [_strategies.yaml](yaml/_strategies.yaml); is a template for setting strategies in TradingView for backtesting purposes. Be forewarned, running backtests can take a long time during which your connection to TradingView may be lost. It can also generate tons of data.
* [_summary.yaml](yaml/_summary.yaml); is a template file for generating summaries of alerts/signals and exporting data to e-mail, a TradingView watchlist, Google Sheet, and webhooks. 

Generally speaking, you want to remove the _ (underscore) from the file name prior to editing it. This ensures your file doesn't get overwritten with a future update of Kairos.
Please read the inline comments of the templates carefully. They are there to give context and necessary information. 

#### YAML within YAML 
As of version 1.3.0 you can load [YAML](https://en.wikipedia.org/wiki/YAML) files from any other [YAML](https://en.wikipedia.org/wiki/YAML) file by including the following in your [YAML](https://en.wikipedia.org/wiki/YAML) file:
```
file: path_to/my_other_yaml_file.yaml 
```
Consider **root.yaml**:
```
root:
  - branch:
      - branch: ["leaf", "leaf", "leaf"]
      - file: "branch_in_branch.yaml"
  - branch: ["leaf", "leaf", "leaf"]
  - file: "branch_in_branch.yaml"
```
By using other [YAML](https://en.wikipedia.org/wiki/YAML) files you can re-use parts of your [YAML](https://en.wikipedia.org/wiki/YAML) and share them with other [YAML](https://en.wikipedia.org/wiki/YAML) definitions you may have.

If you find yourself copying and pasting a lot, you might want to consider to put some or all of that code into a separate YAML file.

The files needed to run **root.yaml** can be found in the folder [yaml](yaml) and I highly encourage to look into them to figure out how they work.

When creating/editing [YAML](https://en.wikipedia.org/wiki/YAML) files you have to be careful with indentation and you might want to use a website like [https://yamlchecker.com](https://yamlchecker.com) to check your YAML before running it with Kairos. Also, note that values are **case sensitive**.

#### Troubleshooting YAML
When Kairos runs, it will create a temporary copy of your [YAML](https://en.wikipedia.org/wiki/YAML) file called **my_file.yaml.tmp**. This temporary file includes your [YAML](https://en.wikipedia.org/wiki/YAML) file (obviously) but also any [YAML](https://en.wikipedia.org/wiki/YAML) file that gets referenced from your [YAML](https://en.wikipedia.org/wiki/YAML) files.<br>
In case of an error, a **my_file.yaml.err** will be created. Kairos error messages will reference the line and column number of the **.err** file.

#### Examples
The rest of this chapter will elaborate on setting up various use cases with [YAML](https://en.wikipedia.org/wiki/YAML) files.<br>
Signals are the core of Kairos and strategies are really useful for automatic backtesting. Although Alerts have largely become obsolete with Signals, they are still expanded upon here. They were the core of version 1 after all, and may still be provide to be useful to some. 
### Alerts
Please read [Editing YAML files](https://github.com/timelyart/Kairos#editing-yaml-files) if you haven't done so already.

Steps:
* Create a chart and plot the indicators you would like to set alerts for
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
### Signals
Please read [Editing YAML files](https://github.com/timelyart/Kairos#editing-yaml-files) if you haven't done so already.

As of [version 2](https://github.com/timelyart/Kairos/tree/v2.0.0), you can screen markets based upon indicator values.
Kairos can read indicator values and then use these values to determine if a particular setup has fired or not. For example, when the 50 SMA has crossed the 200 SMA (Golden Cross). 
Kairos can read the values of multiple indicators and has a simple equation language to determine if indicator values meet the requirements of setups.
The equation language is built up in the following format: 
```
<left-hand-side> <type> <right-hand-side>
```
Where ``<left-hand-side>`` and ``<right-hand-side>`` is either a fixed value, or an indicator value at a specific index; and where ``type`` is one of the following: ``=, <=, >=, <, >, !=``.
A [YAML](https://en.wikipedia.org/wiki/YAML) definition might be:
```
    trigger:
      # The left and right hand side can have one (or both)of the following values:
      # - index: indicator provided value found at the defined index
      # - value: a literal value which can be anything
      # If both index and value are set, then index will take precedence
      left-hand-side:
        index: 6
        value:
        # list of values to ignore, e.g. you can use this to ignore "n/a" values
        ignore: [n/a, 0.00000000]
      right-hand-side:
        index: 7
        value:
        ignore: [n/a, 0.00000000]
      # Define how the equation should be processed. Possible values are: =, <=, >=, <, >, != (use quotation marks)
      type: ">"
``` 
Meaning that in order for Kairos to signal the value found at index 6 of the indicator must be *greater* than the value at index 7.    
You can define multiple indicators each with their own trigger. Only when each trigger for every indicator returns 'true', will Kairos notify the user that the setup has triggered. 

#### Generic Template
Use the [_signal.yaml](yaml/_signal.yaml) as a base for your own [yaml](https://en.wikipedia.org/wiki/YAML) file.<br> 
_Note: [_signal_golden_cross.yaml](yaml/_signal_golden_cross.yaml) has more settings filled in for you and may be easier to start with (see [Golden Cross Template](https://github.com/timelyart/Kairos#golden-cross-template))._

Steps:
* Create a chart and add the indicator(s) you want to scan for values. Make sure that the indicator values are readable on the chart.
* Create a copy/rename [_signal.yaml](yaml/_signal.yaml) and open it for editing.
* Go through the file meticulously filling in settings as needed. Save it after you are finished.
* Run your [YAML](https://en.wikipedia.org/wiki/YAML) file with the following command:
```
python main.py signal.yaml
```
All the settings within the [YAML](https://en.wikipedia.org/wiki/YAML) file are explained. If you miss an explanation, or if an explanation isn't clear. Please, open an [issue](https://github.com/timelyart/Kairos/issues) so it may get addressed.   

#### Golden Cross Template
Use the [_signal_golden_cross.yaml](yaml/_signal_golden_cross.yaml) as a base for your own [yaml](https://en.wikipedia.org/wiki/YAML) file. 

Steps:
* Create a chart and add the **[Golden Cross by Chuckytuh](https://www.tradingview.com/script/qWFFKwNN-Golden-Cross/)**. Make sure that the indicator values are readable on the chart.
* Create a copy/rename [_signal_golden_cross.yaml](yaml/_signal_golden_cross.yaml) and open it for editing.
* Go through the file meticulously filling in settings as needed. Save it after you are finished.
* Run your [YAML](https://en.wikipedia.org/wiki/YAML) file with the following command:
```
python main.py signal_golden_cross.yaml
```
All the settings within the template files are explained. If you miss an explanation, or if an explanation isn't clear. Please, open an issue so it may get addressed.

### Strategies
You can use strategies to backtest TradingView strategies, much in the same way as signals or alerts. Kairos will run your TradingView strategy for each symbol on your watchlist(s) and save the results for you in a [JSON](https://en.wikipedia.org/wiki/JSON) file. 
You can open the [JSON](https://en.wikipedia.org/wiki/JSON) with your favorite web browser or text editor. The results that are saved are per timeframe, symbol and per different input/property setting (see below). Kairos will also aggregate results to help with analyzing the data. 

Much like you can set alerts, you can set the inputs/properties of a strategy as well. This can be any number of combinations of inputs and properties, but try to keep the number down as Kairos will run a strategy for each combination of inputs and properties.  
A word of caution, running large watchlists with a lot of different combinations of inputs/properties will be notoriously slow and can take up hours, or even days.
Since TradingView has a limit on how long you can keep a session with them open, Kairos might fail before it has finished. The best way to work around this, is to first identify optimal inputs/properties for a strategy by limiting your watchlist. After you have found good candidates of input/property combinations, you can then use them in a separate run on a bigger watchlist.       

The [yaml](https://en.wikipedia.org/wiki/YAML) to define strategies is something like below.   
```
strategies:    
  - name: "my_strategy"
    pane_index: 0
    inputs: {my_first_input: 6, my_second_input: [60, 240, 1D, 1W], my_third_input: yes}
    properties: {initial_capital: 1000, base_currency: EUR, order_size: {0: 1 - 5&1, 1: '% of equity'}, commission: {0: [0.25], 1: '%'}, verify_price_for_limit_orders: 10, slippage: 10, recalculate: {after_order_filled: yes, on_every_tick: no}}
```
Note, that the example [yaml](https://en.wikipedia.org/wiki/YAML) files contain a lot of inline comments to help you with filling them out.

#### Generic Template
Use the [_strategies.yaml](yaml/_strategies.yaml) as a base for your own [yaml](https://en.wikipedia.org/wiki/YAML) file.

Steps:
* Create a chart and add the strategy you want to backtest.
* Create a copy/rename [_strategies.yaml](yaml/_strategies.yaml) and open it for editing.
* Go through the file meticulously filling in settings as needed. Save it after you are finished.
* Run your [YAML](https://en.wikipedia.org/wiki/YAML) file with the following command:
```
python main.py strategies.yaml
```
All the settings within the [YAML](https://en.wikipedia.org/wiki/YAML) file are explained. If you miss an explanation, or if an explanation isn't clear. Please, open an [issue](https://github.com/timelyart/Kairos/issues) so it may get addressed.  
## Command line examples
* Refresh your existing alerts (depends on the settings in your kairos.cfg so proceed with caution).
```
python main.py refresh.yaml
```
* Browse through your watchlist going from symbol to symbol at a regular interval. 
  1. Rename [_browse.yaml](yaml/_browse.yaml) to **browse.yaml** and open it
  2. Fill in the blanks
  3. Run:
  ```
  python main.py browse.yaml
  ```
* Generate a summary mail from unread TradingView Alert mails
```
python main.py -s
```
## Troubleshooting
A lot can go wrong running web automation tools like Kairos. These are the most common ones:
* The web page / server hasn't handled the interaction (a click or some input) yet before the next interaction is tried   
* A popup is displayed over the point that Kairos wants to interact with, e.g. a tooltip or TradingView's 'too many devices message'.
* A form (e.g. an alert)was submitted but you don't see results.
* The markup of the web page has changed thereby breaking the flow of Kairos.

These issues are all related and amount to Kairos unable to either find an element or to interact with an element. You will get errors (see debug.log) like:
* Message: unknown error: [...] is not clickable at point [...]
* Time out exceptions
* Not clickable exceptions
* Not visible exceptions

### Solutions 
#### Run multiple times
If you are running Kairos for the first time, then Chrome hasn't cached anything yet. Try to run it a couple of times and ignore any errors. 
Of course, clearing the cache will, in all likelihood, spawn the same issues again.

#### Run on a different time of day
At certain times during the day TradingView can become less responsive. Try to run Kairos on a different time.
If the issue persists, try to [Increase delays](#increase-delays) 

#### Increase delays
If you have run Kairos five times or so, and still encounter issues try to increase the **_break_mini_**, **_break_** and / or **_submit_alert_** in the [kairos.cfg](_kairos.cfg).

#### Check existing issues
If, after increasing wait times, you still get errors then the markup of the web page may have changed.
Check if it is an [existing issue](https://github.com/timelyart/Kairos/issues), and if it is not: [open](https://github.com/timelyart/Kairos/issues/new) one.

## Feedback
Feedback is invaluable. Please, take the time to give constructive feedback by opening an [issue](https://github.com/timelyart/Kairos/issues) so that this project may be improved on code and documentation.

## Acknowledgements
[DorukKorkmaz](https://github.com/dorukkorkmaz), for providing a starting point with his [TradingView scraper](https://github.com/DorukKorkmaz/tradingview-scraper).

[PaulMcG](https://stackoverflow.com/users/165216/paulmcg), for his [timing module](https://stackoverflow.com/questions/1557571/how-do-i-get-time-of-a-python-programs-execution/1557906#1557906)

## Author ##
[timelyart](https://github.com/timelyart)

## Donate
If you find value in this project and you would like to donate, please do so [here](DONATE.md)  

## License
This project is licensed under the GNU GPLv3 License - see the [LICENSE.md](LICENSE.md) file for details. 
