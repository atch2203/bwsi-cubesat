from time import sleep
import adcs_main

test = adcs_main.ADCS()

#Read through the entire comments before running the file.

'''
test.calibrate() should run the prompt that will start the calibration
process. Please record these values and save them in a secure place.
'''
mag_calibration = test.calibrate()

'''
BEFORE pressing the enter button after getting your correct values, make sure
to place your cubesat onto the orbiter and point the orbiter at 0 degrees.
'''
sleep(5)
initial_angle = test.initial_angle(test.calculate_yaw(mag_calibration))

'''
After getting the prompt, "Initial angle set", move the orbiter to a desired
angle.

CLOCKWISE : POSITIVE ANGLE
COUNTER-CLOCKWISE: NEGATIVE ANGLE
'''
sleep(5)
print(test.get_yaw(test.calculate_yaw(mag_calibration), initial_angle))
'''Please update me if your angle corresponds to the correct number of 
degrees in which you turned the orbiter.
'''