#import the required modules
import RPi.GPIO as GPIO
import time
import datetime
import sqlite3
import logging

# setup the parser - used in original for command line arguments, not library
# parser = argparse.ArgumentParser()
# parser.add_argument("socket", choices=['S1','S2'], help="Socket S1 or S2")
# parser.add_argument("command", choices=['on','off'], help="Command on or off")

# args = parser.parse_args()

def sockets(socket, command, source = 'auto'):
    # socket is 'S1' or 'S2, command is 'on' or 'off'

    # open home data sql for updates
    try:
        hcon = sqlite3.connect('/home/pi/data/house_stat.db')
        hcur = hcon.cursor()
        if command == 'on':
            dval = 1
        else:
            dval = 0
        dtf = datetime.datetime.now().timestamp()
        if source == 'man':
            fman = 1
        else:
            fman = 0
    
        hcur.execute('update Bool_Settings set fval = ?, fdt = ?,  man = ? where fname = ?',(dval, dtf, fman, socket,))
    except sqlite3.Error as e:
        logging.error(e)
    else:
        hcon.commit()
        hcon.close
    
    # set the pins numbering mode
    GPIO.setmode(GPIO.BOARD)

    # Select the GPIO pins used for the encoder K0-K3 data inputs
    GPIO.setup(11, GPIO.OUT)
    GPIO.setup(15, GPIO.OUT)
    GPIO.setup(16, GPIO.OUT)
    GPIO.setup(13, GPIO.OUT)

    # Select the signal to select ASK/FSK
    GPIO.setup(18, GPIO.OUT)

    # Select the signal used to enable/disable the modulator
    GPIO.setup(22, GPIO.OUT)

    # Disable the modulator by setting CE pin lo
    GPIO.output (22, False)

    # Set the modulator to ASK for On Off Keying 
    # by setting MODSEL pin lo
    GPIO.output (18, False)

    # Initialise K0-K3 inputs of the encoder to 0000
    GPIO.output (11, False)
    GPIO.output (15, False)
    GPIO.output (16, False)
    GPIO.output (13, False)

    # The On/Off code pairs correspond to the hand controller codes.
    # True = '1', False ='0'

    if socket == 'S1':
        if command == 'on':
            # Set K0-K3
            logging.info ("sending code 1111 socket 1 on")
            GPIO.output (11, True)
            GPIO.output (15, True)
            GPIO.output (16, True)
            GPIO.output (13, True)
            # let it settle, encoder requires this
            time.sleep(0.2)	
            # Enable the modulator
            GPIO.output (22, True)
            # keep enabled for a period
            time.sleep(0.25)
            # Disable the modulator
            GPIO.output (22, False)
        elif command == 'off':
            # Set K0-K3
            logging.info ("sending code 0111 Socket 1 off")
            GPIO.output (11, True)
            GPIO.output (15, True)
            GPIO.output (16, True)
            GPIO.output (13, False)
            # let it settle, encoder requires this
            time.sleep(0.2)
            # Enable the modulator
            GPIO.output (22, True)
            # keep enabled for a period
            time.sleep(0.5)
            # Disable the modulator
            GPIO.output (22, False)
        else:
            logging.warning ("unrecognized command")
    elif socket == 'S2':
        if command == 'on':
            # Set K0-K3
            logging.info ("sending code 1110 socket 2 on")
            GPIO.output (11, False)
            GPIO.output (15, True)
            GPIO.output (16, True)
            GPIO.output (13, True)
            # let it settle, encoder requires this
            time.sleep(0.2)	
            # Enable the modulator
            GPIO.output (22, True)
            # keep enabled for a period
            time.sleep(0.5)
            # Disable the modulator
            GPIO.output (22, False)
        elif command == 'off':
            # Set K0-K3
            logging.info ("sending code 0110 socket 2 off")
            GPIO.output (11, False)
            GPIO.output (15, True)
            GPIO.output (16, True)
            GPIO.output (13, False)
            # let it settle, encoder requires this
            time.sleep(0.2)
            # Enable the modulator
            GPIO.output (22, True)
            # keep enabled for a period
            time.sleep(0.5)
            # Disable the modulator
            GPIO.output (22, False)
        else:
            logging.warning ("unrecognized command")
    else:
        logging.warning ("unrecognized socket")
    # Clean up the GPIOs for next time
    logging.debug ("cleaning up GPIO") 
    GPIO.cleanup()
