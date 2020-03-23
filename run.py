from flask import Flask, request, session
from twilio.twiml.messaging_response import MessagingResponse
import corona
import string
import re
import pandas as pd

# hard coded for now ... ¯\_(ツ)_/¯
louisiana_parishes = ['orleans', 'jefferson', 'catahoula', 'st.james', 'st.tammany', 'eastbatonrouge', 'ascension', 'caddo', 'st.bernard', 'lafourche', 'terrebonne', 'parishunderinvestigation', 'st.johnthebaptist', 'st.charles', 'lafayette', 'bossier', 'plaquemines', 'calcasieu', 'ouachita', 'rapides', 'st.landry', 'tangipahoa', 'westbatonrouge', 'desoto', 'evangeline', 'iberia', 'iberville', 'livingston', 'washington', 'acadia', 'assumption', 'avoyelles', 'beauregard', 'bienville', 'claiborne', 'st.mary', 'webster', 'allen', 'caldwell', 'cameron', 'concordia', 'eastcarroll', 'eastfeliciana', 'franklin', 'grant', 'jackson', 'jeffersondavis', 'lasalle', 'lincoln', 'madison', 'morehouse', 'natchitoches', 'pointecoupee', 'redriver', 'richland', 'sabine', 'st.helena', 'st.martin', 'tensas', 'union', 'vermilion', 'vernon', 'westcarroll', 'westfeliciana', 'winn']
us_states = ['newyork', 'washington', 'newjersey', 'california', 'illinois', 'michigan', 'florida', 'louisiana', 'massachusetts', 'georgia', 'texas', 'colorado', 'tennessee', 'pennsylvania', 'wisconsin', 'ohio', 'northcarolina', 'maryland', 'connecticut', 'virginia', 'mississippi', 'indiana', 'southcarolina', 'nevada', 'utah', 'minnesota', 'arkansas', 'oregon', 'alabama', 'arizona', 'kentucky', 'districtofcolumbia', 'missouri', 'iowa', 'maine', 'rhodeisland', 'newhampshire', 'oklahoma', 'newmexico', 'kansas', 'delaware', 'hawaii', 'vermont', 'idaho', 'nebraska', 'montana', 'northdakota', 'wyoming', 'alaska', 'southdakota', 'westvirginia', 'diamondprincesscruise', 'grandprincesscruise']

bot_la = corona.get_louisiana_bot()
bot_us = corona.get_us_bot()

app = Flask(__name__)
app.config.from_object(__name__)


@app.route("/sms", methods=['GET', 'POST'])
def incoming_sms():
    """ Get the incoming message the user sent our Twilio number """
    body = request.values.get('Body', None)
    stripped_body = corona.clean_text(body)
    print(stripped_body)

    resp = MessagingResponse()

    if stripped_body == "source":
        us = 'https://www.worldometers.info/coronavirus/country/us/'
        la = 'http://ldh.la.gov/Coronavirus/'
        resp.message("For more info on Louisiana stats, go to {0}. \n\nFor more info on US stats, go to {1}".format(la,us))

    # Gets the total for the US
    elif stripped_body in ["total", "all", "usa", "us", "united states"]:
        total_row = corona.get_us_state(bot_us, '<strong>total:</strong>', is_total = True)
        total_cases = total_row.TotalCases.values[0]
        new_cases = total_row.NewCases.values[0] or 0
        total_deaths = total_row.TotalDeaths.values[0]
        new_deaths = total_row.NewDeaths.values[0] or 0
        resp.message("Total cases in the US: {0} cases ({1} new) and {2} deaths ({3} new)".
            format(total_cases, new_cases, total_deaths, new_deaths))

    # Gets the total for each state
    elif stripped_body in us_states:
        state = corona.get_us_state(bot_us, stripped_body, is_total = False)
        state_name = state.State.values[0]
        total_cases = state.TotalCases.values[0]
        new_cases = state.NewCases.values[0] or 0
        total_deaths = state.TotalDeaths.values[0]
        new_deaths = state.NewDeaths.values[0] or 0

        if new_cases == "" and new_deaths == "":
           resp.message("{0} has {1} cases and {2} deaths".
                format(state_name, total_cases, total_deaths))
        else:
            resp.message("{0} has {1} cases ({2} new) and {3} deaths ({4} new)".
                format(state_name, total_cases, new_cases, total_deaths, new_deaths))

    # Gets the total for each Louisiana parish
    elif stripped_body in louisiana_parishes:
        parish = corona.get_parish(bot_la, stripped_body)
        cases = parish.Cases.values[0]
        deaths = parish.Deaths.values[0]
        resp.message("{0} Parish has {1} cases and {2} deaths".format(parish.Parish.values[0], cases, deaths))

    else:
        resp.message("To get the most recent COVID-19 stats, text the name of a Louisiana parish or a US State. \n\nText TOTAL to get the stats for the entire country. \n\nText SOURCE to know where the numbers come from.")

    return str(resp)


if __name__ == "__main__":
    app.run(debug=True)


