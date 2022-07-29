import bootbt
from btcon import BTCon
import sys
import subprocess
import time

class Cubesat:
    def __init__(self, otherpi):
        self.otherpi = otherpi

    def main(self, otherpi):
        print("running connection test")
        self.connection=bootbt.bt_selftest(self.otherpi, "True")
        print("test done")
        print("connected and waiting for ready")
        self.connection.receive_string()
        print("ready received")
        self.connection.close_all_connections()
        for i in range(5):
            time.sleep(1)
            print(i)
            self.send_telemetry(self.connection)
            self.connection.close_all_connections()
        self.connection.close_all_connections()
    
    def send_telemetry(self, connection):
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
    cubesat = Cubesat(otherpi)
    if realRun == "True":
        cubesat.main(otherpi)
    else:
        bootbt.bt_selftest(otherpi, "True")        
