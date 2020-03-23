from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import pandas as pd 
import itertools
import time

class Coronavirus():
  def __init__(self, link):
    self.driver = webdriver.Chrome()
    self.driver.get(link)

###############################
#        Helper Methods       # 
###############################

# Splits a list into groups of n
# Ex: grouper(3, 'ABCDEFG', 'x') --> ABC DEF Gxx
# From https://stackoverflow.com/questions/1624883/alternative-way-to-split-a-list-into-groups-of-n
def grouper(n, iterable, fillvalue=None):
    args = [iter(iterable)] * n
    return itertools.zip_longest(*args, fillvalue=fillvalue)

def clean_text(txt):
    return txt.lower().replace(" ","")

# TODO find typos and resolve typo errors

###############################
# Get webdrivers for scraping # 
###############################
def get_country_bot():
	return Coronavirus('https://www.worldometers.info/coronavirus/')

def get_us_bot():
	return Coronavirus('https://www.worldometers.info/coronavirus/country/us/')

def get_louisiana_bot():
	return Coronavirus('https://www.arcgis.com/apps/opsdashboard/index.html#/69b726e2b82e408f89c3a54f96e8f776')


####################################
# Get scraped stats as a dataframe # 
####################################

def get_us_state(bot_us, state, is_total=False):
	states = bot_us.driver.find_elements_by_xpath("//tbody/tr/td")
	lines = [" ".join(state.get_attribute("innerHTML").split()) for state in states]
	grouped_list = list(grouper(8, lines))
	df = pd.DataFrame(grouped_list).iloc[:,0:5]
	df.columns =['State', 'TotalCases', 'NewCases', 'TotalDeaths', 'NewDeaths']
	
	if is_total:
		return df[df.State.str.contains('Total')]

	df['stripped_state'] = [clean_text(p) for p in df.State.values]
	state = df[df.stripped_state == state]
	print(state)
	return state

def get_parish(bot_la, parish):
	# if parish_list is empty, fetch all
    lines = bot_la.driver.find_elements_by_xpath('//*[@id="ember56"]/div/nav/span/div/div/p[2]/strong')
    lines = [line.get_attribute("innerHTML") for line in lines]
    grouped_list = list(grouper(3, lines))
    df = pd.DataFrame(grouped_list, columns =['Parish', 'Cases', 'Deaths']) 
    df.reset_index(inplace=True)  

    df['stripped_parish'] = [clean_text(p) for p in df.Parish.values]
    parish = df[df.stripped_parish == parish]

    return parish

# TODO: get_country

