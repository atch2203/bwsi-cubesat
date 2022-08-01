import numpy as np
import cv2
import argparse
import imutils
import math

#command to run the file: python3 imaging_test.py --image <image_name>.jpg





def calculateDistance(x1,y1,x2,y2):
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

def cosLawAngle(a, b, c):
    return math.acos((a**2 - b**2 - c**2)/(-2.0*b*c)) #in radian

def cosLawSide(angle, b, c):
    return math.sqrt(b**2 + c**2 - 2.0*b*c*math.cos(angle))

def find_centralAngle(image):
    #constants
    real2Image_coef = 0.3744906844618852 # mm/pixle - subject to change - depending on each person's set-up 
    eCenter2PicCenter = 271 #mm - subject to change - depending on each person's set-up
    center_offset = 27 #pixels - subject to change - depending on each person's set-up
        
    hsv_img = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    low_bound = np.array([155,25,0])
    up_bound = np.array ([179, 255, 255])
    mask = cv2.inRange(hsv_img, low_bound, up_bound)
#   cv2.imshow("mask", mask)
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
        
        print("offset angle:", math.degrees(angleBAC), "degree")
        print("x:",cX,"y:",cY,"area:",area,"hab2edge,mm:",BC,"hab2center,mm:",OC)
        print("distance from hab centroid to earth center:", AC, "mm")
        return math.degrees(angleBAC)
        #return math.degress(angleBAC),d= AC, hab_area
 
    print("OA aka eCenter2PicCenter: 266 mm")
    print("edge2center:", OB, "mm")
    print("eCenter2Edge:", AB, "mm")

'''
enter as degree, inch
output is a number for sector
'''
def find_sector(deg,inch):
    theta = deg * math.pi / 180
    d = mm_to_in(inch)
    
    # o_x = 0 #17
    # o_y = 0 #16.5

    r_x = math.sin(theta) * d
    r_y = math.cos(theta) * d

    # r_x = o_x + (d_x)
    # r_y = o_y + (d_y)

    h_x = r_x + 17
    h_y = r_y * -1 + 16.5

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

def mm_to_in (mm) :
    return mm/25.4






#Main code that is being run
def load_img(image_file):
    image = cv2.imread('/home/pi/' + image_file) #Path to the file
    find_centralAngle(image)
    cv2.imshow("Image", image)
    cv2.waitKey(0)
    
#input image: python3 imaging_test.py --image <image_name>.jpg
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", help = "/home/pi/") #path to the folder of the image
args = vars(ap.parse_args())
load_img(args["image"])

    

