# weather class test

import logging
import json
import urllib.request
import urllib.error
import sqlite3
import datetime
import ener
from astral import Astral

def build_url():
    city_id = '2647178' # Helensburgh city ID 
    user_api = '41e3afb2e3e440fde9d33eb74ac34053'  # Obtain yours form: http://openweathermap.org/
    unit = 'metric'  # For Fahrenheit use imperial, for Celsius use metric, and the default is Kelvin.
    api = 'http://api.openweathermap.org/data/2.5/weather?id='     # Search for your city ID here: http://bulk.openweathermap.org/sample/city.list.json.gz

    full_api_url = api + str(city_id) + '&mode=json&units=' + unit + '&APPID=' + user_api
    return full_api_url

def data_fetch(full_api_url):
    logging.debug('requesting url')
    try:
        url = urllib.request.urlopen(full_api_url)
        output = url.read().decode('utf-8') # should return json format data
    except urllib.error.HTTPError as e:
        msg = 'The server couldn\'t fulfill the request. Error code: ' + str(e.code)
        logging.error(msg)
        raw_api_dict = None
    except urllib.error.URLError as e:
        msg = 'We failed to reach a server. Reason: ' + e.reason
        # note on BT broadband, BT redirect url errors, so this won't always work
        logging.error(msg)
        raw_api_dict = None
    else:
        logging.debug('no url error, now about to read')
        url.close()
        # need to check we have valid json data in case htp gave us something bad
        try:
            raw_api_dict = json.loads(output) # translates json format to dictionary
        except ValueError as e: # can't find a useful error code
            logging.error(e)
            raw_api_dict = None        
    return raw_api_dict 

class weather_log (object):
    def __init__(self):
        self.status = 'empty'
        # check if we can get a record from database
        # if so, and record < 15 mins old and < 1 hr stale
        # ..then use that weather record#
        # otherwise try to get a new record
        # if it's good then use that
        # if we have a record < 1 hr then status is good
        # if it's between 1 - 8 yours then status is stale

w = weather_log()

