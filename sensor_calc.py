#sensor_calc.py
import time
import numpy as np
import adafruit_fxos8700
import adafruit_fxas21002c
import time
import os
import board
import busio

i2c = busio.I2C(board.SCL, board.SDA)
sensor1 = adafruit_fxos8700.FXOS8700(i2c)
sensor2 = adafruit_fxas21002c.FXAS21002C(i2c)


#Activity 1: RPY based on accelerometer and magnetometer
def roll_am(accelX,accelY,accelZ):
    #TODO
    roll = np.arctan2(accelY, np.sqrt(np.power(accelX, 2) + np.power(accelZ, 2)))
    return (180/np.pi) * roll

def pitch_am(accelX,accelY,accelZ):
    #TODO
    pitch = np.arctan2(accelX, np.sqrt(np.power(accelY, 2) + np.power(accelZ, 2)))
    return (180/np.pi) * pitch

def yaw_am(accelX,accelY,accelZ,magX,magY,magZ):
    #TODO
    mag_x = magX * np.cos(pitch_am(accelX, accelY, accelZ)) + magY * np.sin(roll_am(accelX, accelY, accelZ)) + magZ * np.cos(roll_am(accelX, accelY, accelZ)) * np.sin(pitch_am(accelX, accelY, accelZ))
    mag_y = magY * np.cos(roll_am(accelX, accelY, accelZ)) - magY * np.sin(roll_am(accelX, accelY, accelZ))
    return (180/np.pi)*np.arctan2(-mag_y, mag_x)

#Activity 2: RPY based on gyroscope
def roll_gy(prev_angle, delT, gyro):
    #TODO
    roll = prev_angle + gyro * delT
    return roll

def pitch_gy(prev_angle, delT, gyro):
    #TODO
    pitch = prev_angle + gyro * delT
    return pitch
    
def yaw_gy(prev_angle, delT, gyro):
    #TODO
    yaw = prev_angle + gyro * delT
    return yaw

def set_initial(mag_offset):
    #Sets the initial position for plotting and gyro calculations.
    print("Preparing to set initial angle. Please hold the IMU still.")
    time.sleep(3)
    print("Setting angle...")
    accelX, accelY, accelZ = sensor1.accelerometer #m/s^2
    magX, magY, magZ = sensor1.magnetometer #gauss
    #Calibrate magnetometer readings. Defaults to zero until you
    #write the code
    mag_offset = calibrate_mag()
    magX = magX - mag_offset[0]
    magY = magY - mag_offset[1]
    magZ = magZ - mag_offset[2]
    roll = roll_am(accelX, accelY,accelZ)
    pitch = pitch_am(accelX,accelY,accelZ)
    yaw = yaw_am(accelX,accelY,accelZ,magX,magY,magZ)
    print("Initial angle set.")
    return [roll,pitch,yaw]

def calibrate_mag():
    offset = [0, 0, 0]
    mag_values = np.empty((100, 3))
    #TODO: Set up lists, time, etc
    print("Preparing to calibrate magnetometer. Please wave around.")
    time.sleep(3)
    print("Calibrating...")
    #TODO: Calculate calibration constants
    offset[0] = (min(mag_values[:][0].tolist()) + max(mag_values[:][0].tolist())) / 2
    offset[1] = (min(mag_values[:][1].tolist()) + max(mag_values[:][1].tolist())) / 2
    offset[2] = (min(mag_values[:][2].tolist()) + max(mag_values[:][2].tolist())) / 2
    print("Calibration complete.")
    return offset

def calibrate_gyro():
    #TODO
    offset = [0, 0, 0]
    gyro_values = np.empty((100, 3))
    print("Preparing to calibrate gyroscope. Put down the board and do not touch it.")
    time.sleep(3)
    print("Calibrating...")
    #TODO
    offset[0] = (min(gyro_values[:][0].tolist()) + max(gyro_values[:][0].tolist())) / 2
    offset[1] = (min(gyro_values[:][1].tolist()) + max(gyro_values[:][1].tolist())) / 2
    offset[2] = (min(gyro_values[:][2].tolist()) + max(gyro_values[:][2].tolist())) / 2
    print("Calibration complete.")
    return offset
