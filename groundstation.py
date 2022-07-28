import stationinit 
from btcon import BTCon
import sys

def main(otherpi):
    stationinit.bt_groundtest(otherpi, "True")
    connection = BTCon(otherpi)
    connection.connect_repeat_as_client(1, 5)
    print("Type READY to start")
    while input() != "READY":
    connection.write_string("ready")
    
if __name__ == "__main__":
    otherpi = sys.argv[1]#name of other pi hostname
    main(otherpi)
