import cv2
import argparse

ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", help = "/home/pi/CHARMS_local/Images")
args = vars(ap.parse_args())
image = cv2.imread(args["image"])


cv2.putText(image, "Central angle:" + " " + "<str(hab.distance>" + " " + "degrees", (25,600), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)
cv2.putText(image, "Sector:" + " " + "str(<hab.sector>)", (25,630), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)
cv2.putText(image, "Area:" + " " + "str(<hab.area>)" + " " + "mm", (25,660), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)

cv2.imshow('text added',image)
cv2.waitKey(0)
