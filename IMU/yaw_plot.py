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
from abstract_adcs import ADCS


i2c = busio.I2C(board.SCL, board.SDA)
sensor1 = adafruit_fxos8700.FXOS8700(i2c)
sensor2 = adafruit_fxas21002c.FXAS21002C(i2c)

fig = plt.figure()
ax = fig.add_subplot(1,1,1)
xs = []
y = []
y2 = []
adcs = ADCS()
rpy = [0,0,0]

def animate(i, xs, type, y, y2):
    xs.append(time.time())

    if type == 'am':
       adcs.update_yaw_average()
       y.append(adcs.get_yaw())
       y2.append(adcs.get_raw_yaw())
       ax.clear()
       ax.plot(xs,y,label = "Yaw")
       ax.plot(xs,y2,label = "Yaw")
       plt.title('Yaw, Using Accelerometer and Magnetometer')
       plt.ylabel('deg')

    else:
       print("Not a valid argument.")
       return

    #Keep the plot from being too long
    xs = xs[-20:]
    y = y[-20:]
    y2 = y2[-20:]
    plt.grid()
    plt.legend()
    plt.xlabel('Time')

def plot_data(type = 'am'):
    adcs.calibrate(15)
    adcs.initial_angle(False)
    ani = animation.FuncAnimation(fig, animate, fargs =(xs,type,y,y2), interval = 1000)
    plt.show()

if __name__ == '__main__':
    plot_data(*sys.argv[1:])
