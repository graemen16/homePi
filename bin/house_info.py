from flask import Flask, render_template
import sqlite3
import datetime
import logging
import ener
import subprocess

app = Flask(__name__)

weatherd = {
   'dt':0,
   'clouds':{'all':0},
   'main':{'temp':0,'pressure':0,'humidity':0},
   'wind':{'speed':0,'deg':0},
   'weather':{'id': 0, 'main':'','description':'','icon':''}
   } # create global dictionary variable
sockets = {
   'S1' : {'stat' : 'xxx', 'time' : 'xxx', 'ts' : 0, 'man' : False, 'use' : 'Outside light'},
   'S2' : {'stat' : 'xxx', 'time' : 'xxx', 'ts' : 0, 'man' : False, 'use' : 'Downstairs light'}
   }
tform = "%d-%m-%Y %H:%M"
cameras = {
    'du':0,
    'left':{'du':0},
    'right':{'du':0}
    }

def get_weather_db_data():
    # get weather data from database if possible
    global weatherd
    # don't bother requesting data if we can't connect to the database
    try:
        wcon = sqlite3.connect('/mnt/GigaStore/db/home.db')
    except sqlite3.Error as e:
        logging.error('unable to connect to db on GigaStore')
        logging.error(e)
        return

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
    weatherd['weather']['id'] = record[8]
    weatherd['weather']['main'] = record[9]
    weatherd['weather']['description'] = record[10]
    weatherd['weather']['icon'] = record[11]
    wcon.close()

def get_socket_status():
   global sockets
   try:
      wcon = sqlite3.connect('/home/pi/data/house_stat.db')
      wcur = wcon.cursor()
      wcur.execute('SELECT * FROM Bool_Settings ORDER BY fname')
   except sqlite3.Error as e:
      logging.error(e)
   else:
      data = wcur.fetchall()
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

def get_cam_status():
    cameras['du']=subprocess.check_output(['du','-sh', '/mnt/GigaStore']).split()[0].decode('utf-8')
    cameras['left']['du'] = subprocess.check_output(['du','-sh', '/mnt/GigaStore/FTP/Cameras/Camera_rear_left/']).split()[0].decode('utf-8')
    cameras['right']['du'] = subprocess.check_output(['du','-sh', '/mnt/GigaStore/FTP/Cameras/Camera_rear_right/']).split()[0].decode('utf-8')
    return

@app.route("/")
def home():
   now = datetime.datetime.now()
   
   timeString = now.strftime(tform)
   get_socket_status()
   get_weather_db_data()
   get_cam_status()
   templateData = {
      'title' : 'Casa Nelson',
      'time': timeString,
      'data_time' :datetime.datetime.fromtimestamp(weatherd['dt']).strftime(tform),
      'clouds': weatherd['clouds']['all'],
      'temp' : weatherd['main']['temp'],
      'pressure' : weatherd['main']['pressure'],
      'humidity' : weatherd['main']['humidity'],
      'wind_speed' : weatherd['wind']['speed'],
      'weather' : weatherd,
      'wicon_url' : 'http://www.openweathermap.org/img/w/'+str(weatherd['weather']['icon'])+'.png',
      'sockets' : sockets,
      'cameras' : cameras
      }
   return render_template('main.html', **templateData)

# The function below is executed when someone requests a URL with the socket name and action in it:
@app.route("/<ss>/<action>")
def action(ss, action):
   logging.debug('change socket ' + ss + ' to ' + action)
   ener.sockets(ss, action, 'man')

   now = datetime.datetime.now()
   timeString = now.strftime("%d-%m-%Y %H:%M")
   get_socket_status()
   get_weather_db_data()
   templateData = {
      'title' : 'Casa Nelson',
      'time': timeString,
      'data_time' :datetime.datetime.fromtimestamp(weatherd['dt']).strftime(tform),
      'clouds': weatherd['clouds']['all'],
      'temp' : weatherd['main']['temp'],
      'pressure' : weatherd['main']['pressure'],
      'humidity' : weatherd['main']['humidity'],
      'wind_speed' : weatherd['wind']['speed'],
      'weather' : weatherd,
      'wicon_url' : 'http://www.openweathermap.org/img/w/'+str(weatherd['weather']['icon'])+'.png',
      'sockets' : sockets,
      'cameras' : cameras
      }
   return render_template('main.html', **templateData)

if __name__ == "__main__":
   logging.basicConfig(filename='/home/pi/logs/house_server.log', format='%(asctime)s %(levelname)s: %(message)s', level=logging.DEBUG)
   logging.debug("server started")
   print ("server started.")
   app.run(host='0.0.0.0', port=80, debug=True)
