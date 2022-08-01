from Comms import stationinit 
from Comms.btcon import BTCon
import sys
import time

class Ground:
    def __init__(self, otherpi):
        self.otherpi = otherpi

    def main(self, otherpi):
        self.connection = stationinit.bt_groundtest(self.otherpi, "True")
        print("Type READY to start")
        while input() != "READY":
            print("not ready")
        self.connection.write_raw("ready")
        self.connection.close_all_connections()
        for i in range (5):
            print(i)
            self.nominal_loop()
        self.connection.close_all_connections()

    def nominal_loop(self):
        self.connection.connect_as_host(1)
        while True:
            type = self.connection.receive_raw()
            if type == "telemetry":
                self.telemetry()
            elif type == "image":
                self.image()
            again = self.connection.receive_raw()
            if again != "again":
                self.connection.close_all_connections()
                break
    
    def telemetry(self):
        print(f"{self.connection.receive_string()}")
                    
    def image(self):
        time.sleep(1)
            self.connection.connect_repeat_again_as_client(2, 3)
            name = self.connection.receive_raw()
            self.connection.receive_image(f"/home/pi/CHARMS/Data/{name}.jpg")
            self.connection.write_raw("done")
            data = self.connection.receive_string()
            with open(f"/home/pi/CHARMS/Data/{name}.txt", "w") as f:
                f.write(data)
    
if __name__ == "__main__":
    otherpi = sys.argv[1]#name of other pi hostname
    ground = Ground(otherpi)
    ground.main(otherpi)
