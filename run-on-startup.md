# To get stuff to run on startup (only do this on the cubesat pi)
1. Run `crontab -e`
2. Add `@reboot $HOME/CHARMS/startup.sh`
3. Modify the hostname (raspberrypi3) in `startup.sh`
