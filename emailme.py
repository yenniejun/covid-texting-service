from flask import Flask
from flask_mail import Mail, Message
import os
from dotenv import load_dotenv, find_dotenv
import corona
import time
from datetime import date
import pandas as pd
from tabulate import tabulate
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import render_template

tabulate.PRESERVE_WHITESPACE = True

app = Flask(__name__)

load_dotenv(find_dotenv())

mail_settings = {
	"MAIL_SERVER": 'smtp.gmail.com',
	"MAIL_PORT": 465,
	"MAIL_USE_TLS": False,
	"MAIL_USE_SSL": True,
	"MAIL_USERNAME": os.environ['EMAIL_USER'],
	"MAIL_PASSWORD": os.environ['EMAIL_PASSWORD']
}

app.config.update(mail_settings)
mail = Mail(app)

today = date.today()
date_now = today.strftime("%m/%d/%y")

# louisiana_updates_df = corona.get_parishes()
# df = pd.read_csv('louisiana_updates_df.csv')
bot_la = corona.get_louisiana_bot()
bot_us = corona.get_us_bot()
time.sleep(5)

df_la = corona.get_parish_df(bot_la)
df_la.reset_index(inplace=True)  
df_la = df_la.sort_values(by='Parish')
df_la = df_la[["Parish", "Cases", "Deaths"]]

df_us = corona.get_states_df(bot_us)
# df_us.drop(columns="Unnamed: 0", inplace=True)
df_us.State.replace("<strong>Total:</strong>", "Total", inplace=True)
total = df_us[53:54]
df_us = df_us[0:51].sort_values(by='State')


if __name__ == '__main__':
	with app.app_context():
		message_template = render_template('email_template.html',  
			parishtable=[df_la.to_html(index=False, classes='data', header="true")], 
			statetable = [df_us.to_html(index=False, classes='data', header="true")],
			countrytable = [total.to_html(index=False, classes='data', header='true')],
			date=date_now)
		msg = Message(subject="Your Corona Updates in Louisiana for {}".format(date_now),
					  sender=app.config.get("MAIL_USERNAME"),
					  recipients=["yennie.jun@gmail.com"], # replace with your email for testing
					  body="hi")
		msg.html = message_template
		mail.send(msg) 


def print_table(table):
    col_width = [max(len(x) for x in col) for col in zip(*table)]
    for line in table:
        print ("| " + " | ".join("{:{}}".format(x, col_width[i])
                                for i, x in enumerate(line)) + " |")
