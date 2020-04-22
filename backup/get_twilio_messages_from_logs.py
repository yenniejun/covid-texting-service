account_sid = "AC21f2520650e863ffd6ed9613e1a98da4"
username = "AC21f2520650e863ffd6ed9613e1a98da4"
password = "5c2d28b637af6701da3b5a483557b5d3"

# CHANGE THIS TO WHATEVER NUMBER I WANT
phone_num = "17185243409"


# GET ALL responses

dateSent = "2020-04-21"

if dateSent:
    url = 'https://api.twilio.com/2010-04-01/Accounts/{0}/Messages.json?To=%2B{1}&DateSent>={2}'.format(account_sid, phone_num, dateSent)
else:
    url = 'https://api.twilio.com/2010-04-01/Accounts/{0}/Messages.json?To=%2B{1}'.format(account_sid, phone_num)

while (True):
    response = get(url, auth=(username, password))
    
    # Do stuff with response
    num_responses = len(response.json()['messages'])
    print(num_responses)
    
    # print whatever information you want to see I guess
#     for msg in response.json()['messages']:
#         print(msg['body'], msg['from'], msg['date_sent'], msg['error_message'])
    
    if (num_responses < 50): 
        break
    
    # skip token
    print(response.json()['next_page_uri'])
    url = 'https://api.twilio.com/{0}'.format(response.json()['next_page_uri'])


# from io import StringIO
# import pandas as pd

# # This works too... Just returns a CSV?
# url = 'https://api.twilio.com/2010-04-01/Accounts/{0}/Messages.csv'.format(account_sid, phone_num)
# response = get(url, auth=(username, password))
# data = StringIO(response.text)
# df = pd.read_csv(data)
                 