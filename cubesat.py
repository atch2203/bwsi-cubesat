from Comms import bootbt
from Comms.btcon import BTCon
from IMU.mag_avg_adcs import ADCS
from Imaging import imaging_stage_one as img
import sys
import subprocess
import time
import threading
import numpy as np

class Cubesat:
    def __init__(self, otherpi):
        self.otherpi = otherpi
        self.adcs = ADCS()
        self.state = "commission"
        self.orbit = 0
        self.orbit_adcs = 0
        self.comms_pass = 0
        self.prefix = "image"
        #queues for sending
        self.science_queue = np.array([1, 1.25, 1.5, 1.75, 2, 2.35, 2.65, 2.9]) 
        self.process_queue = []
        self.image_queue = []
        self.image_comms = False
        #orbit constants
        self.time_scale = 10 #seconds per orbit
        self.cycle = 1 #wait time per nominal cycle
        
        self.cur_image = 1#TODO change this

    def main(self, otherpi):
        while self.orbit_adcs < 10 and self.state != "sleep":
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
            #print("nominal")
            time.sleep(self.cycle)

            #orbit 1-4: 12 total photos x 2 sec per photo (max margin) to process
            #orbit 5-7: 5 photos max x 2 sec per photo max margin
            for i in self.science_queue:
                if self.orbit_adcs - i > 0.2: #too late/rotated too much, postpone to next orbit
                    self.science_queue.remove(i)
                    self.science_queue.append(i+1)
                if self.orbit_adcs > i:
                    self.state = "science" 
                    self.science_queue.remove(i) 
                    break

            #telemetry packet
            elif self.orbit_adcs > self.comms_pass:
                self.state = "comms" 
                self.comms_pass = self.comms_pass + 1 #TODO adapt to HAB positions

            #orbit 8-10: transmit 5 images and text file
            elif self.orbit_adcs > 7:
                self.state = "comms"
                self.image_comms = True
            #TODO: add checks for angle, etc to switch state 
    
    def science(self):
        print(f"science {self.orbit_adcs}")
        
        name = f"{self.prefix}_{self.cur_image}"
        self.cur_image = self.cur_image + 1
        
        #take image and process it
        img.camera.capture(f"/home/pi/CHARMS/Images/{name}.jpg")
        img.find_HABs(f"/home/pi/CHARMS/Images/{name}.jpg", self.adcs.get_yaw(), img.real2Img, img.E2PicCenter, img.centerOff)#TODO change constants
        
        hab = 1 #find this from processing
        dist = 1

        #formulate data
        t = time.localtime()
        data = (f"{name}\n{time.strftime('%H:%M:%S', t)}\n"
        f"angle: {self.adcs.get_yaw()}\nhab angle:{hab}\nhab distance:{dist}")
        
        #write data
        with open(f"/home/pi/CHARMS/Images/{name}.txt", "w") as f:
            f.write(data)
        
        #add to self.image_queue depending on quality of image
        self.image_queue.append(name)
        self.state = "nominal"
    
    def comms(self): 
        print(f"comms {self.orbit_adcs}")
        
        #send packet
        self.connection.connect_repeat_again_as_client(1, 3)
        self.send_telemetry() 

        #send images
        if self.image_comms:
            for image in self.image_queue:
                self.connection.write_raw("again")
                self.send_image(image)           
            self.image_comms = False
        self.connection.write_raw("done")        
        self.connection.close_all_connections()
        self.state = "nominal"

    def commission(self):
        print("commission")
        
        #ADCS init
        self.adcs.calibrate(10)
        self.adcs.initial_angle(False)
        
        #Comms test/init
        print("running connection test")
        self.connection=bootbt.bt_selftest(self.otherpi, "True")
        print("connected and waiting for ready")
        self.connection.receive_raw()
        print("ready received")
        self.connection.close_all_connections()
        
        #ADCS start, start
        self.start_time = time.time()
        self.adcs_thread = threading.Thread(target=self.background_update, daemon=True)
        self.adcs_thread.start()
        self.state = "nominal"
        
        
    def error(self): #TODO
        print("error")

    def sleep(self):
        print("sleep")
        self.connection.connect_repeat_again_as_client(1, 3)
        self.connection.write_raw("sleep")
        self.connection.write_raw("done")
        self.connection.close_all_connections()
        #TODO: shutdown somehow: subprocess?
    
    def safe(self):#TODO
        print("safe")
    
    def send_telemetry(self): #Connect as client before calling
        self.connection.write_raw("telemetry")
        #formulate packet
        t = time.localtime()
        send_data = (f"{time.strftime('%H:%M:%S', t)}\norbit: {self.orbit_adcs}\nangle: {self.adcs.get_yaw()}\n"
        f"{subprocess.check_output(['vcgencmd', 'measure_temp']).decode('UTF-8')}")
        
        self.connection.write_string(send_data)
        #receive updates
        self.connection.connect_as_host(2)
        response = self.connection.receive_raw()
        if response != "no_update":
            data = self.connection.receive_raw()
            while data != "done":
                print(data)
                data = self.connection.receive_raw() #TODO parse data 
            

    def send_image(self, name): #connect as client and host before calling
        start_time = time.time()
        self.connection.write_raw("image")
        
        self.connection.receive_raw()
        #send name
        print(f"sending {name}")
        self.connection.write_raw(name)
        
        self.connection.receive_raw()
        #write image
        self.connection.write_image(f"/home/pi/CHARMS/Images/{name}.jpg")
        
        self.connection.receive_raw() #DO NOT TRY TO CONNECT AGAIN WHILE THE GROUND STATION IS RECEIVING DATA
        
        with open(f"/home/pi/CHARMS/Images/{name}.txt", "r") as f:
            self.connection.write_string(f.read())
        
        print(time.time() - start_time)

    def background_update(self):
        while True:
            time.sleep(0.25)
            self.adcs.update_yaw_average()

            #update orbit
            self.orbit = (time.time() - self.start_time) / self.time_scale 
            orbit_adcs = self.adcs.get_yaw()
            #correct for imprecision in orbit
            if np.mod(self.orbit, 1) > 0.3 and orbit_adcs < 100:
                orbit_adcs = orbit_adcs + 360
            elif np.mod(self.orbit, 1) < 0.7 and orbit_adcs > 260:
                orbit_adcs = orbit_adcs - 360
            self.orbit_adcs = np.floor(self.orbit) + orbit_adcs / 360
            print(self.orbit_adcs)
        
if __name__ == "__main__":
    otherpi = sys.argv[1]#name of other pi hostname
    realRun = sys.argv[2]#whether this is the 1st/2nd time run in startup.sh
    cubesat = Cubesat(otherpi)
    if realRun == "True":
        cubesat.main(otherpi)
    else:
        bootbt.bt_selftest(otherpi, "True")        
