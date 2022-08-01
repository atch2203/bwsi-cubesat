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
        self.orbit = 0

    def main(self, otherpi):
        while self.orbit < 10 and self.state != "sleep":
            if self.state == "nominal":
                self.nominal() 
            elif self.state == "science":
                self.science()
            elif self.state == "comms":
                self.comms()         
            elif self.state == "commission":
                self.commission()
            elif self.state == "error":
                self.error()
            elif self.state == "safe":
                self.safe()
        self.sleep()

    def nominal(self):
        while self.state == "nominal": 
            print("nominal")
            time.sleep(1)
            #add checks for angle, etc to switch state 
            self.state = "comms"
    
    def science(self):
        print("science")
        #take image, process it, add adcs data to it
        t = time.localtime()
        data = (f"{name}\n{time.strftime('%H:%M:%S', t)}\n"
        f"angle: {adcs}\nhab angle:{hab}")
        #write data to txt file
    
    def comms(self):
        print("comms")
        self.orbit = self.orbit + 1
        if self.orbit == 10:
            self.state = "sleep"
        self.connection.connect_repeat_again_as_client(1, 3)
        self.send_telemetry() 
        self.connection.write_raw("done")
        self.connection.close_all_connections()

    def commission(self):
        print("commission")
        print("running connection test")
        self.connection=bootbt.bt_selftest(self.otherpi, "True")
        print("connected and waiting for ready")
        self.connection.receive_raw()
        print("ready received")
        #add init stuff and add 2nd ready/start?
        self.connection.close_all_connections()
        self.state = "nominal"
        
        
    def error(self):
        print("error")

    def sleep(self):
        print("sleep")
        self.connection.connect_repeat_again_as_client(1, 3)
        self.connection.write_raw("sleep")
        self.connection.write_raw("done")
        self.connection.close_all_connections()
        #shutdown somehow: subprocess?
    
    def safe(self):
        print("safe")
    
    def send_telemetry(self): #Connect as client before calling
        start_time = time.time()
        self.connection.write_raw("telemetry")
        t = time.localtime()
        send_data = (f"{time.strftime('%H:%M:%S', t)}\norbit: {self.orbit}\n"
        f"{subprocess.check_output(['vcgencmd', 'measure_temp']).decode('UTF-8')}")
        self.connection.write_string(send_data)
        print(time.time() - start_time)

    def send_image(self, name, adcs, hab): #connect as client before calling
        start_time = time.time()
        self.connection.write_raw("image")
        self.connection.connect_as_host(2)
        self.connection.write_raw(name)
        while True:
            self.connection.write_image(f"/home/pi/CHARMS/Images/{name}.jpg")
            reply = self.connection.receive_raw() #DO NOT TRY TO CONNECT AGAIN WHILE THE GROUND STATION IS RECEIVING DATA
            if reply == "done":
                break #otherwise error received
        #read txt file and put in write string
        self.connection.write_string(send_data)
        print(time.time() - start_time)
        
if __name__ == "__main__":
    otherpi = sys.argv[1]#name of other pi hostname
    realRun = sys.argv[2]#whether this is the 1st/2nd time run in startup.sh
    cubesat = Cubesat(otherpi)
    if realRun == "True":
        cubesat.main(otherpi)
    else:
        bootbt.bt_selftest(otherpi, "True")        
