from urllib.request import Request, urlopen
from urllib.error import URLError
req = Request('http://xpi.openweathermap.org')
try:
    req = Request('http://xpi.openweathermap.org')
    response = urlopen(req)
except URLError as e:
    if hasattr(e, 'reason'):
        print('We failed to reach a server.')
        print('Reason: ', e.reason)
    elif hasattr(e, 'code'):
        print('The server couldn\'t fulfill the request.')
        print('Error code: ', e.code)
except Error as e:
    print('some other error')
    print (e)
else:
    print('no error')
