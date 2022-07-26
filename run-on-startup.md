# To get stuff to run on startup
1. Run `crontab -e`
2. Use nano and add `@reboot python3 $HOME/CHARMS/btcon_main.py` and whatever arguments (host, rapsberypi4)
