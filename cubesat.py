import bootbt
from btcon import BTCon
import sys
import subprocess
import time

def main(otherpi):
    print("running connection test")
    connection=bootbt.bt_selftest(otherpi, "True")
    print("test done")
    print("connected and waiting for ready")
    connection.receive_string()
    print("ready received")
    connection.close_all_connections()
    for i in range(5):
        time.sleep(1)
        print(i)
        send_telemetry(connection)
        connection.close_all_connections()
    connection.close_all_connections()
    
def send_telemetry(connection):
    start_time = time.time()
    connection.connect_repeat_again_as_client(1, 3)
    t = time.localtime()
    send_data = f"""{time.strftime("%H:%M:%S", t)}
    {subprocess.check_output(['vcgencmd', 'measure_temp']).decode('UTF-8')}"""
    connection.write_string(send_data)
    print(time.time() - start_time)
    
    
if __name__ == "__main__":
    otherpi = sys.argv[1]#name of other pi hostname
    realRun = sys.argv[2]#whether this is the 1st/2nd time run in startup.sh
    if realRun == "True":
        main(otherpi)
    else:
        bootbt.bt_selftest(otherpi, "True")        
