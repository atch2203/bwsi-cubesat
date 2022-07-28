import stationinit 
from btcon import BTCon
import sys

def main(otherpi):
    stationinit.bt_groundtest(otherpi, "True")
    connection = BTCon(otherpi)
    
if __name__ == "__main__":
    otherpi = sys.argv[1]#name of other pi hostname
    realRun = sys.argv[2]#whether this is the 1st/2nd time run in startup.sh
    if realRun == "True":
        main(otherpi)
    else:
        stationinit.bt_groundtest(otherpi, "True")        
