from Comms import stationinit 
from Comms.btcon import BTCon
from Comms import git_push 
import sys
import time
import threading

class Ground:
    def __init__(self, otherpi):
        self.otherpi = otherpi
        self.orbit = 0
        self.push = False
        self.send = False

    def main(self, otherpi):
        self.commission()
        while self.orbit < 10:
            self.nominal_loop()

    def nominal_loop(self):
        self.connection.connect_as_host(1)
        while True:
            type = self.connection.receive_raw()
            if type == "telemetry":
                self.telemetry()
            elif type == "image":
                self.image()
            elif type == "sleep":
                self.orbit = 10
            elif type == "done":
                break

            connect = self.connection.receive_raw()
            if connect == "connect":
                self.connection.connect_repeat_again_as_client(3, 5)
            #check to go again
            again = self.connection.receive_raw()
            if again != "again":
                self.connection.close_all_connections()
                break
        #pull for updates
        #push images
        if self.push:
            git_push.pull()
            self.push = False
            self.push_image_thread = threading.Thread(target=git_push.commit_and_push, args=("add images"))
            self.push_image_thread.start()
        #parse update.txt
        #with open("/home/pi/CHARMS/update.txt", "r") as f:
        #    self.update_data = f.readlines()
        #change update.txt to no to not repeat update
        #if self.update_data[0] == "yes":
        #    self.send = True
        #    self.update_data[0] = "no"
        #    with open("/home/pi/CHARMS/update.txt", "w") as f:
        #        f.writelines(self.update_data)
        #    self.push_update_thread = threading.Thread(target=git_push.commit_and_push, args=("read update.txt"))
        #    self.push_update_thread.start()

    def commission(self):
        self.connection = stationinit.bt_groundtest(self.otherpi, "True")
        print("Type READY to ready") #init adcs
        while input() != "READY":
            print("not ready")
        self.connection.write_raw("ready")
        print(f"received {self.connection.receive_raw()}")
        print("Type START to start")
        while input() != "START":
            print("not start")
        self.connection.write_raw("start")
        self.connection.close_all_connections()
    
    def telemetry(self):
        #receive telemetry
        print(f"{self.connection.receive_string()}")
        #send updates
        #self.connection.connect_repeat_again_as_client(2, 3)
        #if self.send:
        #    self.connection.write_raw("update")
        #    for l in self.update_data[1:]:
        #        self.connection.write_raw(l)
        #    self.connection.write_raw("done") 
        #else:
        #    self.connection.write_raw("no_update")
                    
    def image(self):
        self.push = True
        self.connection.write_raw("ready1")
        
        name = self.connection.receive_raw()
        
        self.connection.write_raw("ready2")
        #receive image
        print(f"receiving {name}")
        self.connection.receive_image(f"/home/pi/CHARMS/Data/{name}.jpg")
        
        print("sending done")
        self.connection.write_raw("done")
        #receive and write data
        data = self.connection.receive_string()
        with open(f"/home/pi/CHARMS/Data/{name}.txt", "w") as f:
            f.write(data)
    
if __name__ == "__main__":
    otherpi = sys.argv[1]#name of other pi hostname
    ground = Ground(otherpi)
    ground.main(otherpi)
