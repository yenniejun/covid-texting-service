import string
import re

def clean_text(txt):
    return ''.join(txt.lower().strip().replace(".","").replace(",",""))

# https://stackoverflow.com/questions/1823058/how-to-print-number-with-commas-as-thousands-separators
# 123,456,789
def format_num(num):
    if num != None: return f'{num:,}'
    else: return num


def format_total_cases(json_object):
	resp = "Total cases in the world:\n {0} confirmed\n {1} recovered\n {2} deaths".format(
        format_num(json_object['totalConfirmed']),
        format_num(json_object['totalRecovered']),
        format_num(json_object['totalDeaths']))
	return resp