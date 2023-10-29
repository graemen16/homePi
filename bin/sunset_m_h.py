import datetime
from astral import Astral

city_name = 'Glasgow'

a = Astral()
a.solar_depression = 'civil'

city = a[city_name]

sun = city.sun(date=datetime.datetime.now(), local=True)
print('{} {}'.format(str(sun['dusk'].minute), str(sun['dusk'].hour)))
