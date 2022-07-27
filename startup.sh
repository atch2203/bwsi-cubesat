#! /usr/bin/bash
sleep 10s
touch $HOME/donesleep
python3 $HOME/CHARMS/btcon_main.py client raspberrypi3 > $HOME/btcon.log &
