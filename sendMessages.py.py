from pickletools import uint8
from controller import Robot, Emitter, Receiver
import struct

robot = Robot()
TimeStep = 32
receiver = robot.getDevice("receiver") # Retrieve the receiver and emitter by device name
emitter = robot.getDevice("emitter")
receiver.enable(TimeStep)

def sendMessage():
    emitter = robot.getDevice("emitter")
    message = bytes(str('Done').encode())
    emitter.send(message)
    print("I've just sent the message")

while robot.step(TimeStep) != -1:
    sendMessage()