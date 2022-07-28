import bootbt
from btcon import BTCon
import sys

def main(otherpi):
    bootbt.bt_selftest(otherpi, "True")
    connection = BTCon(otherpi)
    
if __name__ == "__main__":
    otherpi = sys.argv[1]#name of other pi hostname
    realRun = sys.argv[2]#whether this is the 1st/2nd time run in startup.sh
    if realRun == "True":
        main(otherpi)
    else:
        bootbt.bt_selftest(otherpi, "True")        
