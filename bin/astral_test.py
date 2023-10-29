import datetime
from astral import Astral

city_name = 'Glasgow'

a = Astral()
a.solar_depression = 'civil'

city = a[city_name]

print('Information for %s/%s\n' % (city_name, city.region))

timezone = city.timezone
print('Timezone: %s' % timezone)

print('Latitude: %.02f; Longitude: %.02f\n' % (city.latitude, city.longitude))

#sun = city.sun(date=datetime.date(2009, 4, 22), local=True)
sun = city.sun(date=datetime.datetime.now(), local=True)
print('time:    %s' % str(datetime.datetime.now()))
print('Dawn:    %s' % str(sun['dawn']))
print('Sunrise: %s' % str(sun['sunrise']))
print('Noon:    %s' % str(sun['noon']))
print('Sunset:  %s' % str(sun['sunset']))
print('Dusk:    %s' % str(sun['dusk']))
print('sunrise minute hour:   {} {}'.format(str(sun['sunrise'].minute), str(sun['sunrise'].hour)))
print('sunset minute hour:    {} {}'.format(str(sun['sunset'].minute), str(sun['sunset'].hour)))
