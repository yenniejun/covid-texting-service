import time
from flask import Flask, request, session
from twilio.twiml.messaging_response import MessagingResponse
import requests
import string
import re
import json
import entity_names as en

bing_json = {}
starttime = time.time()

app = Flask(__name__)
app.config.from_object(__name__)


def get_bing_json():
	print("GETTING DATA!")
	starttime=time.time()
	return {'time': starttime}

	# bing_json = requests.get(url = "https://covidtracking.com/api/counties")#"https://bing.com/covid/data")   

@app.route("/sms", methods=['GET', 'POST'])
def incoming_sms():
    """ Get the incoming message the user sent our Twilio number """
    resp = MessagingResponse()

    global bing_json
    global starttime

    if not bing_json:
    	print("Initial get bing json")
    	bing_json = get_bing_json()

    print("LAST UPDATED: time diff", time.time() - starttime / 60)

    # TODO: This must be 1 hour, not 1 minute ... so 3600
    if time.time() - starttime > 60:
    	bing_json = get_bing_json()

    body = request.values.get('Body', None)

    resp.message("HUNGRY" + body)
    return str(resp)

if __name__ == "__main__":
    app.run(debug=True)


