# socket test
import logging
import sqlite3
import datetime
import ener

if __name__ == '__main__':
    logging.basicConfig(filename='/home/pi/logs/socket_test.log', format='%(asctime)s %(levelname)s: %(message)s', level=logging.DEBUG)
    logging.info("starting socket test")
    ener.sockets('S2', 'off')
