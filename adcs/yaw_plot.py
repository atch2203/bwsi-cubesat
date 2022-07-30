import adafruit_fxos8700
import adafruit_fxas21002c
import time
import os
import board
import busio
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
import numpy as np
import sys
from yaw import *


i2c = busio.I2C(board.SCL, board.SDA)
sensor1 = adafruit_fxos8700.FXOS8700(i2c)
sensor2 = adafruit_fxas21002c.FXAS21002C(i2c)

fig = plt.figure()
ax = fig.add_subplot(1,1,1)
xs = []
y = []

rpy = [0,0,0]

def animate(i, xs, type, y, mag_offset, gyro_offset, initial_angle):
    if len(y) == 0:
        prev_ang = 0
    else:
        c = y[-1]
        prev_ang = c
        
    accelX, accelY, accelZ = sensor1.accelerometer #m/s^2
    magX, magY, magZ = sensor1.magnetometer #gauss
    #Calibrate magnetometer readings
    magX = (magX - mag_offset[0]) * mag_offset[3]
    magY = (magY - mag_offset[1]) * mag_offset[4] 
    magZ = (magZ - mag_offset[2]) * mag_offset[5] 
    accgyroX, accgyroY, accgyroZ = sensor2.gyroscope #rad/s
    gyroX = accgyroX * (180/np.pi) - gyro_offset[0]
    gyroY = accgyroY * (180/np.pi) - gyro_offset[1]
    gyroZ = accgyroZ * (180/np.pi) - gyro_offset[2]
    xs.append(time.time())

    if type == 'am':
       y.append(yaw_am(accelX,accelY,accelZ,magX,magY,magZ) - initial_angle)
       ax.clear()
       ax.plot(xs,y,label = "Yaw")
       plt.title('Yaw, Using Accelerometer and Magnetometer')
       plt.ylabel('deg')

    elif type =='gyro':
       if len(xs) == 1:
           y.append(prev_ang)

       else:
           delT = xs[-1] - xs[-2]
           y.append(yaw_gy(prev_ang,delT,gyroZ,accgyroZ))

       ax.clear()
       ax.plot(xs,y,label = "Yaw")
       plt.title('Yaw, Using Gyro')
       plt.ylabel('deg')

    else:
       print("Not a valid argument.")
       return

    #Keep the plot from being too long
    xs = xs[-20:]
    y = y[-20:]
    plt.grid()
    plt.legend()
    plt.xlabel('Time')

def plot_data(type = 'am'):
    mag_offset = calibrate_mag()
    initial_angle = set_initial(mag_offset)
    gyro_offset = calibrate_gyro()
    ani = animation.FuncAnimation(fig, animate, fargs =(xs,type,y,mag_offset,gyro_offset,initial_angle), interval = 1000)
    plt.show()

if __name__ == '__main__':
    plot_data(*sys.argv[1:])