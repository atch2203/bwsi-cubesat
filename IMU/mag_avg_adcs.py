import time
import threading
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


class ADCS:

    def calibrate(self, t):

        i2c = busio.I2C(board.SCL, board.SDA)
        sensor1 = adafruit_fxos8700.FXOS8700(i2c)
        sensor2 = adafruit_fxas21002c.FXAS21002C(i2c)

        print("Magnetometer Calibration")
        print("Start moving the board in all directions")
        print("When the magnetic Hard Offset values stop")

        start_time = time.time()

        mag_x, mag_y, mag_z = sensor1.magnetometer
        min_x = max_x = mag_x
        min_y = max_y = mag_y
        min_z = max_z = mag_z

        while time.time() - start_time < t:
            mag_x, mag_y, mag_z = sensor1.magnetometer

            print(
                "Magnetometer: X: {0:8.2f}, Y:{1:8.2f}, Z:{2:8.2f} uT".format(
                    mag_x, mag_y, mag_z
                )
            )

            min_x = min(min_x, mag_x)
            min_y = min(min_y, mag_y)
            min_z = min(min_z, mag_z)

            max_x = max(max_x, mag_x)
            max_y = max(max_y, mag_y)
            max_z = max(max_z, mag_z)

            offset_x = (max_x + min_x) / 2
            offset_y = (max_y + min_y) / 2
            offset_z = (max_z + min_z) / 2

            #soft iron calibration
            avg_delta_x = (max_x - min_x) / 2
            avg_delta_y = (max_y - min_y) / 2
            avg_delta_z = (max_z - min_z) / 2

            avg_delta = (avg_delta_x + avg_delta_y + avg_delta_z) / 3

            if avg_delta == 0 or avg_delta_x == 0 or avg_delta_y == 0 or avg_delta_z == 0:
                continue
            else:
                scale_x = avg_delta / avg_delta_x
                scale_y = avg_delta / avg_delta_y
                scale_z = avg_delta / avg_delta_z

            print(
                "Hard Offset:  X: {0:8.2f}, Y:{1:8.2f}, Z:{2:8.2f} uT".format(
                    offset_x, offset_y, offset_z
                )
            )
            print(
                "Field:        X: {0:8.2f}, Y:{1:8.2f}, Z:{2:8.2f} uT".format(
                    avg_delta_x, avg_delta_y, avg_delta_z
                )
            )
            print("")
            time.sleep(0.01)

        mag_calibration = (offset_x, offset_y, offset_z, scale_x, scale_y, scale_z)

        print("Calibration complete.")

        print(mag_calibration)
        self.mag_calibration = mag_calibration
    
    def calculate_raw_yaw(self):
        magX, magY, magZ = sensor1.magnetometer
        magX = (magX - self.mag_calibration[0]) * self.mag_calibration[3]
        magY = (magY - self.mag_calibration[1]) * self.mag_calibration[4]
        yaw = (180/np.pi)*np.arctan2(magY, magX)
        return yaw


    def calculate_yaw(self):
        magX = self.get_magX()
        magY = self.get_magY()
        magX = (magX - self.mag_calibration[0]) * self.mag_calibration[3]
        magY = (magY - self.mag_calibration[1]) * self.mag_calibration[4]
        yaw = (180/np.pi)*np.arctan2(magY, magX)
        return yaw

    def initial_angle(self, fast):
        #Sets the initial position for plotting and gyro calculations.
        print("Preparing to set initial angle. Please hold the IMU still.")
        time.sleep(0 if fast else 5)    
        self.magX_list = np.zeros(9)
        self.magY_list = np.zeros(9)
        self.sma_diff_listx = np.zeros(4)
        self.sma_diff_listy = np.zeros(4)
        print("Setting angle...")
        for i in range(10):
            self.update_yaw()
        self.angle = self.calculate_yaw()
        print("Initial angle set.")
        time.sleep(0 if fast else 2)
        print("Initial Angle: ")
        print(self.angle)
        self.angle_list = np.zeros(4)
        self.sma_diff_list = np.zeros(2)

    def get_raw_yaw(self):
        ret = self.calculate_raw_yaw() - self.angle
        if ret > 370:
            ret -= 360
        elif ret < -10:
            ret += 360
        return ret

    def get_avg_yaw(self):
        ret = self.calculate_yaw() - self.angle
        if ret > 370:
            ret -= 360
        elif ret < -10:
            ret += 360
        return ret
    
    def update_yaw(self):
        magX, magY, magZ = sensor1.magnetometer
        self.magX_list = np.append(self.magX_list[1:], magX)
        self.magY_list = np.append(self.magY_list[1:], magY)

    def simple_moving_average(self, list, n):
        return np.mean(list[-n:]) 
    
#    def update_yaw_average(self):
#        self.update_yaw()
#        sma1x = self.simple_moving_average(self.magX_list, 9)
#        sma2x = self.simple_moving_average(self.magX_list, 4)
#        sma1y = self.simple_moving_average(self.magY_list, 9)
#        sma2y = self.simple_moving_average(self.magY_list, 4)
#        sma_diffx = 2 * sma2x - sma1x
#        sma_diffy = 2 * sma2y - sma1y
#        self.sma_diff_listx = np.append(self.sma_diff_listx[1:], sma_diffx)
#        self.sma_diff_listy = np.append(self.sma_diff_listy[1:], sma_diffy)
    
    def get_magX(self):
        return self.simple_moving_average(self.magX_list, 3)

    def get_magY(self):
        return self.simple_moving_average(self.magY_list, 3)

#    def get_yaw(self):
#        return min(180, max(-180, self.simple_moving_average(self.sma_diff_list, 2)))

    def update_yaw_average(self):
        self.update_yaw()

    def get_yaw(self):
        return self.get_avg_yaw()

