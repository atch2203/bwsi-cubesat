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
        self.connection.write_string("ready")
        self.connection.close_all_connections()
        for i in range (5):
            print(i)
            self.connection.connect_as_host(1)
            print(f"{self.connection.receive_string()}")
        self.connection.close_all_connections()
    
if __name__ == "__main__":
    otherpi = sys.argv[1]#name of other pi hostname
    ground = Ground(otherpi)
    ground.main(otherpi)
