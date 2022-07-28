#! /usr/bin/bash
timestamp=$(date +%c)
touch $HOME/boot.txt
echo "$timestamp" > $HOME/boot.txt
sleep 10s
sudo hciconfig hci0 piscan
touch $HOME/donesleep.txt
python3 $HOME/CHARMS/cubesat.py raspberrypi4 True > printlog.txt &
touch $HOME/ranthing.txt
sleep 3s
python3 $HOME/CHARMS/cubesat.py raspberrypi4 False 
