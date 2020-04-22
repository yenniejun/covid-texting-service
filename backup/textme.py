from twilio.rest import Client

account_sid = 'AC21f2520650e863ffd6ed9613e1a98da4'
auth_token = '5c2d28b637af6701da3b5a483557b5d3'
messaging_service_sid = 'MG190803a65ac8975b66401b6fefe262a6'
phone_sid = 'PNba2e97fa706fe092e5947bde5ffc2492'
phone_num = +17185243409

client = Client(account_sid, auth_token)

client = Client(account_sid, auth_token)

message = client.messages.create(
                              body='Hi there!',
                              from_='+17185243409',
                              to='+12252840859'
                          )

print(message.sid)

# twilio api:messaging:v1:services:phone-numbers:create --service-sid MG5a1ff0ba14452f770b3de4753164c9cb --phone-number-sid PN8b34cad5050f49ffe598652e4e981b2f
# twilio api:messaging:v1:services:update --sid MG5a1ff0ba14452f770b3de4753164c9cb --inbound-request-url https://9c7c4919.ngrok.io/sms

