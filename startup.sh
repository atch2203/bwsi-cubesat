#! /usr/bin/bash
sleep 10s
sudo hciconfig hci0 piscan
touch $HOME/donesleep.txt
python3 $HOME/CHARMS/btcon_main.py client raspberrypi4 True >> $HOME/btcon.log &
touch $HOME/ranthing.txt
