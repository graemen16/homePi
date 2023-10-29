# downstairs_light.py
# control downstairs light socket
# switch off during sleep time
# switch on morning & evening
# switch off during the day if it's daylight, not too dull
# switch on during day if it gets a bit dull
# log activities to external drive
# call as a cron job periodically

import logging
import json
import urllib.request
import urllib.error
import sqlite3
import datetime
import ener
from astral import Astral
import paho.mqtt.publish as publish

weatherd = {
   'dt':0,
   'clouds':{'all':0},
   'main':{'temp':0,'pressure':0,'humidity':0},
   'wind':{'speed':0,'deg':0},
   'weather':[{'id': 0, 'main':'','description':'','icon':''}]
   } # create global dictionary variable
sockets = {
   'S1' : {'stat' : 'xxx', 'time' : 'xxx', 'ts' : 0, 'man' : False, 'use' : 'Outside light'},
   'S2' : {'stat' : 'xxx', 'time' : 'xxx', 'ts' : 0, 'man' : False, 'use' : 'Downstairs light'}
   }
tform = "%d-%m-%Y %H:%M"
tls_dict = {'ca_certs':"/home/pi/mqtt_srv.crt"}

def build_url():
    # build a url to request local weather data from openweathermap.org
    city_id = '2647178' # Helensburgh city ID 
    user_api = '41e3afb2e3e440fde9d33eb74ac34053'  # Obtain yours form: http://openweathermap.org/
    unit = 'metric'  # For Fahrenheit use imperial, for Celsius use metric, and the default is Kelvin.
    api = 'http://api.openweathermap.org/data/2.5/weather?id='     # Search for your city ID here: http://bulk.openweathermap.org/sample/city.list.json.gz

    full_api_url = api + str(city_id) + '&mode=json&units=' + unit + '&APPID=' + user_api
    return full_api_url


def data_fetch(full_api_url):
    # request data from url and if successful, load into a dictionary variable
    logging.debug('requesting url')
    try:
        url = urllib.request.urlopen(full_api_url)
        output = url.read().decode('utf-8') # should return json format data
    except urllib.error.HTTPError as e:
        msg = 'The server couldn\'t fulfill the request. Error code: ' + str(e.code)
        logging.error(msg)
        raw_api_dict = None
    except urllib.error.URLError as e:
        msg = 'We failed to reach a server. Reason: ' + str(e.reason)
        # note on BT broadband, BT redirect url errors, so this won't always work
        logging.error(msg)
        raw_api_dict = None
    else:
        url.close()
        try:
            raw_api_dict = json.loads(output) # translates json format to dictionary
        except ValueError as e: # can't find a useful error code
            logging.error(str(e))
            raw_api_dict = None        
    return raw_api_dict 

def logWeatherData():
    # get weather data from database if possible, and if needed update from web
    global weatherd
    # don't bother requesting data if we can't connect to the database
    try:
        wcon = sqlite3.connect('/mnt/GigaStore/db/home.db')
    except sqlite3.Error as e:
        logging.error('unable to connect to db on GigaStore')
        logging.error(str(e))
        return

    # we don't want to call the data too frequently..
    # only request data if last data logged was more than 30 mins old
    SQL = 'SELECT * FROM Weather_Data ORDER BY dt DESC LIMIT 1'
    wcur = wcon.cursor()
    wcur.execute(SQL)
    record = wcur.fetchone()
    logging.debug('read from db: '+str(record))
    last_dt = record[0]
    # load the last data record in case we don't go for new data
    dt = record[1]
    weatherd['dt'] = record[1]
    weatherd['clouds']['all'] = record[2]
    weatherd['main']['temp'] = record[3]
    weatherd['main']['pressure'] = record[4]
    weatherd['main']['humidity'] = record[5]
    weatherd['wind']['speed'] = record[6]
    weatherd['wind']['deg'] = record[7]
    weatherd['weather'][0]['id'] = record[8]
    weatherd['weather'][0]['main'] = record[9]
    weatherd['weather'][0]['description'] = record[10]
    weatherd['weather'][0]['icon'] = record[11]
    
    dt_now = int(datetime.datetime.timestamp(datetime.datetime.now()))
    if dt > (dt_now - 3000): # timestamp is less than 50 mins old...
        logging.debug('logged data less than 50 mins old: '\
                      +datetime.datetime.fromtimestamp(dt).strftime(tform))
        wcon.close()
        return
    else:
        logging.debug('more than 50 mins old - last: '\
                      +datetime.datetime.fromtimestamp(dt).strftime(tform))
    weatherd = data_fetch(build_url())
    if weatherd is not None:
        # extract relevant data from dictionary item to a tuple
        try:
            entry = [dt_now,\
                     int(weatherd['dt']),\
                     int(weatherd['clouds']['all']),\
                     float(weatherd['main']['temp']),\
                     float(weatherd['main']['pressure']),\
                     float(weatherd['main']['humidity']),\
                     float(weatherd['wind']['speed']),\
                     ]
            if 'deg' in weatherd['wind']: # guard for missing 'deg'
                entry += [float(weatherd['wind']['deg']),]
            else:
                entry += [0,]
            entry += int(weatherd['weather'][0]['id']),\
                     str(weatherd['weather'][0]['main']),\
                     str(weatherd['weather'][0]['description']),\
                     str(weatherd['weather'][0]['icon']),
        except KeyError as e:
            logging.error(str(e))
            logging.error(str(weatherd))
            # entry won't be set, so can't carry on regardless...
        else:
            if not dt == weatherd['dt']:
                # data from server is not the same as already logged
                SQL = 'insert into Weather_Data values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
                wcur.execute(SQL, entry)
                wcon.commit()
                logging.debug('weather data logged with tag '
                              +datetime.datetime.fromtimestamp(weatherd['dt']).strftime(tform))
                # also publish temperature to mqtt server
                sensord= {
                    'id':'external',
                    'loc':'Outside',
                    'val': weatherd['main']['temp'],
                    'ts':datetime.datetime.fromtimestamp(weatherd['dt']).strftime(tform)
                    },
                try:
                    publish.single("sensors", str(sensord), hostname="raspberrypi", port=8883, tls=tls_dict)
                except ValueError as e:
                    logging.error(e)
                except OSError as e:
                    logging.error(e)
                
            else:
                logging.debug('data from server is same as already logged for dt:' +\
                              datetime.datetime.fromtimestamp(weatherd['dt']).strftime(tform))
    else:
        logging.info('No weather data to log')
    wcon.close()

# isSleepTime
def is_sleep_time():
    get_up = ("6:10","6:10","6:10","6:10","6:10","8:30","8:30")
    go_to_bed = ("22:10", "22:10", "22:10", "22:10", "22:40", "22:40", "22:10")
    week_day = datetime.date.weekday(datetime.date.today()) # Monday is 0, Sunday is 6
    get_up_time =datetime.datetime.strptime(get_up[week_day],"%H:%M").time()
    bed_time =datetime.datetime.strptime(go_to_bed[week_day],"%H:%M").time()
    time_now = datetime.datetime.now().time()
    return (time_now < get_up_time) or (time_now > bed_time)
    
# isLight
def is_light():
    # is it light enough outside that we don't need the light on?
    # 1 hour after sunrise, 1 hour before sunset
    a = Astral()
    a.solar_depression = 'civil'
    sun = a['Glasgow'].sun(date=datetime.datetime.now(), local=True)
    dt_now = datetime.datetime.now().replace(tzinfo = sun['sunset'].tzinfo)
    hour_1 = datetime.timedelta(hours = 1)
    return (dt_now > sun['sunrise']+hour_1) and (dt_now < sun['sunset']-hour_1)
    
    
# isDullOrDark
def is_dull():
    # cloud > 50%? function of sun position in sky?
    # don't think cloud data is sufficiently reliable
    # go with cloud > 80% or humidity > 85%
    status = None
    if weatherd is not None: # this is a global variable
        if (weatherd['clouds']['all'] > 80) or (weatherd['main']['humidity'] > 85):
            status = True
            logging.debug('it is dull')
        else:
            status = False
            logging.debug('it is not dull')
    return status    
    
# wasOn
##def was_on():
##    # need some error handling for this
##    try:
##        wcon = sqlite3.connect('/home/pi/data/house_stat.db')
##        wcur = wcon.cursor()
##        wcur.execute('SELECT fval FROM Bool_Settings WHERE fname=?', ('S2',))
##    except sqlite3.Error as e:
##        logging.error(e)
##        status = None
##    else:
##        status = wcur.fetchone()[0] == 1
##        wcon.close()
##        #logging.debug('got current status')
##    logging.debug('was on status :' + str(status))
##    return status
##
##def socket_status (socket):
##    try:
##        wcon = sqlite3.connect('/home/pi/data/house_stat.db')
##        wcur = wcon.cursor()
##        wcur.execute('SELECT fval FROM Bool_Settings WHERE fname=?', (socket,))
##    except sqlite3.Error as e:
##        logging.error(e)
##        status = 'Unknown'
##    else:
##        if (wcur.fetchone()[0] == 1):
##            status = 'On'
##        else:
##            status = 'Off'
##        wcon.close()
##        logging.debug('got current status')
##    logging.debug('was on status :' + status)
##    return status

def get_socket_status():
   global sockets
   try:
      wcon = sqlite3.connect('/home/pi/data/house_stat.db')
      wcur = wcon.cursor()
      wcur.execute('SELECT * FROM Bool_Settings ORDER BY fname')
   except sqlite3.Error as e:
      logging.error(str(e))
   else:
      data = wcur.fetchall()
      # logging.debug('data: '+str(data))
      wcon.close()
      i=0
      for ss in sockets:
         socket = data[i][0]
         if data[i][1]== 1:
            sockets[socket]['stat'] = 'On'
         else:
            sockets[socket]['stat'] = 'Off'
         sockets[socket]['time'] = datetime.datetime.fromtimestamp(data[i][2]).strftime(tform)
         sockets[socket]['ts']=data[i][2]
         if data[i][3]== 1:
            sockets[socket]['man'] = True
         else:
            sockets[socket]['man'] = False
         i=i+1
   return 

def socket_overriden(socket):
    global sockets
    dt_now = int(datetime.datetime.timestamp(datetime.datetime.now()))
    if sockets[socket]['man'] and (dt_now - int(sockets[socket]['ts'])) < 7200:
        return True
    else:
        return False
         

# main...
if __name__ == '__main__':
    logging.basicConfig(filename='/home/pi/logs/downstairs_light.log', format='%(asctime)s %(levelname)s: %(message)s', level=logging.DEBUG)
    logging.debug("going for weather data")

    # download weather data and log to external drive
    # would be neat if we created an instance of a weatherdata object
    
    logWeatherData()
    get_socket_status()
    if socket_overriden('S2'):
        logging.debug('on manual override since '+sockets['S2']['time']+str(sockets['S2']['man']))
    else:
        if is_sleep_time():
            logging.debug('sleep time')
            if sockets['S2']['stat']=='On':
                logging.debug('sleep time. S2 Stat was: ' + str(sockets['S2']['stat']))
                ener.sockets('S2', 'off')
        else: # not sleep time
            logging.debug('not sleep time')
            # change here - ignore 'is_dull' if None
            if is_light()and not is_dull():
                logging.debug('light and not dull - S2 Stat was: ' + str(sockets['S2']['stat']))
                if sockets['S2']['stat']=='On':
                    ener.sockets('S2', 'off')
            else: # dull or not light
                logging.debug('dull or not light - S2 Stat was: ' + str(sockets['S2']['stat']))
                if sockets['S2']['stat']=='Off':
                    ener.sockets('S2', 'on')

# if it's now sleep time
# -- if socket was on and then switch off and end
# if it's not sleep time
# -- if socket was on
# --- if it's light outside then switch off
# -- if socket was off
# --- if it's dull or dark outside then switch on





