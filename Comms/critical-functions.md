# To get stuff to run on startup (only do this on the cubesat pi)
1. Run `crontab -e` and choose a text editor
2. Add `@reboot $HOME/CHARMS/startup.sh` to the bottom of the file
3. Modify the hostname (raspberrypi3) in `startup.sh` to the ground station pi name
4. There should be a file named `boot.txt` with the date in your home directory

# To send an image
1. Run `python3 btcon_main.py client other_pi_name True` on the cubesat pi
2. Run `python3 btcon_main.py host other_pi_name True` on the ground station pi
3. There should be a file named `test.jpg` that is a copy of `saturnpencil.jpg`
