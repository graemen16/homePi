# OpenWeatherMap API functions
# My account graemen, API key 41e3afb2e3e440fde9d33eb74ac34053
# Helensburgh city ID 2647178

# http://api.openweathermap.org/data/2.5/weather?id=2647178&units=metric&APPID=41e3afb2e3e440fde9d33eb74ac34053

# api.openweathermap.org/v3/uvi/56.01,-4.73/current.json&appid=41e3afb2e3e440fde9d33eb74ac34053
# this doesn't work...

# http://api.owm.io/air/1.0/uvi/current?lat=56.01&lon=-4.73&appid=41e3afb2e3e440fde9d33eb74ac34053

# primarily interested in cloud cover on the basis that cloud cover will affect light level
# lets log this in sqlite database, with some other data - temperature, humidity, pressure, time
# fields: dt, clouds, temp, pressure, humidity, wind_speed, wind_dir


weatherd = {"coord":{"lon":-4.73,"lat":56.01},\
                   "weather":[{"id":310,\
                               "main":"Drizzle",\
                               "description":"light intensity drizzle rain",\
                               "icon":"09d"},\
                              {"id":500,\
                               "main":"Rain",\
                               "description":"light rain",\
                               "icon":"10d"}],\
                   "base":"stations",\
                   "main":{"temp":4.99,\
                           "pressure":1018,\
                           "humidity":93,\
                           "temp_min":4,\
                           "temp_max":6},\
                   "visibility":2700,\
                   "wind":{"speed":2.6,"deg":80},\
                   "clouds":{"all":64},\
                   "dt":1492332699,\
                   "sys":{"type":1,\
                          "id":5121,\
                          "message":0.01,\
                          "country":"GB",\
                          "sunrise":1492319376,\
                          "sunset":1492370933},\
                   "id":2647178,\
                   "name":"Helensburgh",\
                   "cod":200}

