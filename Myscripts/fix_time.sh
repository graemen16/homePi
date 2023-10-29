#!/bin/bash
# script to bring time back into synch with ntp server

sudo /etc/init.d/ntp stop
sudo ntpd -g -q
sudo /etc/init.d/ntp start
