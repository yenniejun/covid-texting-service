import requests
import string
import re
import json
import pandas as pd
import time
import entity_names as en
import utility
import logging
import random

logFormatter = '%(asctime)s - %(levelname)s -` %(message)s'
logging.basicConfig(
    level=logging.NOTSET,
    format=logFormatter, 
    handlers=[logging.StreamHandler()])
logging.root.setLevel(logging.NOTSET)
logger = logging.getLogger(__name__)

apology_message = "Sorry, we are unable to support that query.\nPlease specify the name of a US county/parish, US state, or global country.\nFor example: Cases in New York"

# Worldometers
world_data = {}
state_data = {}

# NYT 
local_data = pd.DataFrame([])

starttime = time.time()

def format_response_for_cases(json_object): 
    if json_object == "":
        return ("")

    if '!!!' in json_object:
        return json_object['!!!']
    
    displayName = json_object["displayName"]

    if type(json_object["totalConfirmed"]) != str:
        confirmed = utility.format_num(json_object["totalConfirmed"])
        deaths = utility.format_num(json_object["totalDeaths"])
        recovered = utility.format_num(json_object["totalRecovered"])
    else:
        confirmed = json_object["totalConfirmed"]
        deaths = json_object["totalDeaths"]
        recovered = json_object["totalRecovered"]

    return ("Cases in {0}: \n{1} confirmed\n{2} recovered\n{3} deaths".
        format(displayName, confirmed, recovered, deaths))

def fetch_data():
    global starttime
    global world_data
    global state_data
    global local_data

    if time.time() - starttime < 3600 and world_data and state_data and not local_data.empty:
        return

    logger.info("Fetching new data... it has been {0} seconds".format(time.time() - starttime))
    starttime=time.time()

    # Global data
    req_world = requests.get(url = "https://covid19-server.chrismichael.now.sh/api/v1/AllReports") 
    logger.info(f"Request Covid19-server World Json Response Code: {req_world.status_code}")
    
    if req_world.status_code == 200:
        world_data = req_world.json()
    else:
        logger.error(f"Response code for World Covid19-server is {req_world.status_code}")

    # US State data
    req_usa = requests.get(url="https://covid19-server.chrismichael.now.sh/api/v1/CasesInAllUSStates")
    logger.info(f"Request Covid19-server US State Json Response Code: {req_usa.status_code}")

    if req_usa.status_code == 200:
        state_data = req_usa.json()
    else:
        logger.error(f"Response code for USA State Covid19-server is {req_usa.status_code}")

    # Local data
    local_data = pd.read_csv('https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties.csv')


def get_last_refreshed_time():
    sec_since_refresh = time.time() - starttime
    logger.debug("TIME: {0} ... starttime: {1}".format(time.time(), starttime))
    if sec_since_refresh < 120:
        return("The numbers were last refreshed {0} seconds ago".format(round(sec_since_refresh)))
    else:
        return("The numbers were last refreshed {0} minutes ago".format(round(sec_since_refresh/60)))

def get_total_cases():
    fetch_data()
    if (not world_data):
        logger.error("No world data is available to fetch...")
        return(apology_message)

    global_stats = world_data['reports'][0]

    logger.debug(f"TOTAL cases for the world from covid19server {global_stats['cases']}")

    return(utility.format_total_cases({
        'totalConfirmed':global_stats['cases'],
        'totalRecovered': global_stats['recovered'],
        'totalDeaths':global_stats['deaths']}))


def get_state_name_for_county_query(query):
    my_state=''
    my_county=query

    # Special case for state names that are two words long
    for s in en.two_name_states:
        last_two_words = ' '.join(query.rsplit(' ',2)[-2:])
        if s in last_two_words:
            splitted = query.rsplit(' ',2)
            my_county = splitted[0]
            my_state = ' '.join(splitted[-2:])
            return (my_county, my_state)
            
    splitted = query.rsplit(' ',1)
            
    # For normal states that are one word long
    if len(splitted) == 2:
        if splitted[1].lower() in en.us_states_l:
            my_state = query.rsplit(' ',1)[1]
            my_county = query.rsplit(' ',1)[0]

    logger.debug(f"get_state_name_for_county_query: my county {my_county}, my state {my_state}")
    return my_county, my_state


def get_county(search_term):
    query = ' '.join([word for word in search_term.split() if word.lower() not in ["parish", "county", "borough"]])
    my_county, my_state = get_state_name_for_county_query(query)

    logger.info("Searching for county {0} in state {1}".format(my_county, my_state))

    counties = local_data[local_data.county.str.lower().str.contains(my_county)].sort_values(by='date', ascending=False)

    if len(counties) > 0:
        counties = counties[counties['date'] == counties.iloc[0].date]
        if my_state != '': counties = counties[counties['state'].str.lower() == my_state]
        if len(counties) > 1:
            logger.debug(f"There are {len(counties)} counties with the name {my_county} ... Please try again")
            ret_msg = "Please specify the state. \nFor example: Cases in {0}, {1}".format(counties.iloc[0].county, counties.iloc[0].state) 
        else:
            logger.debug(f"Found stats for the county {my_county}")
            ret_msg = "Cases in {0}, {1}:\n{2} confirmed\n{3} deaths".format(counties.iloc[0].county, 
                counties.iloc[0].state,
                utility.format_num(counties.iloc[0].cases),
                utility.format_num(counties.iloc[0].deaths))
    else:
        logger.warning(f"Invalid cases search, returning message: {' '.join(ret_mes.split())}")
        ret_mes = apology_message

    return ret_msg



def handle_cases(search_term):

    fetch_data()

    if (len(search_term.split()) < 1):
        logger.debug("CASES search term is empty. Returning early")
        return(apology_message)

    logger.debug(f"In handle cases. Looking for {search_term}")

    ### Special Cases ######################################
    if ("china" in search_term):
        search_term = "china (mainland)"
    if (search_term in ["usa", "us", "america"]):
        search_term = "united states"
    if ("korea" in search_term):
        search_term = "south korea"
    ########################################################

    if search_term in en.countries_worldometer:
        my_country = ''
        for country in world_data['reports'][0]['table'][0]:
            if utility.clean_text(country['Country']) == search_term:
                my_country = country
                break

        if my_country == '':
            # Maybe if the country code changes in the API and what I have
            logger.warning("Could not find country for some reason...")
            return (apology_message)

        logger.debug(f"Found number of cases for {my_country['Country']}")

        obj = {"totalConfirmed": my_country['TotalCases'],
               "totalRecovered": my_country['TotalRecovered'],
               "totalDeaths": my_country['TotalDeaths'],
               "displayName": my_country['Country']}

        return format_response_for_cases(obj)
    
    # Total for each US state
    elif search_term in en.us_states_worldometer:   
        mystate = ''
        for state in state_data['data'][0]['table']:   
            if utility.clean_text(state['USAState']) == search_term:
                my_state = state
                break

        if my_state == '':
            # Maybe if the country code changes in the API and what I have
            logger.warning("Could not find state for some reason...")
            return (apology_message)

        logger.debug(f"Found number of cases for {my_state['USAState']}")

        obj = {"totalConfirmed": my_state['TotalCases'],
               "totalRecovered": 0,
               "totalDeaths": my_state['TotalDeaths'],
               "displayName": my_state['USAState']}

        return(format_response_for_cases(obj))    

    else:
        my_county = get_county(search_term) 
        return(my_county)

