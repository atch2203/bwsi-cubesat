import stationinit 
from btcon import BTCon
import sys

def main(otherpi):
    connection = stationinit.bt_groundtest(otherpi, "True")
    print("Type READY to start")
    while input() != "READY":
        print("not ready")
    connection.write_string("ready")
    print(f"{connection.receive_string()}")
    connection.close_all_connections()
    
if __name__ == "__main__":
    otherpi = sys.argv[1]#name of other pi hostname
    main(otherpi)
