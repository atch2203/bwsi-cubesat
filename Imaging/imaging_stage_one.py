import time
# from time import strftime
from picamera import PiCamera
import numpy as np
import cv2
import argparse
import imutils
import math
camera = PiCamera() 
camera.resolution = (750,670)
time.sleep(2)

# path = "home/pi/CHARMS/Imaging/test_images/"

'''
CONSTANTS:
'''
dir_path = "test_images/" #TODO need to figure this out


'''
CALL THE SET USER VALUES FUNCTOIN TO SET THESE
'''
user = "" 
real2Img = 1  # mm/pixle - subject to change - depending on each person's set-up
E2PicCenter = 271 #mm - subject to change - depending on each person's set-up
centerOff = 1 #subject to change - depending on each person's set-up


'''
call the set imu angle function to change this
'''
imu_angle = 0 #TODO get this info
# real2Img  = 0.3744906844618852 # mm/pixle - subject to change - depending on each person's set-up 
# E2PicCenter = 271 #mm - subject to change - depending on each person's set-up
# centerOff = 27  


HAB_list = [] #stores all detected HABs (including duplicates)

cleaned_HABs = [] #stores all unique HABs

class HAB:
    def __init__(self):
        self.area = 0
        self.x = 0
        self.y = 0
        self.central_angle = 0
        self.distance = 0
        self.sector = 0
        self.path = ""
    def __str__(self):
        return str(self.x) + " " + str(self.y) + " \n"
    def __eq__(self, other):
        # if not isinstance(other, HAB):
        #     return NotImplemented
        return self.x == other.x and self.y == other.y and self.path == other.path
    def summary(self):
        return ("\n-------\nNEW HAB: " + self.path + "\nCENTRAL ANGLE: " + str(self.central_angle) + "\nCOORDINATE: " + str(self) + "\nSECTOR: " + str(self.sector) + "\nAREA: " + str(self.area) + "\nDISTANCE TO BOARD CENTER: " + str(self.distance))
    

'''
captures an image, stores in global path by timestamp
Returns path to file as string 
'''
def capture_image():
    #capture image
    timestr = time.strftime("%Y-%m-%d_%H-%M-%S")
    fileName = user + "_" + timestr + ".jpg"
    camera.capture(dir_path + fileName)
    # return image
    return dir_path + fileName


'''
finds HAB location supplied img path, imu_angle, (and the global vars)
saves hab object(s) into HAB_list
returns a temporary list of just the new HABs from this image 
'''
def find_HABs(img, imu_angle):
    #constants
    real2Image_coef = real2Img  
    eCenter2PicCenter = E2PicCenter 
    center_offset = centerOff 
    
    image = cv2.imread(img)
    hsv_img = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    # low_bound = np.array([155,25,0])
    # up_bound = np.array ([179, 255, 255])

    low_bound = np.array([150,50,50])
    up_bound = np.array ([179, 255, 255])

    # low_bound_2 = np.array([150,50,10])
    # up_bound_2 = np.array ([179, 255, 255])



    mask = cv2.inRange(hsv_img, low_bound, up_bound)

    #uncomment this if you think something messed up
    #and you want to see how the mask looks

    # cv2.imshow("mask", mask) #comment out after integration
    # cv2.waitKey() #comment out after integration
    # cv2.destroyAllWindows() #comment out after integration

    cnts = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)

    threshold = 1000
    #red = 0 #unnecessary?
    ret_habs = []
    
    for c in cnts:
        area = cv2.contourArea(c)
        #red+=area #unnecessary?
        if(area<threshold):
            continue
        #cv2.drawContours(image,[c],-1,(0,255,0),3) #can comment out after completing integration
        M =  cv2.moments(c)
        if M["m00"] == 0:
            cX=0
            cY=0
        else:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            
        #drawing 
        #cv2.circle(image, (cX, cY), 5, (0, 255, 0), -1) #comment out after completing integration
        #cv2.putText(image, "centroid", (cX - 25, cY - 25),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (128, 0, 0), 2) #same as above
        cv2.imwrite(img[:-4] + "_mask.jpg", mask)
       
        # off_set angle of hab from IMU current angle aka camera orientation calculation
        OB = calculateDistance(375, 335 - center_offset, 750, 335 - center_offset) #edge to actual center
        OC = calculateDistance(375, 335 - center_offset, cX, cY) #distance: hab to actual center
        BC = calculateDistance(750, 335 - center_offset, cX, cY) #distance: hab to  edge relative to actual center 
        angleCBA = math.pi - cosLawAngle(OC, OB, BC) #offset angle from edge relative to actual center
        AB = eCenter2PicCenter - OB*real2Image_coef #Earth cennter to actual center
        AC = cosLawSide(angleCBA, BC*real2Image_coef, AB) #hab to Earth center
        
        if cY < (335 - center_offset) or cY == (335 - center_offset):
            angleBAC = cosLawAngle(BC*real2Image_coef, AB, AC) 
        else: angleBAC = - cosLawAngle(BC*real2Image_coef, AB, AC)
        
        
        #to avoid mdf parts
        if(AC<167):
            continue
        
        

        temp_hab = HAB()
        temp_hab.distance = AC
        temp_hab.area = area * 282/2180 #real2Image is mm not mm^2, this is mm^2/pixel
        temp_hab.central_angle = fin_angle = (imu_angle + math.degrees(angleBAC)) % 360
        temp_hab.x  = h_x = find_x(fin_angle, AC)
        temp_hab.y  = h_y = find_y(fin_angle, AC)
        temp_hab.sector = find_sector(h_x, h_y)
        temp_hab.path = img

        ret_habs.append(temp_hab)

        HAB_list.append(temp_hab)

        # h_x = self.find_x(self, deg, inch)
        # h_y = self.find_y(self, deg, inch)



        # print("offset angle:", math.degrees(angleBAC), "degree")
        # print("x:",cX,"y:",cY,"area:",area,"hab2edge,mm:",BC,"hab2center,mm:",OC)
        # print("distance from hab centroid to earth center:", AC, "mm")

    # print("OA aka eCenter2PicCenter: 266 mm")
    # print("edge2center:", OB, "mm")
    # print("eCenter2Edge:", AB, "mm")
    return ret_habs


'''
given x and y values in inches, determine sector
coordinte plane is scaled x: [0, 34], y: [0, 33]
with (0,0) inches at the top left of sector 1

returns sector num 1-6 
'''
def find_sector(h_x, h_y):
    
    
    # print(h_x, h_y)

    #returns sector based on hx and hy:
    sector = 0
    if (h_x<=17):
        if(h_y<=11): 
            sector = 1
        elif(h_y>11 and h_y<=22): 
            sector = 3
        else:
            sector = 5
    else:
        if(h_y<=11): 
            sector = 2
        elif(h_y>11 and h_y<=22): 
            sector = 4
        else:
            sector = 6

    
    # return ("Sector: " + str(sector)) 
    return sector

'''
This function makes a COPY of the HAB_list and returns
a new list with the duplicates and near duplicates removed
based on a margin. 
It also sets the list global var cleaned_HABs for easier
access as needed.

should handle all HAB_list with lengths 0+
'''

def remove_doubles():
    in_margin = 1 #sets margin at +-1 inch in all directions from centroid
    new_list = HAB_list[:]

    #handling case of 0 or 1 HABs (nothing to remove)
    if (len(HAB_list)<=1):
        return new_list


    list_len = len(new_list)
    i = 0
    j = 0

    while i<list_len:
        og_hab = new_list[i]
        
        while j<list_len:
            new_hab = new_list[j]
            
            if(og_hab == new_hab):
                j+=1
            
            else:
                if(is_within(og_hab.x, og_hab.y, new_hab.x, new_hab.y,in_margin)):
                    new_list.remove(new_hab)
                    # i-=1 #resets the indexes accounting for removed
                    j-=1
                    list_len-=1
                
                #move forward
                j+=1
        
        i+=1

    global cleaned_HABs
    cleaned_HABs = new_list[:]

    return new_list

def list_to_txt(this_list, txt_name):
    with open(dir_path + txt_name, 'w') as file:
        for hab in this_list:
            file.write(hab.summary() + "\n")


#helper methods


def is_within(x_o, y_o,x_n, y_n, margin):
    if(abs(x_n-x_o)<margin and abs(y_n-y_o)<margin):
        return True
    return False


def find_x(deg, inch):
    theta = deg * math.pi / 180
    d = mm_to_in(inch)
    r_x = math.sin(theta) * d
    h_x = r_x + 17
    return h_x

def find_y(deg, inch):
    theta = deg * math.pi / 180
    d = mm_to_in(inch)
    r_y = math.cos(theta) * d
    h_y = r_y * -1 + 16.5
    return h_y

def mm_to_in (mm) :
    return mm/25.4

def calculateDistance(x1,y1,x2,y2):
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

def cosLawAngle(a, b, c):
    return math.acos((a**2 - b**2 - c**2)/(-2.0*b*c)) #in radian

def cosLawSide(angle, b, c):
    return math.sqrt(b**2 + c**2 - 2.0*b*c*math.cos(angle)) 

'''
This can be called to set the global variables specific to the user
so it only needs to be called once. These values depend on what you
recorded/used in the imaging calibration (see Stephen's instructions)

username = your first name as a string to set img names
r2I = mm/pixel ratio
E2PC = 'earth' to pic center 
(should be around 271 for everyone since same set up)
cenOff = the value you adjusted to move the center line as needed


eg. set_user_values("rhea", 100/258.49564793241683, 271, 45)
eg. set_user_values("stephen", 0.3744906844618852, 271, 27)

'''
def set_user_values(username, r2I, E2PC, cenOff):
    global user, real2Img, E2PicCenter, centerOff
    user = username #this should your first name to set img names
    real2Img = r2I
    E2PicCenter = E2PC
    centerOff = cenOff

#need to actually test this
#Angle order: 0-60-120-180-240-300-30-90-150-210-270-330
def flight_test():
    num_photos  = 0
    deg_est = 0
    zzz = 60 / 6
    #orbit 1
    orbit_end_deg = 300

    while (orbit_end_deg<=330):
        while (deg_est<=orbit_end_deg):
                
            find_HABs(capture_image(), deg_est)
            num_photos += 1
            print(str(num_photos) + "\tdegree: " + str(deg_est) + "\ttime: "+ time.strftime("%H:%M:%S"))
            deg_est+=60 
            time.sleep(zzz-1)
        #it will be at 360=0, so need to take an extra 30/6 = 5 sec
        time.sleep(30/6)
        orbit_end_deg+=30 #orbit 2 300+30=330
        deg_est = deg_est%360 + 30
    
    #test cleaning
    print("done with 2 orbits, checking HAB list")
    print(*HAB_list)
    print("\nafter removal: ")
    print(*remove_doubles())
    return num_photos








'''
you can use this to set the current imu reading instead of 
changing the global var. we're using angle on a 0 to 360 scale.
this should probably be called each time you capture an image.
'''
def set_pic_angle(angle):
    global imu_angle
    imu_angle = angle

if __name__ == "__main__":    
    
    #THIS LINE SHOULD CHANGE PER PERSON
    set_user_values("rhea", 100/258.49564793241683, 271, 45)
    set_pic_angle(45)
    #color test
    find_HABs(capture_image(), imu_angle)


    #flight test
    # input('Press enter to start imaging: ')
    # print("started")
    # n = flight_test()
    # print("done imaging, photos total taken: " + str(n))
    # print("making text file")
    # list_to_txt(cleaned_HABs, user + "_summary.txt")
    # print("finished all processes")

    #testing the remove doubles method
    # find_HABs(capture_image(), imu_angle)
    # find_HABs(capture_image(), imu_angle)
    # print("before removal: ")
    # print(*HAB_list)
    # print("\nafter removal: ")
    # print(*remove_doubles())
    # print("\nold list:")
    # print(*HAB_list)

