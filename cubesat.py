import bootbt
from btcon import BTCon
import sys
import subprocess

def main(otherpi):
    print("running connection test")
    connection=bootbt.bt_selftest(otherpi, "True")
    print("test done")
    print("connected and waiting for ready")
    connection.receive_string()
    print("ready received")
    connection.write_string(subprocess.call(["vcgencmd", "measure_temp"])) 
    connection.close_all_connections()
    
    
if __name__ == "__main__":
    otherpi = sys.argv[1]#name of other pi hostname
    realRun = sys.argv[2]#whether this is the 1st/2nd time run in startup.sh
    if realRun == "True":
        main(otherpi)
    else:
        bootbt.bt_selftest(otherpi, "True")        
