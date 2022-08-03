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

#this entire thing only saves 1 image for now. 
#supposed to be called for each pahse 1 capture


# path = "home/pi/CHARMS/Imaging/test_images/"

'''
CONSTANTS:
'''
path = "test_images/"
user = "rhea" #replace with your name
real2Img = 100/258.49564793241683 # 0.3744906844618852 # mm/pixle - subject to change - depending on each person's set-up
E2PicCenter = 271 #mm - subject to change - depending on each person's set-up
centerOff = 45 


'''
Figure this out how to change it
'''
imu_angle = 0 #TODO get this info
# real2Img  = 0.3744906844618852 # mm/pixle - subject to change - depending on each person's set-up 
# E2PicCenter = 271 #mm - subject to change - depending on each person's set-up
# centerOff = 27  


HAB_list = []

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
    


def capture_image(imu_angle):
    #capture image
    timestr = time.strftime("%Y%m%d_%H%M%S")
    fileName = user + timestr + ".jpg"
    # fileName = strftime("%X%x_" + user + ".jpg") #locale date_locale time_time zone
    camera.capture(path + fileName)
    # return image
    return path + fileName





#TODO rhea: fix this part with the constants
'''
finds HAB location supplied img path, imu_angle, other constants
saves hab object 
'''
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

    cv2.imshow("mask", mask) #comment out after integration
    cv2.waitKey() #comment out after integration
    cv2.destroyAllWindows() #comment out after integration

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
        cv2.drawContours(image,[c],-1,(0,255,0),3) #can comment out after completing integration
        M =  cv2.moments(c)
        if M["m00"] == 0:
            cX=0
            cY=0
        else:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            
        #drawing 
        cv2.circle(image, (cX, cY), 5, (0, 255, 0), -1) #comment out after completing integration
        cv2.putText(image, "centroid", (cX - 25, cY - 25),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (128, 0, 0), 2) #same as above
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
        temp_hab.area = area * 282/2392.5 #real2Image is mm not mm^2, this is mm^2/pixel
        temp_hab.central_angle = fin_angle = imu_angle + math.degrees(angleBAC)
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


def remove_doubles():
    in_margin = 1 #sets margin at +-1 inch in all directions from centroid
    new_list = HAB_list[:]

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

    return new_list





        



def is_within(x_o, y_o,x_n, y_n, margin):
    if(abs(x_n-x_o)<margin and abs(y_n-y_o)<margin):
        return True
    return False



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
    # real2Img  = 0.3744906844618852 # mm/pixle - subject to change - depending on each person's set-up 
    # E2PicCenter = 271 #mm - subject to change - depending on each person's set-up
    # centerOff = 27  
    # imu_angle = 0
    
    # find_HABs("test_images/light3.jpg", imu_angle, real2Img, E2PicCenter, centerOff)

    
    find_HABs(capture_image(imu_angle), imu_angle, real2Img, E2PicCenter, centerOff)
    find_HABs(capture_image(imu_angle), imu_angle, real2Img, E2PicCenter, centerOff)
    print("before removal: ")
    print(*HAB_list)
    print("\nafter removal: ")
    print(*remove_doubles())
    print("\nold list:")
    print(*HAB_list)

