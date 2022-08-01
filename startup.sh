#! /usr/bin/bash
sleep 10s
sudo hciconfig hci0 piscan
python3 $HOME/CHARMS/cubesat.py raspberrypi4 True > printlog.txt &
sleep 3s
python3 $HOME/CHARMS/cubesat.py raspberrypi4 False 
