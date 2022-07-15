# Import all relevant libraries
from controller import Robot
import math
import struct
import time

# If you would like to use the camera to detect visual victims, set usecamera to True. This requires opencv to be installed.
usecamera = True
try:
    import cv2
    import numpy as np
    viewHSV = True

    usecamera = True

    print("Camera-based visual victim detection is enabled.")

except:
    print("[WARNING] Since OpenCV and numpy is not installed, the visual victim detection is turned off. \
        Run 'pip install opencv-python' to install OpenCV and 'pip install numpy' on your terminal/command line.\
        If you have python2, try 'pip3 install' rather than 'pip install'. ")

# Set RGB colours of the swamp and hole to avoid them
# These should be calibrated to match the environment
hole_colour = b';;@\xff'
swamp_colour = b'555\xff'

# Simulation time step and the maximum velocity of the robot
timeStep = 32
max_velocity = 2.0


# Threshold for detecting the wall
sensor_value = 0.05

# Threshold for the victim being close to the wall
victimProximity = 0.1

# Default setting for the "messageSent" variable
messageSent = True

# Variables related to timers and delays
startTime = 0
duration = 0
victimDetectedGlobal = True
victimTimer = 0

# Create a robot instance from the imported robot class
robot = Robot()

TimeStep = 32
receiver = robot.getDevice("receiver") # Retrieve the receiver and emitter by device name
emitter = robot.getDevice("emitter")
receiver.enable(TimeStep)

# Define the wheels
wheel1 = robot.getDevice("wheel1 motor")   # Create an object to control the left wheel
wheel2 = robot.getDevice("wheel2 motor") # Create an object to control the right wheel


# Declare communication link between the robot and the controller
emitter = robot.getDevice("emitter")

# Declare GPS
gps = robot.getDevice("gps")
gps.enable(timeStep)


# [left wheel speed, right wheel speed]
speed1 = max_velocity
speed2 = max_velocity
wheel1.setPosition(float("inf"))
wheel2.setPosition(float("inf"))

# Store when the program began
program_start = robot.getTime()

# Setting the speed to steer right towards the victim
def turn_right_to_victim():
    #set left wheel speed
    speed1 = 1 * max_velocity

    #set right wheel speed
    speed2 = 0.8 * max_velocity

# Setting the speed to steer left towards the victim
def turn_left_to_victim():
    #set left wheel speed
    speed1 = 0.8 * max_velocity

    #set right wheel speed
    speed2 = 1 * max_velocity

# Setting the speed to move backwards
def move_backwards():
    #set left wheel speed
    speed1 = -0.5 * max_velocity

    #set right wheel speed
    speed2 = -0.7 * max_velocity

# Stop the robot
def stop():
    #set left wheel speed
    speed1 = 0

    #set right wheel speed
    speed2 = 0

# Steer the robot right
def turn_right():
    #set left wheel speed
    speed1 = 0.6 * max_velocity

    #set right wheel speed
    speed2 = -0.2 * max_velocity

# Steer the robot left
def turn_left():
    #set left wheel speed
    speed1 = -0.2 * max_velocity

    #set right wheel speed
    speed2 = 0.6 * max_velocity

# Spin the robot on its spot
def spin():
    #set left wheel speed
    speed1 = 0.6 * max_velocity

    #set right wheel speed
    speed2 = -0.6 * max_velocity

def indietro():
    speed1 = -6.28
    speed2 = -6.28

    print(str(speed1))
    print(str(speed2))

def getQueueLength_and_data():
    queueLength = receiver.getQueueLength()
    if queueLength >= 1:
        data = receiver.getData()
        print(data[1:10])  # [1:10]
        if data:
            print("I have to start moving now")
    else:
        return False

################################################################
#                                                              #
#############   Main loop starts here   ########################
#                                                              #
################################################################

while robot.step(timeStep) != -1:
    if getQueueLength_and_data():
        move_backwards()
    