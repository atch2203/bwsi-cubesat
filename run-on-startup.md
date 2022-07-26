# To get stuff to run on startup
1. Run `touch startup.sh` in the CHARMS directory
2. Run `crontab -e`
3. Use nano and add `@reboot $HOME/CHARMS/startup.sh`
4. Save the file and open up `startup.sh`
5. Add whatever commands you want to run at boot (`python3 test.py`, `echo "hello"`, etc)
