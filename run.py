from flask import Flask, request, session
from twilio.twiml.messaging_response import MessagingResponse
import time
import requests
import re
import logging
import utility
import cases
import bot

logFormatter = '%(asctime)s - %(levelname)s - %(message)s'
logging.basicConfig(
    level=logging.NOTSET,
    format=logFormatter, 
    handlers=[logging.StreamHandler()])
logging.root.setLevel(logging.NOTSET)
logger = logging.getLogger(__name__)


bing_json = {}
starttime = 0

      
def get_bing_json():
    global starttime
    logger.info("Fetching new BING data... it has been {0} seconds".format(time.time() - starttime), )
    starttime=time.time()
    response = requests.get(url = "https://bing.com/covid/data")
    logger.info(f"Request Bing Json Response Code: {response.status_code}")
    return response

app = Flask(__name__)
app.config.from_object(__name__)


generic_message = "Ask any question related to COVID-19. For example: 'What is coronavirus?' \n\nTo get the most recent stats, text the name of a location. For example: 'Cases in New York'\n\nText TOTAL to get global stats\n\nText SOURCE to know where the numbers come from\n\nText FEEDBACK with a message to leave feedback."
@app.route("/sms", methods=['GET', 'POST'])
def incoming_sms():
    """ Get the incoming message the user sent our Twilio number """
    resp = MessagingResponse()

    global bing_json

    # Fetching every 1 hour or 3600 seconds
    if not bing_json or time.time() - starttime > 3600:
        bing_json = get_bing_json()

    body = request.values.get('Body', None)

    if (body is None):
        logging.error("There is no body. What is happening?")
        resp.message("THERE IS NO BODY!!! IS IT A ZOMBIE?")
        return str(resp)

    search_term = utility.clean_text(body)
    logger.info(f"Search term: {search_term}")

    # helpful message
    if len(search_term) < 1 or search_term == "hello" or search_term == "info":
        resp.message(generic_message)
        return str(resp)

    elif search_term == "source":
        logger.debug("SOURCE")
        resp.message("For more information on where the data comes from, go to {0}".
            format("https://bing.com/covid"))

    elif search_term == "time":
        sec_since_refresh = time.time() - starttime
        logger.debug("TIME: {0} ... starttime: {1}".format(time.time(), starttime))
        if sec_since_refresh < 120:
            resp.message("The numbers were last refreshed {0} seconds ago".format(round(sec_since_refresh)))
        else:
            resp.message("The numbers were last refreshed {0} minutes ago".format(round(sec_since_refresh/60)))

    elif search_term.split() and search_term.split()[0] == "feedback":
        # Write to a file
        logger.info("FEEDBACK: {0}".format(search_term))
        resp.message("Thank you for your feedback!")
        return str(resp)

    # global
    elif search_term == "total":
        # report = requests.get(url = "https://covid19-server.chrismichael.now.sh/api/v1/AllReports") 
        # global_stats = report.json()['reports'][0]

        logger.debug(f"TOTAL cases for the world {bing_json.json()['totalConfirmed']}")
        resp.message("Total cases in the world: \n {0} confirmed \n {1} recovered \n {2} deaths".
            format(
                utility.format_num(bing_json.json()['totalConfirmed']),
                utility.format_num(bing_json.json()['totalRecovered']),
                utility.format_num(bing_json.json()['totalDeaths'])))
#                global_stats['active_cases'][0]['currently_infected_patients']))

    
    elif "cases in" in search_term:
        regexp = re.compile("cases in(.*)$")
        case_search = regexp.search(search_term).group(1)

        logger.debug("CASES Searching for cases in: {0}".format(case_search))
        result = cases.handle_cases(utility.clean_text(case_search), bing_json)
        
        if len(result) < 1:
            ret_mes = f"Unable to find a location of the name {case_search}.\nPlease specify the name of a US county/parish, US state, or global country.\nFor example: Cases in New York"
            logger.warning(f"Invalid cases search, returning message: {' '.join(ret_mes.split())}")
            result = ret_mes
        else:
          logger.debug("Returning result for cases")

        resp.message(result)

    # ask a question
    else:
        result = bot.handle_query(search_term)
        logger.debug(f"Returning answer to question: {' '.join(result.split())}")
        resp.message(result)

    return str(resp)


if __name__ == "__main__":
    app.run(debug=True)


