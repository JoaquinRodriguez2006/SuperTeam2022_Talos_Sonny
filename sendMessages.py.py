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
    message = ('Done').encode()
    emitter.send(message)
    print("I've just sent the message")


sendMessage()
print("i've just sent the message")
