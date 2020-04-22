import requests
import string
import re
import json
import entity_names as en
import utility
import logging

logFormatter = '%(asctime)s - %(levelname)s - %(message)s'
logging.basicConfig(
    level=logging.NOTSET,
    format=logFormatter, 
    handlers=[logging.StreamHandler()])
logging.root.setLevel(logging.NOTSET)
logger = logging.getLogger(__name__)

def format_response_for_cases(json_object): 
    if json_object == "":
        return ("")

    if '!!!' in json_object:
        return json_object['!!!']
    
    displayName = json_object["displayName"]
    confirmed = utility.format_num(json_object["totalConfirmed"])
    deaths = utility.format_num(json_object["totalDeaths"])
    recovered = utility.format_num(json_object["totalRecovered"])

    parent_name = get_state_name_from_county_parent_id(json_object['parentId'])
    logger.debug(f"PARENT: {parent_name}")

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

    logger.info("Searching for county {0} in state {1}".format(search_term, my_state))
            
    matching_counties_json = []
    
    for country in bing_json.json()['areas']: 
        if country['id'] == "unitedstates":                
            for state in country['areas']:      
                if my_state == '' or my_state in state['displayName'].lower():
                    
                    for county in state['areas']:
                        if (search_term in utility.clean_text(county['displayName'])) and (county['totalConfirmed']):
                            logger.debug(f"{county['displayName']}, {state['displayName']}")

                            if "City" in county['displayName']:
                                if search_term == county['displayName'].lower():
                                    logger.debug(f"Found CITY special case: {county['displayName']}")
                                    return county

                            else:
                                matching_counties_json.append(county)
    
    if (len(matching_counties_json) == 0):
        return('')
    elif (len(matching_counties_json) == 1):
        logger.info(f"Found county: {matching_counties_json[0]['displayName']}")
        return(matching_counties_json[0])
    elif len(matching_counties_json) > 1 and my_state == '':
        sample_state = get_state_name_from_county_parent_id(matching_counties_json[0]['parentId'])
        ret_msg = "Please specify the state. \nFor example: Cases in {0}, {1}".format(matching_counties_json[0]['displayName'], sample_state) 
        logger.warning(f"Unable to find one specific county for search term {search_term}")
        return({"!!!": ret_msg})
    else:
        logger.warning(f"Unable to find any matching county for search term {search_term}")
        return('')   


def handle_cases(search_term, bing_json):

    if (len(search_term.split()) < 1):
        logger.debug("CASES search term is empty. Returning early")
        return('')

    logger.debug(f"In handle cases. Looking for {search_term}")

    ### Special Cases ######################################
    if ("china" in search_term):
        search_term = "china (mainland)"
    if (search_term in ["usa", "us", "america"]):
        search_term = "united states"
    if ("korea" in search_term):
        search_term = "south korea"
    ########################################################
    
     # Total for each country
    if search_term in en.countries_l:  
        mycountry = ""

        for country in bing_json.json()['areas']:   
            if search_term in utility.clean_text(country['displayName']):    
                mycountry = country 
                break

        logger.info(f"found country with id: {country['id']}, name: {country['displayName']}, confirmed: {country['totalConfirmed']}")
        return(format_response_for_cases(mycountry))  

    # Total for each US state
    elif search_term in en.us_states_l:        
        mystate = ""    

        for country in bing_json.json()['areas']:   
            if country['id'] == "unitedstates": 
                for state in country['areas']:
                    if search_term in utility.clean_text(state['displayName']):
                        mystate = state
                        break

        logger.info(f"found state with id: {state['id']}, name: {state['displayName']}, confirmed: {state['totalConfirmed']}")
        return(format_response_for_cases(mystate))    

    # Gets the total for each county
    else: 
        mycounty = get_county(search_term, bing_json) 
        return(format_response_for_cases(mycounty))

