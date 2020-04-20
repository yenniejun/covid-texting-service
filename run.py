from flask import Flask, request, session
from twilio.twiml.messaging_response import MessagingResponse
import requests
import string
import re
import json
import entity_names as en
import time


generic_message = "To get the most recent COVID-19 stats, text the name of a US county/parish/borough, US state, or global country.\n\nText TOTAL to get the stats for the world.\n\nText SOURCE to know where the numbers come from.\n\nText TIME to know when the numbers were last refreshed."
bing_json = {}
starttime = time.time()

def clean_text(txt):
    return ''.join(txt.lower().strip().replace(".","").replace(",",""))

# https://stackoverflow.com/questions/1823058/how-to-print-number-with-commas-as-thousands-separators
# 123,456,789
def format_num(num):
    if num != None: return f'{num:,}'
    else: return num

def format_response_for_cases(json_object): 
    if json_object == "":
        return generic_message

    if '!!!' in json_object:
        return json_object['!!!']
    
    displayName = json_object["displayName"]
    confirmed = format_num(json_object["totalConfirmed"])
    deaths = format_num(json_object["totalDeaths"])
    recovered = format_num(json_object["totalRecovered"])

    parent_name = get_state_name_from_county_parent_id(json_object['parentId'])
    print("PARENT", parent_name)

    if any([a in displayName for a in ['Parish', 'County', 'Borough', 'City']]):
        displayName = displayName + ', ' + parent_name

    return ("Cases in {0}: \n{1} confirmed \n{2} recovered \n{3} deaths".
        format(displayName, confirmed, recovered, deaths))

def get_state_name_from_county_parent_id(parentId):
    parentName = parentId.split('_')[0].capitalize()
    sep = ["West", "South", "New", "North", "Rhode"]

    for s in sep:
        if s in parentName:
            return(s + " " + parentName.split(s)[1].capitalize())

    return parentName

def get_county(search_term, bing_json):
    my_state=''
    print("Searching for county", search_term)
    
    my_state=''
    splitted = search_term.rsplit(' ',1)

    # Special case for state names that are two words long
    if "city" not in search_term:
        for s in en.two_name_states:
            if s in search_term:
                splitted = search_term.rsplit(' ',2)
                search_term = splitted[0]
                my_state = ' '.join(splitted[-2:])

    # For normal states that are one word long
    if len(splitted) == 2:
        if splitted[1].lower() in en.us_states_l:
            my_state = search_term.rsplit(' ',1)[1]
            search_term = search_term.rsplit(' ',1)[0]

    print("For county:", my_state, search_term)
            
    matching_counties_json = []
    
    for country in bing_json.json()['areas']: 
        if country['id'] == "unitedstates":                
            for state in country['areas']:      
                if my_state == '' or my_state in state['displayName'].lower():
                    
                    for county in state['areas']:
                        if (search_term in clean_text(county['displayName'])) and (county['totalConfirmed']):
                            print(county['displayName'], "--", state['displayName'])

                            if "City" in county['displayName']:
                                if search_term == county['displayName'].lower():
                                    print('Found CITY special case', county['displayName'], county['totalConfirmed'])
                                    return county

                            else:
                                matching_counties_json.append(county)
    
    if (len(matching_counties_json) == 0):
        return('')
    elif (len(matching_counties_json) == 1):
        print('Found county:', matching_counties_json[0]['displayName'])
        return(matching_counties_json[0])
    elif len(matching_counties_json) > 1 and my_state == '':
        sample_state = get_state_name_from_county_parent_id(matching_counties_json[0]['parentId'])
        ret_msg = "Please specify the state. \nFor example: {0}, {1}".format(matching_counties_json[0]['displayName'], sample_state) 
        return({"!!!": ret_msg})
    else:
        return('')   
            

def get_bing_json():
    global starttime
    print("Fetching new data... it has been {0} seconds".format(time.time() - starttime), )
    starttime=time.time()
    return requests.get(url = "https://bing.com/covid/data") 

app = Flask(__name__)
app.config.from_object(__name__)


@app.route("/sms", methods=['GET', 'POST'])
def incoming_sms():
    """ Get the incoming message the user sent our Twilio number """
    resp = MessagingResponse()

    global bing_json

    # Fetching every 30 minutes or 1800 seconds
    if not bing_json or time.time() - starttime > 1800:
        bing_json = get_bing_json()

    body = request.values.get('Body', None)

    if (body is None):
        resp.message("THERE IS NO BODY!!! IS IT A ZOMBIE?")
        return str(resp)

    search_term = clean_text(body)
    print(search_term)

    # bing_json = requests.get(url = "https://bing.com/covid/data")   

    ### Special Cases ######################################
    if ("china" in search_term):
        search_term = "china (mainland)"
    if (search_term in ["usa", "us"]):
        search_term = "united states"
    ########################################################

    if search_term == "source":
         resp.message("For more information on where the data comes from, go to {0}".
            format("https://bing.com/covid"))

    elif search_term == "time":
        sec_since_refresh = time.time() - starttime
        if sec_since_refresh < 120:
            resp.message("The numbers were last refreshed {0} seconds ago".format(round(sec_since_refresh)))
        else:
            resp.message("The numbers were last refreshed {0} minutes ago".format(round(sec_since_refresh/60)))


    # helpful message
    elif search_term in ["hello", "hi", "yo", "corona", "covid", "covid-19", "covid19"]:
        resp.message(generic_message)
        return str(resp)

    # global
    elif search_term in ["total", "global", "world"]:
        # report = requests.get(url = "https://covid19-server.chrismichael.now.sh/api/v1/AllReports") 
        # global_stats = report.json()['reports'][0]

        resp.message("Total cases in the world: \n {0} confirmed \n {1} recovered \n {2} deaths".
            format(
                format_num(bing_json.json()['totalConfirmed']),
                format_num(bing_json.json()['totalRecovered']),
                format_num(bing_json.json()['totalDeaths'])))
#                global_stats['active_cases'][0]['currently_infected_patients']))

     # Total for each country
    elif search_term in en.countries_l:  
        mycountry = ""

        for country in bing_json.json()['areas']:   
            if search_term in clean_text(country['displayName']):    
                mycountry = country 
                break

        print ("found country:", country['id'], country['displayName'], country['totalConfirmed'])
        resp.message(format_response_for_cases(mycountry))  

    # Total for each US state
    elif search_term in en.us_states_l:        
        mystate = ""    

        for country in bing_json.json()['areas']:   
            if country['id'] == "unitedstates": 
                for state in country['areas']:
                    if search_term in clean_text(state['displayName']):
                        mystate = state
                        break

        print ("found state:", state['id'], state['displayName'], state['totalConfirmed'])
        resp.message(format_response_for_cases(mystate))    

    # Gets the total for each county
    else: 
        mycounty = get_county(search_term, bing_json) 
        resp.message(format_response_for_cases(mycounty))

    # else:
        # resp.message(generic_message)

    return str(resp)


if __name__ == "__main__":
    app.run(debug=True)


