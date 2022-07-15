from controller import Robot
import struct

robot = Robot()
timeStep = 32
start = 0

# Declare communication link between the robot and the controller
emitter = robot.getDevice("emitter")

if robot.step(timeStep) != -1:
    start = robot.getTime()

while robot.step(timeStep) != -1:
    if (robot.getTime() - start) > 3:
        message = struct.pack('c', 'E'.encode())
        emitter.send(message)
        break
