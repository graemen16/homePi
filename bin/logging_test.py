# see https://docs.python.org/3/howto/logging.html
import logging

logging.basicConfig(filename='/home/pi/logs/sample.log', format='%(asctime)s %(levelname)s: %(message)s', level=logging.DEBUG)
 
logging.debug("This is a debug message")
logging.info("Informational message")
logging.error("An error has happened!")
