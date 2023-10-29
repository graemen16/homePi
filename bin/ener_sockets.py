#import the required modules
import argparse
import logging
import ener

logging.basicConfig(filename='/home/pi/logs/ener_sockets.log', format='%(asctime)s %(levelname)s: %(message)s', level=logging.DEBUG)

# setup the parser
parser = argparse.ArgumentParser()
parser.add_argument("socket", choices=['S1','S2'], help="Socket S1 or S2")
parser.add_argument("command", choices=['on','off'], help="Command on or off")

args = parser.parse_args()
ener.sockets(args.socket, args.command)

