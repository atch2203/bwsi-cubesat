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


class KeyListener:
    """Object for listening for input in a separate thread"""

    def __init__(self):
        self._input_key = None
        self._listener_thread = None

    def _key_listener(self):
        while True:
            self._input_key = input()

    def start(self):
        """Start Listening"""
        if self._listener_thread is None:
            self._listener_thread = threading.Thread(
                target=self._key_listener, daemon=True
            )
        if not self._listener_thread.is_alive():
            self._listener_thread.start()


    def stop(self):
        """Stop Listening"""
        if self._listener_thread is not None and self._listener_thread.is_alive():
            self._listener_thread.join()

    @property
    def pressed(self):
        "Return whether enter was pressed since last checked" ""
        result = False
        if self._input_key is not None:
            self._input_key = None
            result = True
        return result

class ADCS:

    def calibrate(self):
        key_listener = KeyListener()
        key_listener.start()

        print("Magnetometer Calibration")
        print("Start moving the board in all directions")
        print("When the magnetic Hard Offset values stop")
        print("changing, press ENTER to go to the next step")
        print("Press ENTER to continue...")

        while not key_listener.pressed:
            pass

        mag_x, mag_y, mag_z = sensor1.magnetometer
        min_x = max_x = mag_x
        min_y = max_y = mag_y
        min_z = max_z = mag_z

        while not key_listener.pressed:
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

            if avg_delta == 0:
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
        return mag_calibration
   
    def calculate_yaw(self, mag_calibration):
        magX, magY, magZ = sensor1.magnetometer
        magX = (magX - mag_calibration[0]) * mag_calibration[3]
        magY = (magY - mag_calibration[1]) * mag_calibration[4]
        yaw = (180/np.pi)*np.arctan2(magY, magX)
        return yaw

    def initial_angle(self, yaw):
        #Sets the initial position for plotting and gyro calculations.
        print("Preparing to set initial angle. Please hold the IMU still.")
        time.sleep(5)
        print("Setting angle...")
        angle = yaw
        print("Initial angle set.")
        time.sleep(2)
        print("Initial Angle: ")
        print(angle)
        return angle
    
    def get_yaw(self, yaw, initial_angle):
        if initial_angle > 0:
            return -1 * (yaw - initial_angle)
        return yaw - initial_angle
