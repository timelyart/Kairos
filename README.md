# Kairos #
Web automation tool using Python, Selenium and Chrome's Web Driver.
Kairos aims to help you save time by automating repetitive tasks on TradingView such as refreshing alerts and creating new ones.
  
## Getting Started ##
These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

## Prerequisites ##
* [Python 3](https://www.python.org/downloads/)
* [ChromeDriver](http://chromedriver.chromium.org/downloads)

_Note: when you install Python on Windows make sure that it's part of your PATH._

## Installing ##
### Windows Installer ###
An advantage of using the Windows installer is that you can uninstall it easily through Windows own 'Add or remove programs' dialogue, but the installer will install Kairos under your Python installation and you cannot change this. Use the install method [Archive](https://github.com/timelyart/Kairos#archive-linux--macos--windows) listed below if you want more control over where files are installed.  

* [Install Python 3](https://www.python.org/downloads/) - [macOS guide](https://www.macworld.co.uk/how-to/mac/python-coding-mac-3635912/) - [Windows guide](https://www.ics.uci.edu/~pattis/common/handouts/pythoneclipsejava/python.html)
* [Download ChromeDriver](http://chromedriver.chromium.org/downloads)
* [Download](dist) and run the installer as an Administrator.
* Continue with the steps listed under section [Post installation](https://github.com/timelyart/Kairos#post-installation)

### Archive Linux / macOS / Windows ###
* [Install Python 3](https://www.python.org/downloads/) - [macOS guide](https://www.macworld.co.uk/how-to/mac/python-coding-mac-3635912/) - [Windows guide](https://www.ics.uci.edu/~pattis/common/handouts/pythoneclipsejava/python.html)
* [Download ChromeDriver](http://chromedriver.chromium.org/downloads)
* [Download](dist) and extract the Kairos archive
* Run the following command from the Kairos directory: 
```
python setup.py install
```
* Continue with the steps listed under section [Post installation](https://github.com/timelyart/Kairos#post-installation)

### From source ###
```
git clone --recursive https://github.com/timelyart/kairos.git
cd python
python setup.py install
```
* Continue with the steps listed under section [Post installation](https://github.com/timelyart/Kairos#post-installation)

## Post installation process ##
* Open the Kairos directory
* Rename [_kairos.cfg](_kairos.cfg) to **kairos.cfg** and open it.
* Take good notice of the options that are available to you in the [kairos.cfg](kairos.cfg).Fill in the blanks and adjust to your preference and limitations.
* Rename [tv/_example.yaml](tv/_example.yaml) to **example.yaml** and open it.
* Edit the [example.yaml](tv/_example.yaml) to your liking. Study the section [Defining TradingView alerts](https://github.com/timelyart/Kairos#defining-tradingview-alerts) to get a feeling for the structure of the document. Together with the inline documentation within the YAML file, it should give you a good idea on how to cater it to your preferences. If you have questions please contact me.
* Finally, run the following command from the Kairos directory:
```
python main.py example.yaml
```           
**_TIP 1: Run Kairos periodically. Use a separate file for each interval you wish to run, e.g. weekly.yaml, daily.yaml and 4hourly.yaml._**

**_TIP 2: If all you want to do is 'refresh' existing alerts, run a yaml with no watchlist defined._**

## Defining TradingView alerts
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
      durarion: 10 seconds
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
      durarion: 10 seconds
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
      durarion: 10 seconds
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
      durarion: 10 seconds
    send:
      email: yes
      email-to-sms: no
      sms: no
      notify-on-app: no
    message:
      prepend: no
      text:      
```
## Troubleshooting ##
A lot can go wrong running web automation tools like Kairos. These are the most common ones:
* The web page / server hasn't handled the interaction (a click or some input) yet before the next interaction is tried   
* A popup is displayed over the point that Kyros wants to interact with, e.g. a tooltip or TradingView's 'too many devices message'.
* A form (e.g. an alert)was submitted but you don't see results.
* The markup of the web page has changed thereby breaking the flow Kairos.

These issues are all related and amount to Kairos unable to either find an element or to interact with an element. You will get errors (see debug.log) like:
* Message: unknown error: [...] is not clickable at point [...]
* Time out exceptions
* Not visible exceptions

### Solutions ###
#### Run multiple times ###
If you are running Kairos for the first time, then Chrome hasn't cached anything yet. Try to run it a couple of times and ignore any errors. 
Of course, clearing the cache will, in all likelihood, spawn the same issues again.

#### Increase delays ###
If you have run Kairos five times or so, and still encounter issues try to increase the **_wait_time_break_mini_**, **_wait_time_break_** and / or **_wait_time_submit_alert_** in the [kairos.cfg](_kairos.cfg).

#### Check existing issues ###
If, after increasing wait times, you still get errors then the markup of the web page may have changed.
Check if it is an [existing issue](https://github.com/timelyart/Kairos/issues), and if it is not: [open](https://github.com/timelyart/Kairos/issues/new) one.

## Feedback ##
Feedback is invaluable. Please, take the time to give constructive feedback by opening an [issue](https://github.com/timelyart/Kairos/issues) so that this project may be improved on code and documentation.

## Donate ##
If you find value in this project and you would like to donate, please do so [here](DONATE.md)  

## Author ##
[timelyart](https://github.com/timelyart)

## Acknowledgments ##   
[DorukKorkmaz](https://github.com/dorukkorkmaz), for providing a starting point with his [TradingView scraper](https://github.com/DorukKorkmaz/tradingview-scraper).

[PaulMcG](https://stackoverflow.com/users/165216/paulmcg), for his [timing module](https://stackoverflow.com/questions/1557571/how-do-i-get-time-of-a-python-programs-execution/1557906#1557906)

## License ##
This project is licensed under the GNU GPLv3 License - see the [LICENSE.md](LICENSE.md) file for details. 
