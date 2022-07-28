import bootbt
from btcon import BTCon
import sys

def main(otherpi):
    print("running connection test")
    bootbt.bt_selftest(otherpi, "True")
    print("test done")
    connection = BTCon(otherpi)
    print("connecting as host")
    connection.connect_as_host(1)
    print("connected and waiting for ready")
    connection.receive_string()
    print("ready received")
    
    
if __name__ == "__main__":
    otherpi = sys.argv[1]#name of other pi hostname
    realRun = sys.argv[2]#whether this is the 1st/2nd time run in startup.sh
    if realRun == "True":
        main(otherpi)
    else:
        bootbt.bt_selftest(otherpi, "True")        
