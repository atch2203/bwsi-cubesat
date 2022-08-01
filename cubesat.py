from Comms import bootbt
from Comms.btcon import BTCon
from ADCS.adcs_main import ADCS
import sys
import subprocess
import time

class Cubesat:
    def __init__(self, otherpi):
        self.otherpi = otherpi
        self.adcs = ADCS()
        self.state = "commission"

    def main(self, otherpi):
        print("running connection test")
        self.connection=bootbt.bt_selftest(self.otherpi, "True")
        print("test done")
        print("connected and waiting for ready")
        self.connection.receive_raw()
        print("ready received")
        self.connection.close_all_connections()
        for i in range(5):
            time.sleep(1)
            print(i)
            self.connection.connect_repeat_again_as_client(1, 3)
            if i == 3:
                self.send_image("saturnpencil", 45, 32)
            else:
                self.send_telemetry()
            self.connection.close_all_connections()
            if self.state == "nominal":
                print("nominal")
            elif self.state == "science":
                print("science")
            elif self.state == "comms":
                print("comms")
            elif self.state == "commission":
                print("commission")
            elif self.state == "error":
                print("error")
            elif self.state == "sleep":
                print("sleep")
            elif self.state == "safe":
                print("safe")





    
    def send_telemetry(self): #Connect as client before calling
        start_time = time.time()
        self.connection.write_raw("telemetry")
        t = time.localtime()
        send_data = (f"{time.strftime('%H:%M:%S', t)}\n"
        f"{subprocess.check_output(['vcgencmd', 'measure_temp']).decode('UTF-8')}")
        self.connection.write_string(send_data)
        self.connection.write_raw("done")
        print(time.time() - start_time)

    def send_image(self, name, adcs, hab): #connect as client before calling
        start_time = time.time()
        self.connection.write_raw("image")
        self.connection.connect_as_host(2)
        t = time.localtime()
        send_data = (f"{name}\n{time.strftime('%H:%M:%S', t)}\n"
        f"angle: {adcs}\nhab angle:{hab}")
        self.connection.write_raw(name)
        self.connection.write_image(f"/home/pi/CHARMS/Images/{name}.jpg")
        self.connection.receive_raw() #DO NOT TRY TO CONNECT AGAIN WHILE THE GROUND STATION IS RECEIVING DATA
        self.connection.write_string(send_data)
        self.connection.write_raw("done")#change for multiple images, use list parameter
        print(time.time() - start_time)
        
if __name__ == "__main__":
    otherpi = sys.argv[1]#name of other pi hostname
    realRun = sys.argv[2]#whether this is the 1st/2nd time run in startup.sh
    cubesat = Cubesat(otherpi)
    if realRun == "True":
        cubesat.main(otherpi)
    else:
        bootbt.bt_selftest(otherpi, "True")        
