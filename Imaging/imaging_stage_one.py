import time
from time import strftime
from picamera import PiCamera
import numpy as np
import cv2
import argparse
import imutils
import math
camera = PiCamera() 
time.sleep(2)

#this entire thing only saves 1 image for now. 
#supposed to be called for each pahse 1 capture


# path = "home/pi/CHARMS/Imaging/test_images/"

'''
DEPENDANTS:
'''
path = "test_images/"
user = "rhea" #replace with your name
real2Img  = 0.3744906844618852 # mm/pixle - subject to change - depending on each person's set-up 
E2PicCenter = 271 #mm - subject to change - depending on each person's set-up
centerOff = 27  
imu_angle = 0 #TODO get this info

HAB_list = []

class HAB:
    def __init__(self):
        self.area = 0
        self.x = 0
        self.y = 0
        self.central_angle = 0
        self.distance = 0
        self.sector = 0
    def __str__(self):
        return str(self.x) + " " + str(self.y) + " \n"
    


def capture_image(imu_angle):
    #capture image
    fileName = user + ".jpg"
    # fileName = strftime("%X%x_" + user + ".jpg") #locale date_locale time_time zone
    camera.capture(path + fileName)
    # return image
    return path + fileName





#TODO rhea: fix this part with the constants
def find_HABs(img, imu_angle, real2Img, E2PicCenter, centerOff):
    #constants
    real2Image_coef = real2Img  #= 0.3744906844618852 # mm/pixle - subject to change - depending on each person's set-up 
    eCenter2PicCenter = E2PicCenter #= 271 #mm - subject to change - depending on each person's set-up
    center_offset = centerOff #27 #pixels - subject to change - depending on each person's set-up
    
    image = cv2.imread(img)
    hsv_img = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    low_bound = np.array([155,25,0]) #TODO rhea: fix these
    up_bound = np.array ([179, 255, 255])
    mask = cv2.inRange(hsv_img, low_bound, up_bound)
    cv2.imshow("mask", mask)
    cv2.waitKey()
    cv2.destroyAllWindows()

    cnts = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)

    threshold = 1000
    red = 0
    
    for c in cnts:
        area = cv2.contourArea(c)
        red+=area
        if(area<threshold):
            continue
        cv2.drawContours(image,[c],-1,(0,255,0),3)
        M =  cv2.moments(c)
        if M["m00"] == 0:
            cX=0
            cY=0
        else:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            
        #drawing 
        cv2.circle(image, (cX, cY), 5, (0, 255, 0), -1)
        cv2.putText(image, "centroid", (cX - 25, cY - 25),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (128, 0, 0), 2)
        # cv2.imshow('Red Mask', red_mask)
        
        # cv2.waitKey()
        # cv2.destroyAllWindows()


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
        temp_hab.area = area * real2Image_coef
        temp_hab.central_angle = fin_angle = imu_angle + math.degrees(angleBAC)
        temp_hab.x  = h_x = find_x(fin_angle, AC)
        temp_hab.y  = h_y = find_y(fin_angle, AC)
        temp_hab.sector = find_sector(h_x, h_y)

        HAB_list.append(temp_hab)

        # h_x = self.find_x(self, deg, inch)
        # h_y = self.find_y(self, deg, inch)



        # print("offset angle:", math.degrees(angleBAC), "degree")
        # print("x:",cX,"y:",cY,"area:",area,"hab2edge,mm:",BC,"hab2center,mm:",OC)
        # print("distance from hab centroid to earth center:", AC, "mm")
        # return math.degrees(angleBAC)
        #return math.degress(angleBAC),d= AC, hab_area

    # print("OA aka eCenter2PicCenter: 266 mm")
    # print("edge2center:", OB, "mm")
    # print("eCenter2Edge:", AB, "mm")
    print(*HAB_list)





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

    #can change this based on what return type needed
    # return ("Sector: " + str(sector)) 
    return sector


#helper methods
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




if __name__ == "__main__":
    find_HABs(capture_image(imu_angle), imu_angle, real2Img, E2PicCenter, centerOff)

