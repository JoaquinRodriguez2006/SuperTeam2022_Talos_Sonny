from controller import Robot, Emitter, Receiver
import struct
import numpy

robot = Robot()
TimeStep = 32
receiver = robot.getDevice("receiver") # Retrieve the receiver and emitter by device name
emitter = robot.getDevice("emitter")
receiver.enable(TimeStep)
class message_sender():
    def __init__(self):
        self.robot = robot()

    def sendMessage():
        emitter = robot.getDevice("emitter")
        data = ['im done']
        emitter.send(data)
        print("I've just sent the message")

class message_receiver():
    def __init__(self):
        self.robot = Robot()
        self.receiver = Receiver()
    
    def getQueueLength(queueLength):
        queueLength = receiver.getQueueLength()
        print(queueLength)
        if queueLength >= 1:
            return True
    
    def getData(queueLength):
        if queueLength:
            data = receiver.getData()
            if data:
                print("I have to start moving now")

message_sender.sendMessage()