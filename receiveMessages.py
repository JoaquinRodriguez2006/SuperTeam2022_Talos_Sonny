from controller import Robot, Emitter, Receiver
import struct
import numpy

robot = Robot()
TimeStep = 32
receiver = robot.getDevice("receiver") # Retrieve the receiver and emitter by device name
emitter = robot.getDevice("emitter")
receiver.enable(TimeStep)

def getQueueLength_and_data():
    queueLength = receiver.getQueueLength()
    print(queueLength)
    if queueLength >= 1:
        data = receiver.getData()
        if data:
            print("I have to start moving now")
    else:
        return False
            

while robot.step(TimeStep) != -1:
    contador = 1
    if contador == 1:
        getQueueLength_and_data()
        contador += 1