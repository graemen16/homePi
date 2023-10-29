#!/bin/bash
# script to update crontab with lines to switch off
# socket at sunrise and switch on again at sunset

crontab -l|grep -v 'ener'
echo $(python /home/pi/bin/sunrise_m_h.py) '* * * python3 /home/pi/bin/ener_sockets.py S1 off >> /home/pi/logs/cronlog.log 2>&1'
echo $(python /home/pi/bin/sunset_m_h.py) '* * * python3 /home/pi/bin/ener_sockets.py S1 on >> /home/pi/logs/cronlog.log 2>&1'

