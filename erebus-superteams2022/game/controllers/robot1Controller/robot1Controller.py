from controller import Robot, Emitter
import struct

robot = Robot()
TimeStep = 32

wheel_left = robot.getDevice("wheel1 motor")
wheel_right = robot.getDevice("wheel2 motor")
wheel_left.setPosition(float('inf'))
wheel_right.setPosition(float('inf'))
receiver = robot.getDevice("receiver") # Retrieve the receiver and emitter by device name
emitter = robot.getDevice("emitter")
receiver.enable(TimeStep)

def recieve_and_decode_messages_from_team():
    if receiver.getQueueLength() > 0:
        message = receiver.getData()
        receiver.nextPacket()
        struct_fmt = "S"
        message = struct.unpack(struct_fmt, message)
        data = {"robot_id:", (message[0])}
        print("Data: ", data)
        return data
    
while robot.step(TimeStep) != -1:
    if recieve_and_decode_messages_from_team() == True:
        wheel_left.setVelocity(5.0)
        wheel_right.setVelocity(5.0)