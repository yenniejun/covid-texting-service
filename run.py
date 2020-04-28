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

generic_message = "Welcome to COVID-19 Information Service. Text one of the following for instructions:\n\nQUESTION\nCASES\nSOURCE\nFEEDBACK"

# generic_message = "Text QUESTION to ask something about COVID-19. \n\nText CASES to get the most recent stats.\n\nText SOURCE to know where the info comes from\n\nText FEEDBACK with a message"
    # generic_message_no_cases = "Ask any question related to COVID-19. For example: What is coronavirus?\n\nText SOURCE to know where the information comes from\n\nText FEEDBACK with a message to leave feedback"


@app.route("/sms", methods=['GET', 'POST'])
def incoming_sms():
    """ Get the incoming message the user sent our Twilio number """
    resp = MessagingResponse()
    response_text = ''

    is_get_request = False

    print(request.args)

    if 'from' in request.args:
        is_get_request = True
        logging.info("Servicing a GET request")
        arg_from = request.args.get('from')
        body = request.args.get('message')
        logging.debug(f"Message phone number from: {arg_from}, message: {body}")
    else:
        logging.info("Servicing a POST request")
        body = request.values.get('Body', None)

    if (body is None):
        # print("RESP", resp)
        logging.error("There is no body. What is happening?")
        resp.message("THERE IS NO BODY!!! IS IT A ZOMBIE?")
        return str(resp)

    search_term = utility.clean_text(body)
    logger.info(f"Search term: {search_term}")

     # helpful message
    if len(search_term) < 1 or search_term == "hello" or search_term == "info":
        response_text = generic_message

    elif search_term == "source":
        logger.debug("SOURCE")
        response_text = source_reply

    elif search_term == "time":
        logger.debug("TIME")
        time = cases.get_last_refreshed_time()
        response_text = time

    elif search_term == "feedback":
        response_text = "Please text FEEDBACK followed by whatever message you would like to leave"

    elif search_term.split() and search_term.split()[0] == "feedback":
        # Write to a file
        logger.info("FEEDBACK: {0}".format(search_term))
        response_text = "Thank you for your feedback!"

    elif search_term == "total":
        total_cases = cases.get_total_cases()
        response_text = total_cases

    elif search_term == "cases":
        response_text = "Please specify the name of a US county/parish, US state, or global country.\n\nFor example: Cases in New York\n\nText TOTAL to get global stats"

    elif "cases in" in search_term:
        regexp = re.compile("cases in(.*)$")
        case_search = regexp.search(search_term).group(1)

        logger.debug("CASES Searching for cases in: {0}".format(case_search))
        result = cases.handle_cases(utility.clean_text(case_search))
        response_text = result

    # ask a question
    else:
        result = bot.handle_query(search_term)
        logger.debug(f"Returning answer to question: {' '.join(result.split())}")
        response_text = result


    if is_get_request:
        return response_text
    else:
        resp.message(response_text)
        return str(resp)


if __name__ == "__main__":
    app.run(debug=True)


