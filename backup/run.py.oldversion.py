from flask import Flask, request, session
from twilio.twiml.messaging_response import MessagingResponse
import corona
import string
import re
import pandas as pd

louisiana_parishes = ['orleans', 'jefferson', 'catahoula', 'st.james', 'st.tammany', 'eastbatonrouge', 'ascension', 'caddo', 'st.bernard', 'lafourche', 'terrebonne', 'parishunderinvestigation', 'st.johnthebaptist', 'st.charles', 'lafayette', 'bossier', 'plaquemines', 'calcasieu', 'ouachita', 'rapides', 'st.landry', 'tangipahoa', 'westbatonrouge', 'desoto', 'evangeline', 'iberia', 'iberville', 'livingston', 'washington', 'acadia', 'assumption', 'avoyelles', 'beauregard', 'bienville', 'claiborne', 'st.mary', 'webster', 'allen', 'caldwell', 'cameron', 'concordia', 'eastcarroll', 'eastfeliciana', 'franklin', 'grant', 'jackson', 'jeffersondavis', 'lasalle', 'lincoln', 'madison', 'morehouse', 'natchitoches', 'pointecoupee', 'redriver', 'richland', 'sabine', 'st.helena', 'st.martin', 'tensas', 'union', 'vermilion', 'vernon', 'westcarroll', 'westfeliciana', 'winn']
us_states = ['newyork', 'washington', 'newjersey', 'california', 'illinois', 'michigan', 'florida', 'louisiana', 'massachusetts', 'georgia', 'texas', 'colorado', 'tennessee', 'pennsylvania', 'wisconsin', 'ohio', 'northcarolina', 'maryland', 'connecticut', 'virginia', 'mississippi', 'indiana', 'southcarolina', 'nevada', 'utah', 'minnesota', 'arkansas', 'oregon', 'alabama', 'arizona', 'kentucky', 'districtofcolumbia', 'missouri', 'iowa', 'maine', 'rhodeisland', 'newhampshire', 'oklahoma', 'newmexico', 'kansas', 'delaware', 'hawaii', 'vermont', 'idaho', 'nebraska', 'montana', 'northdakota', 'wyoming', 'alaska', 'southdakota', 'westvirginia', 'diamondprincesscruise', 'grandprincesscruise']

bot_la = corona.get_louisiana_bot()
bot_us = corona.get_us_bot()


# The session object makes use of a secret key.
SECRET_KEY = 'a secret key'
app = Flask(__name__)
app.config.from_object(__name__)

# Try adding your own number to this list!
callers = {
    "+12252840859": "MEEEE",
}


@app.route("/", methods=['GET', 'POST'])
def hello():
    """Respond with the number of text messages sent between two parties."""
    # Increment the counter
    counter = session.get('counter', 0)
    counter += 1

    # Save the new counter value in the session
    session['counter'] = counter

    from_number = request.values.get('From')
    if from_number in callers:
        print("IN CALLERS")
        name = callers[from_number]
    else:
        name = "Friend"

    # Build our reply
    message = '{} has messaged {} {} times.' \
        .format(name, request.values.get('To'), counter)

    # Put it in a TwiML response
    resp = MessagingResponse()
    resp.message(message)

    return str(resp)


def compare_string(parish, input):
    s1.lower().replace(" ","") == s2.lower().replace(" ","")


@app.route("/sms", methods=['GET', 'POST'])
def incoming_sms():
    """Send a dynamic reply to an incoming text message"""
    # Get the message the user sent our Twilio number
    body = request.values.get('Body', None)
    stripped_body = body.lower().replace(" ","")

    resp = MessagingResponse()

    # if stripped_body in us_states:
    #     # state = corona.get_state(stripped_body)
    #     # data = state.text.split(" ")
    #     # data = [i for i in data if 'source' not in i]

    #     df = pd.read_csv('us_states_df.csv')
    #     # df = corona.get_states()
    #     print(df)
    #     df['stripped_state'] = [p.lower().replace(" ", "") for p in df.State.values]
    #     state = df[df.stripped_state == stripped_body]
    #     state_name = state.State.values[0]
    #     total_cases = state.TotalCases.values[0]
    #     new_cases = state.NewCases.values[0]
    #     total_deaths = state.TotalDeaths.values[0]
    #     new_deaths = state.NewDeaths.values[0]
    #     print(new_deaths)
    #     resp.message("{0} has {1} cases ({2} new) and {3} deaths ({4} new)".
    #         format(state_name, total_cases, new_cases, total_deaths, new_deaths))

    print(stripped_body)

    if stripped_body == "total" or stripped_body == "all" or stripped_body in us_states:
        states = bot_us.driver.find_elements_by_xpath("//tbody/tr/td")
        lines = [" ".join(state.get_attribute("innerHTML").split()) for state in states]
        grouped_list = list(corona.grouper(8, lines))
        df = pd.DataFrame(grouped_list).iloc[:,0:5]
        df.columns =['State', 'TotalCases', 'NewCases', 'TotalDeaths', 'NewDeaths']
        totalRow = df[df.State.str.contains('Total')]

        df['stripped_state'] = [p.lower().replace(" ", "") for p in df.State.values]

        if stripped_body == "total" or stripped_body == "all":
            state = df[df.stripped_state == '<strong>total:</strong>']
            total_cases = state.TotalCases.values[0]
            new_cases = state.NewCases.values[0]
            total_deaths = state.TotalDeaths.values[0]
            new_deaths = state.NewDeaths.values[0]
            resp.message("Total cases in the US: {0} cases ({1} new) and {2} deaths ({3} new)".
                format(total_cases, new_cases, total_deaths, new_deaths))

        elif stripped_body in us_states:
            df['stripped_state'] = [p.lower().replace(" ", "") for p in df.State.values]
            state = df[df.stripped_state == stripped_body]
            state_name = state.State.values[0]
            total_cases = state.TotalCases.values[0]
            new_cases = state.NewCases.values[0]
            total_deaths = state.TotalDeaths.values[0]
            new_deaths = state.NewDeaths.values[0]
            print(new_deaths)
            resp.message("{0} has {1} cases ({2} new) and {3} deaths ({4} new)".
                format(state_name, total_cases, new_cases, total_deaths, new_deaths))


        # Louisiana totals
        # totalcase = bot_la.driver.find_element_by_xpath('//*[@id="ember15"]')
        # totalcase = re.match('\d+', totalcase.text).group()
        # totaldead = bot_la.driver.find_element_by_xpath('//*[@id="ember22"]')
        # totaldead = re.match('\d+', totaldead.text).group() 
        # resp.message("Louisiana has {0} total cases and {1} total deaths".format(totalcase, totaldead))               

    # elif stripped_body in us_states:
    #     states = bot_us.driver.find_elements_by_xpath("//tbody/tr/td")
    #     lines = [" ".join(state.get_attribute("innerHTML").split()) for state in states]

    #     grouped_list = list(corona.grouper(8, lines))
    #     df = pd.DataFrame(grouped_list).iloc[:,0:5]
    #     df.columns =['State', 'TotalCases', 'NewCases', 'TotalDeaths', 'NewDeaths']
    #     totalRow = df[df.State.str.contains('Total')]

    #     df['stripped_state'] = [p.lower().replace(" ", "") for p in df.State.values]
    #     state = df[df.stripped_state == stripped_body]
    #     state_name = state.State.values[0]
    #     total_cases = state.TotalCases.values[0]
    #     new_cases = state.NewCases.values[0]
    #     total_deaths = state.TotalDeaths.values[0]
    #     new_deaths = state.NewDeaths.values[0]
    #     print(new_deaths)
    #     resp.message("{0} has {1} cases ({2} new) and {3} deaths ({4} new)".
    #         format(state_name, total_cases, new_cases, total_deaths, new_deaths))


    elif stripped_body in louisiana_parishes:
        lines = bot_la.driver.find_elements_by_xpath('//*[@id="ember56"]/div/nav/span/div/div/p[2]/strong')
        lines = [line.get_attribute("innerHTML") for line in lines]
        grouped_list = list(corona.grouper(3, lines))
        df = pd.DataFrame(grouped_list, columns =['Parish', 'Cases', 'Deaths']) 
        df.reset_index(inplace=True)  

        df['stripped_parish'] = [p.lower().replace(" ", "") for p in df.Parish.values]
        parish = df[df.stripped_parish == stripped_body]
        print(parish)
        cases = parish.Cases.values[0]
        deaths = parish.Deaths.values[0]
        resp.message("{0} Parish has {1} cases and {2} deaths".format(parish.Parish.values[0], cases, deaths))

    # if stripped_body in louisiana_parishes:
    #     df = corona.get_parishes()
    #     # df = pd.read_csv('louisiana_updates_df.csv')

    #     df['stripped_parish'] = [p.lower().replace(" ", "") for p in df.Parish.values]
    #     parish = df[df.stripped_parish == stripped_body]
    #     cases = parish.Cases.values[0]
    #     deaths = parish.Deaths.values[0]
    #     resp.message("{0} Parish has {1} cases and {2} deaths".format(parish.Parish.values[0], cases, deaths))
    else:
        resp.message("To get the most recent COVID-19 stats, text the name of a Louisiana parish or a US State. Text 'total' to get the stats for the entire country.")

        
    return str(resp)



if __name__ == "__main__":
    app.run(debug=True)


