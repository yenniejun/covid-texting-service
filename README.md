# Texting Service for COVID-19 Stats

This is a texting service that allows you stay updated on the COVID-19 statistics for your region.

Currently, I am focusing on my home state of Louisiana. Therefore, you can text the name of any Louisiana Parish, and you will immediately get the number of cases and deaths in that parish. You can also text the name of any US State and get the stats for those as well. Eventually, I would like to be able to support all of the states and territories in the US.

_             |  _
:-------------------------:|:-------------------------:
![](/img/text_screenshot_1.png)  |  ![](/img/text_screenshot_2.png)

# About the Project

## Built With
* [Twilio](https://www.twilio.com/)
* [Flask](https://palletsprojects.com/p/flask/)
* [Selenium](https://selenium-python.readthedocs.io/)
* [ngrok](https://ngrok.com/)

## Why Texting Service?

The reason I created a texting service is to ensure that even those without Internet can access the latest stats on COVID in their region. There are currently a lot of numbers and resources on many different websites, but they are not accessible to those without Internet access. 


According to a [2019 Pew Research survey](https://www.pewresearch.org/fact-tank/2019/04/22/some-americans-dont-use-the-internet-who-are-they/), 10% of Americans (nearly 33 million people) do not use the Internet. In [Louisiana](https://broadbandnow.com/Louisiana), over 400,000 people do not have access to a wired connection capable of 25mbps download speeds, and 262,000 people do not have any wired Internet providers available where they live. 

However, most people have texting, and a service like this would make it easier to access the most up-to-date COVID numbers for the areas that you care most about - at the state level as well as at the local (parish) level.

Note: Louisiana currently has a texting service (text LACOVID to 898211), but it focuses more on recent state-wide announcements, and often contains links, which may not be accessible to those without Internet connection. Further, it doesn't tell you the most up-to-date numbers on COVID in your region, which is very pertinent residents as you increasingly self-quarantine.


## Stats
I am getting my stats for Louisiana from the [Louisiana CDC site](http://ldh.la.gov/Coronavirus/). 

I am getting my stats for the U.S. States from [Worldometers](https://www.worldometers.info/coronavirus/country/us/). I scrape these stats using Selenium from the respective sites and pull the live numbers.




# Getting Started

To set up this service locally, you will need to set up the twilio service and the Flask framework.

1. Clone the repo: 

```git clone https://github.com/yenniejun/covid-texting-service.git```

2. Install a [Chrome Driver](https://chromedriver.chromium.org/)
3. Activate virtual environment and install selenium
```
pip install virtualenv
source venv/bin/activate
pip install selenium
```
4. I would recommend following the set-up steps in the [twilio tutorial](https://www.twilio.com/docs/sms/quickstart/python-msg-svc). This will help you get a phone number, connect the number with the local backend, and to setup ngrok.

# Usage
In Terminal, you should have ngrok open in one tab and the Flask application in another.

To run locally, run ngrok to expose the service to the Internet.

`ngrok http 5000`


Once you have ngrok running, you can run the Flask application.

`
python3 run.py
`


ngrok             |  flask
:-------------------------:|:-------------------------:
![](/img/ngrok.png)  |  ![](/img/runpy.png)


Text "HELLO" from your phone to the phone number to get started. Debug statements will show up on the Terminal window running the application.


# Looking Forward
* Investigate more accurate source of stats
* Investigate an efficient way of auto-refresh
* Investigate a caching system... Currently I am pulling each time ... Since the numbers on the official sites do not update actually real-time, I don't need to use the chrome webdriver with each query... I can simluate real-time by pulling every hour or whatever number makes the most sense. TODO figure this out
* Support typos or slight mispellings of regions
* Support state abbreviations (i.e. LA finds Louisiana)
* I want to create an email service using the same scraping service for Live COVID updates. Users can sign up for how often they want updates (once a day? real-time?) and for the regions that affect them the most (i.e. local, state, country) as well as family or friends that reside in different regions.


# Acknowledgements
I was inspired by this blog post: [How To Track Coronavirus In Your Country with Python](https://towardsdatascience.com/how-to-track-coronavirus-with-python-a5320b778c8e) 
