from flask import Flask, request, session
from twilio.twiml.messaging_response import MessagingResponse
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

app = Flask(__name__)
app.config.from_object(__name__)

source_reply = "The answers for your questions come from creditable sources such as the CDC, WHO, and FDA. The stats come from Worldometers and New York Times."

generic_message = "Ask any question related to COVID-19. For example: What is coronavirus? \n\nTo get the most recent stats, text the name of a location. For example: Cases in New York\n\nText TOTAL to get global stats\n\nText SOURCE to know where the information comes from\n\nText FEEDBACK with a message to leave feedback"
    # generic_message_no_cases = "Ask any question related to COVID-19. For example: What is coronavirus?\n\nText SOURCE to know where the information comes from\n\nText FEEDBACK with a message to leave feedback"


@app.route("/sms", methods=['GET', 'POST'])
def incoming_sms():
    """ Get the incoming message the user sent our Twilio number """
    resp = MessagingResponse()
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

    elif search_term == "source":
        logger.debug("SOURCE")
        resp.message(source_reply)

    elif search_term == "time":
        logger.debug("TIME")
        time = cases.get_last_refreshed_time()
        resp.message(time)

    elif search_term.split() and search_term.split()[0] == "feedback":
        # Write to a file
        logger.info("FEEDBACK: {0}".format(search_term))
        resp.message("Thank you for your feedback!")

    elif search_term == "total":
        total_cases = cases.get_total_cases()
        resp.message(total_cases)

    elif "cases in" in search_term:
        regexp = re.compile("cases in(.*)$")
        case_search = regexp.search(search_term).group(1)

        logger.debug("CASES Searching for cases in: {0}".format(case_search))
        result = cases.handle_cases(utility.clean_text(case_search))
        resp.message(result)

    # ask a question
    else:
        result = bot.handle_query(search_term)
        logger.debug(f"Returning answer to question: {' '.join(result.split())}")
        resp.message(result)

    return str(resp)


if __name__ == "__main__":
    app.run(debug=True)


