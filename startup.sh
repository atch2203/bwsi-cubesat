#! /usr/bin/bash
sleep 10s
sudo hciconfig hci0 piscan
touch $HOME/donesleep.txt
python3 $HOME/CHARMS/bootbt.py raspberrypi3 True &
touch $HOME/ranthing.txt
sleep 3s
python3 $HOME/CHARMS/bootbt.py raspberrypi3 True
