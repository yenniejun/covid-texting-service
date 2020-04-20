# Texting Service for COVID-19 Stats

This is a texting service that allows you stay updated on the COVID-19 statistics for your region.

You can query the latest coronavirus statistics on cases (confirmed, recovered, and deaths) at a global-level, country-level, US state-level, or US county-level (i.e. county, borough, or parish).

_             |  _
:-------------------------:|:-------------------------:
![](/img/text_screenshot_1.png)  |  ![](/img/text_screenshot_2.png)

# About the Project

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

I am pulling my data from the [Bing API Portal](https://bing.com/covid). You can find the details about the api [here](https://www.programmableweb.com/api/bing-covid-19-data-rest-api-v10). You can find the API endpoint [here](https://bing.com/covid/data). 

I tried out several different coronavirus API endpoints and scraping different sites myself. Of all of these, I found that the Bing API provided the most accurate, up-to-date, and easiest-to-use stats.



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






