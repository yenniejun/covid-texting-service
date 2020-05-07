# Texting Service for COVID-19

This is a texting service that provide basic statistics and basic question-answering functionality about COVID-19.  

_             |  _
:-------------------------:|:-------------------------:
![](/img/text_screenshot_1.png)  |  ![](/img/text_screenshot_2.png)

# About the Project
This project is a texting service initially built for those without Internet access to get information about the coronavirus (COVID-19) pandemic. The service provides the latest coronavirus statistics (confirmed, recovered, and deaths) at a global-level, country-level, US state-level, or US county-level (i.e. county, borough, or parish). It also answers basic coronavirus-related questions (for example, about protection, symptoms, quarantine, etc)

To test it out, text "HELLO" to the test number at +1781-524-3409.


## Built With
* [Twilio](https://www.twilio.com/)
* [Flask](https://palletsprojects.com/p/flask/)
* [Heroku](https://devcenter.heroku.com/articles/getting-started-with-python)

## Why Texting Service?

The reason I created a texting service is to ensure that even those without Internet can access the latest stats on COVID in their region. There are currently a lot of numbers and resources on many different websites, but they are not accessible to those without Internet access. 

According to a [2019 Pew Research survey](https://www.pewresearch.org/fact-tank/2019/04/22/some-americans-dont-use-the-internet-who-are-they/), 10% of Americans (nearly 33 million people) do not use the Internet. In [Louisiana](https://broadbandnow.com/Louisiana), over 400,000 people do not have access to a wired connection capable of 25mbps download speeds, and 262,000 people do not have any wired Internet providers available where they live. 

However, most people have texting, and a service like this would make it easier to access the most up-to-date COVID numbers for the areas that you care most about - at the state level as well as at the local (parish) level.

Note: Louisiana currently has a texting service (text LACOVID to 898211), but it focuses more on recent state-wide announcements, and often contains links, which may not be accessible to those without Internet connection. Further, it doesn't tell you the most up-to-date numbers on COVID in your region, which is very pertinent residents as you increasingly self-quarantine.


## Stats
`cases.py`

I am getting my stats from a few sources.

World & Country Level:
* [COVID19 Real-Time Data REST API v1.0](https://github.com/ChrisMichaelPerezSantiago/covid19) built by Chris Michael. You can reach the API endpoint [here](https://covid19-server.chrismichael.now.sh/api/v1). More details [here](https://www.programmableweb.com/api/covid19-real-time-data-rest-api-v10).

US State Level:
* [Corona Tracking Project](https://covidtracking.com/api)

US Local level:
* [New York Times](https://github.com/nytimes/covid-19-data)

To ensure I do not get throttled, I am pulling every hour (3600 seconds). 

## Q&A
`bot.py`

I am scraping my answers from the "Frequently Asked Questions" sections from the following sites:
* [WHO]('https://www.who.int/news-room/q-a-detail/q-a-coronaviruses')
* [CDC]('https://www.cdc.gov/coronavirus/2019-ncov/faq.html')
* [FDA]('https://www.fda.gov/emergency-preparedness-and-response/coronavirus-disease-2019-covid-19/coronavirus-disease-2019-covid-19-frequently-asked-questions'
)

Then, I am doing some *very* preliminary question-answer matching. Eventually I'd like to build a model, but for now, I'm just using heuristics:
* string similarity (Levenshtein)
* cosine similarity
* keyword matching

**Note**
This is a very preliminary version of Q&A. I realize there are a lot of messy manual matching and heuristic decisions being made.


_             |  _
:-------------------------:|:-------------------------:
![](/img/text_screenshot_3.png)  |  ![](/img/text_screenshot_4.png)


# Getting Started

To set up this service locally, you will need to set up the twilio service and the Flask framework.

1. Clone the repo: 

```git clone https://github.com/yenniejun/covid-texting-service.git```

2. Install twilio
```
npm install twilio-cli -g
pip install twilio
```

3. Download and setup [ngrok](https://ngrok.com/download) (For running locally)

4. Install and activate [virtual environment](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)
```
pip install virtualenv
python3 -m venv env
source venv/bin/activate
```
Once you have virtual environment set up, install the dependencies
```
venv/bin/pip install -r requirements.txt
```
<br/>

<b>Note</b>: I would recommend following the set-up steps in the [twilio tutorial](https://www.twilio.com/docs/sms/quickstart/python-msg-svc). This will help you get a phone number, connect the number with the local backend, and to setup ngrok. In this process, you will install twilio, flask, and other required libraries.


# Usage

## Locally
To run locally, run the following twilio-cli command in the terminal. This will run [ngrok](https://ngrok.com/) and expose the service to the Internet. 

`twilio phone-numbers:update "+1xxxxxxxxxx" --sms-url="http://localhost:5000/sms"
`

If this doesn't work, you can also run the ngrok tunnel directly
```
ngrok http 5000
```

If you do this, make sure you note the forwarding URL (`https://<something>.ngrok.io`) and paste `https://<something>.ngrok.io/sms` into the Twilio Webhook console.

Open another terminal window and run the Flask application.

`
python3 run.py
`


ngrok             |  flask
:-------------------------:|:-------------------------:
![](/img/ngrok.png)  |  ![](/img/runpy.png)


Text "HELLO" from your phone to the phone number to get started. 

Debug statements will show up on the Terminal window running the application.
To turn off debug statements, locate the following line in `run.py` and set `debug=False`
```
if __name__ == "__main__":
    app.run(debug=True)
```


## Deployment
Make sure to log onto the [Twilio console](https://www.twilio.com/) -> Phone numbers -> click your phone number -> Messaging. Make sure for "A Message Comes In", "Webhook" is selected in the dropdown.
![](/img/twilio_console.png) 



# Looking Forward
* Investigate more accurate source of stats - currently am pulling from Bing API, which seems to be the most accurate one I've found so far.
* Allow a more robust search that supports typos or slight mispellings of regions 
* Support state abbreviations (i.e. LA finds Louisiana)
* Provide useful (but concise) information about COVID (keeping in mind that the target of this service is for people without internet)
* Create an email service using the same scraping service for Live COVID updates. Users can sign up for how often they want updates (once a day? real-time?) and for the regions that affect them the most (i.e. local, state, country) as well as family or friends that reside in different regions.


# Resources
* [Worldometers](https://www.worldometers.info/coronavirus/country/us/) 
* [Bing API](https://bing.com/covid/data)
* [COVID19 Real-Time Data REST API v1.0](https://github.com/ChrisMichaelPerezSantiago/covid19) built by Chris Michael. You can reach the API endpoint [here](https://covid19-server.chrismichael.now.sh/api/v1). More details [here](https://www.programmableweb.com/api/covid19-real-time-data-rest-api-v10).
* [ProgrammableWeb](https://www.programmableweb.com/news/apis-to-track-coronavirus-covid-19/review/2020/03/27) lists various different APIs that are currently tracking COVID-19 numbers across the world
* [Covid Tracking Project](https://covidtracking.com/)
* [Corona Data Scraper](https://coronadatascraper.com/#home)
* [Covid19api](https://covid19api.com/)
* [NYT](https://github.com/nytimes/covid-19-data)
* [Covid Tracking](https://covidtracking.com/) (The Atlantic)


# Acknowledgements
* I was inspired by this blog post: [How To Track Coronavirus In Your Country with Python](https://towardsdatascience.com/how-to-track-coronavirus-with-python-a5320b778c8e) 
* [Bing API](https://bing.com/covid/data)






