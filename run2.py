### This is the backup with a different API incase Bing API stops working again

from flask import Flask, request, session
from twilio.twiml.messaging_response import MessagingResponse
import requests
import string
import re
import json


# TODO AUTO REFRESH

# hard coded for now ... ¯\_(ツ)_/¯
louisiana_parishes = ['orleans','jefferson','caddo','eastbatonrouge','sttammany','ascension','lafayette','stjohnthebaptist','stjames','bossier','stbernard','lafourche','rapides','ouachita','terrebonne','stcharles','calcasieu','iberville','plaquemines','desoto','livingston','westbatonrouge','avoyelles','stmartin','stlandry','webster','assumption','acadia','washington','tangipahoa','lincoln','stmary','allen','eastfeliciana','beauregard','evangeline','iberia','union','claiborne','jackson','richland','morehouse','natchitoches','vermilion','vernon','catahoula','bienville','pointecoupee','jeffersondavis','grant','madison','lasalle','winn','westfeliciana']
us_states = ['newyork','newjersey','california','michigan','florida','massachusetts','washington','louisiana','illinois','pennsylvania','georgia','texas','colorado','connecticut','ohio','indiana','tennessee','maryland','northcarolina','wisconsin','missouri','arizona','virginia','nevada','alabama','mississippi','southcarolina','utah','minnesota','oregon','oklahoma','arkansas','iowa','districtofcolumbia','kentucky','idaho','kansas','rhodeisland','newhampshire','maine','vermont','newmexico','delaware','hawaii','montana','nebraska','westvirginia','northdakota','alaska','wyoming','southdakota','guam','northernmarianaislands','puertorico','unitedstatesvirginislands','wuhanrepatriated','diamondprincesscruise']
countries = ['usa','italy','spain','germany','france','iran','uk','switzerland','turkey','belgium','netherlands','austria','skorea','canada','portugal','israel','brazil','norway','australia','sweden','ireland','czechia','denmark','malaysia','chile','russia','poland','romania','ecuador','luxembourg','philippines','japan','pakistan','thailand','saudiarabia','indonesia','finland','india','southafrica','greece','iceland','dominicanrepublic','mexico','panama','peru','argentina','singapore','serbia','croatia','slovenia','colombia','qatar','estonia','algeria','hongkong','diamondprincess','egypt','iraq','uae','newzealand','morocco','bahrain','ukraine','lithuania','armenia','hungary','lebanon','bosniaandherzegovina','bulgaria','latvia','andorra','slovakia','tunisia','moldova','kazakhstan','costarica','northmacedonia','taiwan','uruguay','azerbaijan','kuwait','jordan','cyprus','burkinafaso','réunion','albania','sanmarino','vietnam','cameroon','oman','cuba','senegal','afghanistan','uzbekistan','faeroeislands','malta','ivorycoast','ghana','belarus','mauritius','srilanka','honduras','channelislands','venezuela','nigeria','brunei','martinique','palestine','guadeloupe','georgia','montenegro','cambodia','bolivia','kyrgyzstan','drc','mayotte','trinidadandtobago','rwanda','gibraltar','liechtenstein','paraguay','isleofman','kenya','madagascar','aruba','monaco','bangladesh','uganda','frenchguiana','macao','guatemala','jamaica','frenchpolynesia','zambia','togo','barbados','elsalvador','djibouti','mali','niger','bermuda','ethiopia','guinea','tanzania','congo','maldives','gabon','newcaledonia','myanmar','saintmartin','eritrea','haiti','bahamas','guyana','caymanislands','dominica','equatorialguinea','mongolia','curaçao','namibia','syria','greenland','seychelles','benin','grenada','laos','saintlucia','eswatini','zimbabwe','guinea-bissau','libya','mozambique','saintkittsandnevis','suriname','angola','sudan','antiguaandbarbuda','chad','caboverde','mauritania','vaticancity','stbarth','sintmaarten','nepal','fiji','montserrat','somalia','turksandcaicos','gambia','nicaragua','bhutan','belize','botswana','britishvirginislands','car','liberia','mszaandam','anguilla','burundi','papuanewguinea','stvincentgrenadines','sierraleone','timor-leste','china']
generic_message = "To get the most recent COVID-19 stats, text the name of a US state or global country.\n\nText TOTAL to get the stats for the world.\n\nText SOURCE to know where the numbers come from."

def clean_text(txt):
    return txt.lower().strip().replace(".","").replace(" ","")

def format_response_for_cases(obj):
    if obj == "":
        return generic_message

    displayName = obj['displayName']
    confirmed = obj['totalConfirmed']
    deaths = obj['totalDeaths']
    recovered = obj['totalRecovered']

    return ("Cases in {0}: {1} confirmed, {2} recovered, {3} deaths".
        format(displayName, confirmed, recovered, deaths))

app = Flask(__name__)
app.config.from_object(__name__)


@app.route("/sms", methods=['GET', 'POST'])
def incoming_sms():
    """ Get the incoming message the user sent our Twilio number """
    resp = MessagingResponse()

    body = request.values.get('Body', None)

    if (body is None):
        resp.message("THERE IS NO BODY!!! IS IT A ZOMBIE?")
        return str(resp)

    search_term = clean_text(body)
    print(search_term)

    ### Special Cases ######################################
    # if ("china" in search_term):
    #     search_term = "chinamainland"
    if ("unitedstates" in search_term):
        search_term = "usa"
    if "southkorea" in search_term:
        search_term = "skorea"
    ########################################################

    if search_term == "source":
        resp.message("For more information on where the data comes from, go to {0}. \n\nFor more information on the API, go to {1}".
            format("https://www.worldometers.info/coronavirus/", "https://github.com/ChrisMichaelPerezSantiago/covid19"))
        return str(resp)

    # helpful message
    elif search_term in ["hello", "hi", "yo", "corona", "covid"]:
        resp.message(generic_message)
        return str(resp)

    # global
    elif search_term in ["total", "global", "world"]:
        report = requests.get(url = "https://covid19-server.chrismichael.now.sh/api/v1/AllReports") 

        global_stats = report.json()['reports'][0]

        resp.message("Total cases in the world: {0} confirmed, {1} recovered, {2} deaths.".
            format(
                global_stats['cases'],
                global_stats['recovered'],
                global_stats['deaths']))
#                global_stats['active_cases'][0]['currently_infected_patients']))

     # Total for each country
    elif search_term in [clean_text(c) for c in countries]:
        countries_api = requests.get(url = "https://covid19-server.chrismichael.now.sh/api/v1/AllReports") 

        my_country = ""
        for country in countries_api.json()['reports'][0]['table'][0]:
            if clean_text(country['Country']) == search_term:
                my_country = country
                break
        
        obj = {"totalConfirmed": my_country['TotalCases'],
               "totalRecovered": my_country['TotalRecovered'],
               "totalDeaths": my_country['TotalDeaths'],
               "displayName": my_country['Country']}

        resp.message(format_response_for_cases(obj))
        

    # Total for each US state
    elif search_term in us_states:
        states_api = requests.get(url = "https://covid19-server.chrismichael.now.sh/api/v1/CasesInAllUSStates") 
        my_state = ""
        
        for state in states_api.json()['data'][0]['table']:
            if clean_text(state['USAState']) == search_term:
                my_state = state
                break

        obj = {"totalConfirmed": my_state['TotalCases'],
               "totalRecovered": 0,#my_state['TotalRecovered'],
               "totalDeaths": my_state['TotalDeaths'],
               "displayName": my_state['USAState']}


        resp.message(format_response_for_cases(obj))

    else:
        resp.message(generic_message)

    return str(resp)


if __name__ == "__main__":
    app.run(debug=True)