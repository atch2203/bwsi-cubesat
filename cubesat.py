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
        img.set_user_values("alex", 0.37938867461135106, 271, 31)
        #img.set_user_values("stephen",0.3744906844618852, 271, 27)
        #img.set_user_values("hannah", 0.4077146200289641, 289, 25)
        self.otherpi = otherpi
        self.adcs = ADCS()
        self.state = "commission"
        self.orbit = 0
        self.orbit_adcs = 0
        self.comms_pass = 0
        self.prefix = "image"
        #queues for sending

        # TODO: check and uncomment the new science queue below 
        #       if it's formatted correctly (changed the values 
        #       to make more constant/stable and run in 2 orbit)

        self.science_queue = np.array([0, 60, 120, 180, 240, 300, 360+30, 360+90, 360+150, 360+210, 360+270, 360+330]) / 360
        
        # #revised angle order: 0-60-120-180-240-300-30-90-150-210-270-330
        # #big leap from 300 to 30 degrees 

        self.retake_queue = np.array([])
        self.angle_index = np.array([])
        self.image_queue = []
        self.image_comms = False
        #orbit constants
        self.time_scale = 60 #seconds per orbit
        self.cycle = 0.5 #wait time per nominal cycle
        
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
            for i in self.science_queue:
                if self.orbit_adcs - i > 10/360: #too late/rotated too much, postpone to next orbit
                    self.science_queue = self.science_queue[self.science_queue != i]
                    if i+1 < 7:
                        self.science_queue = np.append(self.science_queue, i+1)
                    #print(f"skipped {i},\n orbit is {self.orbit_adcs} and angle is {self.adcs.get_yaw()}")
                elif self.orbit_adcs > i:
                    self.prefix = "image"
                    self.state = "science" 
                    self.science_queue = self.science_queue[self.science_queue != i]
                    print(f"execute {i}")
                    break
            
            #orbit 5-7: 5 photos max x 2 sec per photo max margin
            if self.state != "science":
                for i in self.retake_queue:
                    if self.orbit_adcs - i > 10/360: #too late/rotated too much, postpone to next orbit
                        self.retake_queue = self.retake_queue[self.retake_queue != i]
                        if i+1 < 7:
                            self.retake_queue = np.append(self.retake_queue, i+1)
                        #print(f"skipped {i},\n orbit is {self.orbit_adcs} and angle is {self.adcs.get_yaw()}")
                    elif self.orbit_adcs > i:
                        self.prefix = "retake"
                        self.state = "science" 
                        self.retake_queue = self.retake_queue[self.retake_queue != i]
                        print(f"execute {i}")
                        break

            #telemetry packet
            if self.orbit_adcs > self.comms_pass and self.state != "science":
                self.state = "comms" 
                self.comms_pass = self.comms_pass + 1.07

            #orbit 8-10: transmit 5 images and text file
            elif self.orbit_adcs > 7 and self.state != "science" and len(self.image_queue) > 0:
                self.state = "comms"
                self.image_comms = True
            #TODO: add checks for angle, etc to switch state 
    
    def science(self):
        print(f"science {self.orbit_adcs}")
        
        name = f"{self.prefix}_{self.cur_image}"
        if self.prefix == "retake":
            name = f"{self.prefix}_{np.floor(self.adcs.get_yaw())}_{np.floor(self.orbit_adcs)}"
        else:
            self.cur_image = self.cur_image + 1
       
        print(f"image at angle {self.adcs.get_yaw()}")
        #take image and process it
        img.camera.capture(f"/home/pi/CHARMS/Images/{name}.jpg")
        yaw = self.adcs.get_yaw()
        habs = img.find_HABs(f"/home/pi/CHARMS/Images/{name}.jpg", self.adcs.get_yaw())#TODO change constants
        
        #formulate data
        t = time.localtime()
        hab_data = "no hab found"
        if len(habs) > 0:
            hab_data = ""
            for hab in habs:
                hab_angle = hab.central_angle #find this from processing
                dist = hab.distance
                sector = hab.sector
                x = hab.x
                y = hab.y
                area = hab.area
                hab_data += f"\nhab angle:{hab_angle}\nhab distance:{dist}\nsector:{sector}\nx:{x}\ny:{y}\narea:{area}\n" 

 
        data = (f"{name}\n{time.strftime('%H:%M:%S', t)}\n"
        f"angle: {yaw}\n"
        f"{hab_data}\n")
        
        #write data
        with open(f"/home/pi/CHARMS/Images/{name}.txt", "w") as f:
            f.write(data)
        
        #add to self.image_queue depending on quality of image
        if sector != -1:
            print("found hab")
            if self.prefix == "retake": #don't add initial images
                self.image_queue.append(name)

            if self.orbit_adcs < 5:
                cur_orbit = np.floor(self.orbit_adcs)
                next = cur_orbit + 2 + hab_angle/360
                self.add_angle(next)

        self.state = "nominal"
    
    def add_angle(self, angle):
        if self.find_index(angle, self.retake_queue, 10) != -1:
            print("no")
            return False
        self.retake_queue = np.append(self.retake_queue, angle)
        return True

    def find_index(self, angle, arr, bound):
        for i in arr:
            if self.close_angles(angle, i, bound):
                return np.where(abs(arr - i) < 0.0001)[0][0]
        return -1

    def close_angles(self, a1, a2, bound):
        a1_frac = np.mod(a1, 1)
        a2_frac = np.mod(a2, 1)
        diff = a1_frac - a2_frac
        return abs(diff) < bound/360 or abs(diff + 1) < bound/360 or abs(diff - 1) < bound/360 
        

    def comms(self): 
        print(f"comms {self.orbit_adcs}")
        
        #send packet
        self.connection.connect_repeat_again_as_client(1, 3)
        self.send_telemetry() 
        print(self.image_queue)

        #send images
        if self.image_comms:
            print("sending images")
            self.connection.write_raw("connect")
            self.connection.connect_as_host(1)
            for image in self.image_queue:
                self.send_image(image)           
                self.connection.write_raw("again")
            self.image_queue = []
            self.image_comms = False
        else:
            self.connection.write_raw("no")
        self.connection.write_raw("done")        
        self.connection.close_all_connections()
        self.state = "nominal"

    def commission(self):
        print("commission")
        
        
        #Comms test/init
        print("running connection test")
        self.connection=bootbt.bt_selftest(self.otherpi, "True")
        print("connected and waiting for ready")
        self.connection.receive_raw()
        print("ready received")
        #ADCS init
        self.adcs.calibrate(10)
        self.connection.write_raw("got_ready")
        self.connection.receive_raw()
        self.adcs.initial_angle(True)
        print("start received")
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
        f"{subprocess.check_output(['vcgencmd', 'measure_temp']).decode('UTF-8')}"
        f"retake_queue {self.retake_queue}\n")
        
        self.connection.write_string(send_data)
        #receive updates
        #self.connection.connect_as_host(2)
        #response = self.connection.receive_raw()
        #if response != "no_update":
         #   data = self.connection.receive_raw()
          #  while data != "done":
           #     print(data)
            #    data = self.connection.receive_raw() #TODO parse data 
            

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
            if np.mod(self.orbit, 1) > 0.75 and orbit_adcs < 90:
                orbit_adcs = orbit_adcs + 360
            elif np.mod(self.orbit, 1) < 0.25 and orbit_adcs > 270:
                orbit_adcs = orbit_adcs - 360
            self.orbit_adcs = np.floor(self.orbit) + orbit_adcs / 360
        
if __name__ == "__main__":
    otherpi = sys.argv[1]
    realRun = sys.argv[2]
    cubesat = Cubesat(otherpi)
    if realRun == "True":
        cubesat.main(otherpi)
    else:
        bootbt.bt_selftest(otherpi, "True")        
