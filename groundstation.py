import stationinit 
from btcon import BTCon
import sys

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
                print(f"{self.connection.receive_string()}")
            elif type == "image":
                name = self.connection.receive_raw()
                self.connection.receive_image(f"Data/{name}.jpg")
                with open("Data/{name}.txt", "w") as f:
                    f.write(self.connection.receive_string())
            again = self.connection.receive_raw()
            if again != "again":
                self.connection.close_all_connections()
                break
                    
    
if __name__ == "__main__":
    otherpi = sys.argv[1]#name of other pi hostname
    ground = Ground(otherpi)
    ground.main(otherpi)
