from flask import Flask, request, session
from twilio.twiml.messaging_response import MessagingResponse
import requests
import string
import re
import json

# TODO AUTO REFRESH

# hard coded for now ... ¯\_(ツ)_/¯
louisiana_parishes = ['orleans','jefferson','caddo','eastbatonrouge','sttammany','ascension','lafayette','stjohnthebaptist','stjames','bossier','stbernard','lafourche','rapides','ouachita','terrebonne','stcharles','calcasieu','iberville','plaquemines','desoto','livingston','westbatonrouge','avoyelles','stmartin','stlandry','webster','assumption','acadia','washington','tangipahoa','lincoln','stmary','allen','eastfeliciana','beauregard','evangeline','iberia','union','claiborne','jackson','richland','morehouse','natchitoches','vermilion','vernon','catahoula','bienville','pointecoupee','jeffersondavis','grant','madison','lasalle','winn','westfeliciana']
us_states = ['newyork','newjersey','california','washington','michigan','massachusetts','florida','illinois','louisiana','pennsylvania','georgia','colorado','texas','connecticut','tennessee','ohio','indiana','wisconsin','maryland','northcarolina','missouri','arizona','virginia','mississippi','alabama','southcarolina','nevada','utah','oregon','minnesota','arkansas','oklahoma','districtofcolumbia','kentucky','iowa','idaho','rhodeisland','kansas','newmexico','newhampshire','vermont','maine','delaware','montana','hawaii','westvirginia','alaska','nebraska','wyoming','northdakota','southdakota']
countries = ['unitedstates','italy','chinamainland','spain','germany','france','iran','unitedkingdom','switzerland','southkorea','netherlands','austria','belgium','turkey','canada','portugal','norway','australia','brazil','sweden','israel','czechrepublic','denmark','malaysia','ireland','ecuador','chile','luxembourg','poland','japan','pakistan','romania','southafrica','thailand','saudiarabia','indonesia','finland','russia','greece','iceland','india','philippines','panama','singapore','mexico','argentina','peru','slovenia','croatia','dominicanrepublic','estonia','qatar','colombia','egypt','serbia','hongkong','bahrain','iraq','newzealand','algeria','unitedarabemirates','lebanon','morocco','lithuania','armenia','ukraine','hungary','bulgaria','latvia','slovakia','taiwan','andorra','costarica','uruguay','bosniaandherzegovina','tunisia','kuwait','sanmarino','northmacedonia','jordan','moldova','albania','burkinafaso','azerbaijan','vietnam','cyprus','runion','malta','ghana','kazakhstan','oman','senegal','brunei','venezuela','srilanka','cambodia','ctedivoire','honduras','mauritius','belarus','afghanistan','cameroon','palestinianauthority','uzbekistan','georgia','nigeria','cuba','guadeloupe','kosovo','montenegro','trinidadandtobago','martinique','puertorico','bolivia','kyrgyzstan','liechtenstein','rwanda','congodrc','jersey','paraguay','bangladesh','guam','guernsey','macau','mayotte','monaco','guatemala','kenya','isleofman','frenchguiana','jamaica','madagascar','togo','barbados','zambia','uganda','usvirginislands','ethiopia','maldives','elsalvador','tanzania','equatorialguinea','djibouti','mali','mongolia','saintmartin','dominica','niger','eswatini','bahamas','namibia','suriname','haiti','guinea','benin','mozambique','gabon','seychelles','grenada','eritrea','laos','guyana','zimbabwe','myanmar','fiji','syria','vaticancity','angola','nepal','congo','caboverde','somalia','saintlucia','sudan','gambia','chad','centralafricanrepublic','saintbarthelemy','bhutan','antiguaandbarbuda','liberia','mauritania','guineabissau','belize','nicaragua','stvincentandthegrenadines','libya','timorleste','papuanewguinea']

generic_message = "To get the most recent COVID-19 stats, text the name of a Louisiana parish, US state, or country.\n\nText TOTAL to get the stats for the world.\n\nText SOURCE to know where the numbers come from."

def clean_text(txt):
    return txt.lower().strip().replace(".","").replace(" ","")

def format_response_for_cases(json_object):
    if json_object == "":
        return generic_message

    displayName = json_object['displayName']
    confirmed = json_object['totalConfirmed']
    deaths = json_object['totalDeaths']
    recovered = json_object['totalRecovered']

    return ("Cases in {0}: {1} confirmed, {2} recovered, {3} deaths".
        format(displayName, confirmed, recovered, deaths))

app = Flask(__name__)
app.config.from_object(__name__)


@app.route("/sms", methods=['GET', 'POST'])
def incoming_sms():
    """ Get the incoming message the user sent our Twilio number """
    resp = MessagingResponse()

    body = request.values.get('Body', None)
    search_term = clean_text(body)
    print(search_term)

    bing_json = requests.get(url = "https://bing.com/covid/data")

    ### Special Cases ######################################
    if ("china" in search_term):
        search_term = "chinamainland"
    if ("usa" in search_term):
        search_term = "unitedstates"
    ########################################################

    if search_term == "source":
        resp.message("For more information on where the data comes from, go to {0}".
            format("https://bing.com/covid/data"))

    # helpful message
    elif search_term in ["hello", "hi", "yo", "corona", "covid"]:
        resp.message(generic_message)
        return str(resp)

    # global
    elif search_term in ["total", "global", "world"]:
        resp.message("Total cases in the world: {0} confirmed, {1} recovered, {2} deaths.".
            format(
                bing_json.json()['totalConfirmed'], 
                bing_json.json()['totalRecovered'], 
                bing_json.json()['totalDeaths']))

     # Total for each country
    elif search_term in countries:
        mycountry = ""
        for country in bing_json.json()['areas']:
            if country['id'] == search_term:
                mycountry = country
                break
                print ("found:", country['id'], country['displayName'], country['totalConfirmed'])

        resp.message(format_response_for_cases(mycountry))
       

    # Total for each US state
    elif search_term in us_states:
        mystate = ""
        for country in bing_json.json()['areas']:
            if country['id'] == "unitedstates":
                for state in country['areas']:
                    if search_term in state['id']:
                        mystate = state
                        print (state['displayName'], state['totalConfirmed'])
        
        resp.message(format_response_for_cases(mystate))
               
    # Gets the total for each Louisiana parish
    elif search_term in louisiana_parishes:
        print("Louisiana Parish!")
        myparish = ""
        for country in bing_json.json()['areas']:
            if country['id'] == "unitedstates":
                for state in country['areas']:
                    if "louisiana" in state['id']:
                        for parish in state['areas']:
                            if search_term in parish['id']:
                                myparish = parish
                                print(parish['id'])    

        resp.message(format_response_for_cases(myparish))

    else:
        resp.message(generic_message)

    return str(resp)


if __name__ == "__main__":
    app.run(debug=True)


