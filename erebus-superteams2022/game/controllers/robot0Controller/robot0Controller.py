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

def send_messages_to_other_team():
        struct_fmt = "T"
        data = "Im done"
        message = struct.pack(struct_fmt, data)
        emitter.send(message)
        print("I've just sent the message! It says: ", message)

while robot.step(TimeStep) != -1:
    wheel_left.setVelocity(5.0)
    wheel_right.setVelocity(5.0)
    emitter.send(bytes('E', "utf-8"))
    send_messages_to_other_team()