import btboot
from btcon import BTCon
import sys

def main(otherpi):
    bt_self_test(otherpi, "True")
    connection = BTCon(otherpi)
    
if __name__ == "__main__":
    realRun = sys.argv[1]#whether this is the 1st/2nd time run in startup.sh
    otherpi = sys.argv[2]#name of other pi hostname
    if realRun == "True":
        main(otherpi)
    else:
        bt_selftest()        
