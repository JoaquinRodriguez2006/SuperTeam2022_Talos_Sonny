import struct
from controller import Robot, Emitter, Receiver

robot = Robot()
TimeStep = 32
receiver = robot.getDevice("receiver") # Retrieve the receiver and emitter by device name
emitter = robot.getDevice("emitter")
receiver.enable(TimeStep)

def sendMessage():
    emitter = robot.getDevice("emitter")
    tupla = ((-16, 12), (-14, 12), (-14, 10), (-14, 8))
    message = (str(tupla)).encode()
    emitter.send(message)
    print("I've just sent the message")

sendMessage()