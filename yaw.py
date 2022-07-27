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
SAMPLE_SIZE = 500

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

    #return (180/np.pi)*np.arctan2(magY, magX)

def yaw_gy(prev_angle, delT, gyro, accDataZ):
    #TODO
    #yaw = prev_angle + gyro * delT
    yaw = 0.95 * (prev_angle + gyro * delT) + (0.05) * (accDataZ)
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
    magX = magX - mag_offset[0]
    magY = magY - mag_offset[1]
    magZ = magZ - mag_offset[2]
    roll = roll_am(accelX, accelY,accelZ)
    pitch = pitch_am(accelX,accelY,accelZ)
    yaw = yaw_am(accelX,accelY,accelZ,magX,magY,magZ)
    print("Initial angle set.")
    return [roll,pitch,yaw]

def calibrate_mag():
    key_listener = KeyListener()
    key_listener.start()
    offset = [0, 0, 0]

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

        field_x = (max_x - min_x) / 2
        field_y = (max_y - min_y) / 2
        field_z = (max_z - min_z) / 2

        print(
            "Hard Offset:  X: {0:8.2f}, Y:{1:8.2f}, Z:{2:8.2f} uT".format(
                offset_x, offset_y, offset_z
            )
        )
        print(
            "Field:        X: {0:8.2f}, Y:{1:8.2f}, Z:{2:8.2f} uT".format(
                field_x, field_y, field_z
            )
        )
        print("")
        time.sleep(0.01)

    mag_calibration = (offset_x, offset_y, offset_z)
    offset[0] = offset_x
    offset[1] = offset_y
    offset[2] = offset_z

    print("Calibration complete.")

    return offset

def calibrate_gyro():
    key_listener = KeyListener()
    key_listener.start()
    #TODO
    offset = [0, 0, 0]

    gyro_x, gyro_y, gyro_z = sensor2.gyroscope
    min_x = max_x = gyro_x
    min_y = max_y = gyro_y
    min_z = max_z = gyro_z

    print("")
    print("")
    print("Gyro Calibration")
    print("Place your gyro on a FLAT stable surface.")
    print("Press ENTER to continue...")
    while not key_listener.pressed:
        pass

    for _ in range(SAMPLE_SIZE):
        gyro_x, gyro_y, gyro_z = sensor2.gyroscope

        print(
            "Gyroscope: X: {0:8.2f}, Y:{1:8.2f}, Z:{2:8.2f} rad/s".format(
                gyro_x, gyro_y, gyro_z
            )
        )

        min_x = min(min_x, gyro_x)
        min_y = min(min_y, gyro_y)
        min_z = min(min_z, gyro_z)

        max_x = max(max_x, gyro_x)
        max_y = max(max_y, gyro_y)
        max_z = max(max_z, gyro_z)

        offset_x = (max_x + min_x) / 2
        offset_y = (max_y + min_y) / 2
        offset_z = (max_z + min_z) / 2

        noise_x = max_x - min_x
        noise_y = max_y - min_y
        noise_z = max_z - min_z

        print(
            "Zero Rate Offset:  X: {0:8.2f}, Y:{1:8.2f}, Z:{2:8.2f} rad/s".format(
                offset_x, offset_y, offset_z
            )
        )
        print(
            "Rad/s Noise:       X: {0:8.2f}, Y:{1:8.2f}, Z:{2:8.2f} rad/s".format(
                noise_x, noise_y, noise_z
            )
        )
        print("")

    gyro_calibration = (offset_x, offset_y, offset_z)
    offset[0] = (180/np.pi) * offset_x 
    offset[1] = (180/np.pi) * offset_y
    offset[2] = (180/np.pi) * offset_z

    print("Calibration complete.")
    return offset