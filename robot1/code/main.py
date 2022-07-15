import utilities, state_machines, robot, mapping
from algorithms.expandable_node_grid.bfs import bfs
from algorithms.expandable_node_grid.a_star import a_star_mini_challenge

from agents.closest_position_agent.closest_position_agent import ClosestPositionAgent

from flags import SHOW_DEBUG

# World constants
TIME_STEP = 32
TILE_SIZE = 0.06
TIME_IN_ROUND = 8 * 60


# Components
#Robot
robot = robot.RobotLayer(TIME_STEP)

# Stores, changes and compare states
stateManager = state_machines.StateManager("init")

# Sequence manager
# Resets flags that need to be in a certain value when changing sequence, for example when changing state
def resetSequenceFlags():
    robot.delay_first_time = True
seq = state_machines.SequenceManager(resetFunction=resetSequenceFlags)

# Mapper
mapper = mapping.Mapper(TILE_SIZE)

closest_position_agent = ClosestPositionAgent()


# Variables
do_mapping = False


# Functions
# Sequential functions used frequently
seqPrint = seq.makeSimpleEvent(print)
seqDelaySec = seq.makeComplexEvent(robot.delay_sec)
seqMoveWheels = seq.makeSimpleEvent(robot.move_wheels)
seqRotateToDegs = seq.makeComplexEvent(robot.rotate_to_degs)
seqMoveToCoords = seq.makeComplexEvent(robot.move_to_coords)
seqResetSequenceFlags = seq.makeSimpleEvent(resetSequenceFlags)

# Calculates offsets in the robot position, in case it doesn't start perfectly centerd
def calibratePositionOffsets():
    actualTile = [robot.position[0] // TILE_SIZE, robot.position[1] // TILE_SIZE]
    robot.position_offsets = [
        round((actualTile[0] * TILE_SIZE) - robot.position[0]) + TILE_SIZE // 2,
        round((actualTile[1] * TILE_SIZE) - robot.position[1]) + TILE_SIZE // 2]
    robot.position_offsets = [robot.position_offsets[0] % TILE_SIZE, robot.position_offsets[1] % TILE_SIZE]
    print("positionOffsets: ", robot.position_offsets)

def seqCalibrateRobotRotation():
    # Calibrates the robot rotation using the gps
    if seq.simpleEvent():
        robot.auto_decide_rotation = False
    seqMoveWheels(-1, -1)
    seqDelaySec(0.1)
    if seq.simpleEvent(): robot.rotation_sensor = "gps"
    seqMoveWheels(1, 1)
    seqDelaySec(0.1)
    if seq.simpleEvent(): robot.rotation_sensor= "gyro"
    seqDelaySec(0.1)
    seqMoveWheels(0, 0)
    seqMoveWheels(-1, -1)
    seqDelaySec(0.1)
    seqMoveWheels(0, 0)
    if seq.simpleEvent():
        robot.auto_decide_rotation = True

initial_position = robot.position

def seqMoveToRelativeCoords(x, y):
    global initial_position
    if seq.simpleEvent():
        initial_position = [round(p / TILE_SIZE) * TILE_SIZE for p in robot.position]
    return seqMoveToCoords((initial_position[0] + x, initial_position[1] + y))

def seqMoveToRelativeTile(x, y):
    node = mapper.robot_node
    tile = [node[0] // 2 + x, node[1] // 2 + y]
    return seqMoveToCoords([tile[0] * TILE_SIZE, tile[1] * TILE_SIZE])

def is_complete(grid, robot_node):
        possible_nodes = bfs(grid, robot_node, 500)
        if len(possible_nodes) == 0:
            return True
        return False

def is_in_checkpoint(grid, robot_node):
    for adj in ((1, 1), (1, -1), (-1, 1), (-1, -1)):
        if grid.get_node((robot_node[0] + adj[0], robot_node[1] + adj[1])).tile_type == "checkpoint":
            return True

def get_final_path():
    raw_path = a_star_mini_challenge(mapper.node_grid, mapper.robot_node, mapper.start_node)
    final_path = []
    for node in raw_path:
        final_path.append([(n - rn) // 2 for n, rn in zip(node, mapper.robot_node)])
    if SHOW_DEBUG:
        print("Final path: ", final_path)
    return final_path

# Each timeStep
while robot.do_loop():
    # Updates robot position and rotation, sensor positions, etc.
    robot.update()
    
    # Loads data to mapping
    if do_mapping:
        lidar_point_cloud = robot.get_detection_point_cloud()
        images = robot.get_camera_images()
        #utilities.save_image(images[1], "camera_image_center.png")
        mapper.update(lidar_point_cloud, images, robot.position, robot.rotation, current_time=robot.time)

    else:
        mapper.update(robot_position=robot.position, robot_rotation=robot.rotation, current_time=robot.time)
    
    if is_in_checkpoint(mapper.node_grid, mapper.robot_node):
        seq.resetSequence()
        stateManager.changeState("end")

    # Updates state machine
    if not stateManager.checkState("init"):
        if SHOW_DEBUG:
            print("stuck_counter: ", robot.stuck_counter)
        if robot.is_stuck():
            if SHOW_DEBUG:
                print("FRONT BLOCKED")
            mapper.block_front_vortex(robot.rotation)
            if not stateManager.checkState("stuck"):
                seq.resetSequence()
                stateManager.changeState("stuck")

    if SHOW_DEBUG:
        print("state: ", stateManager.state)

    utilities.tune_hsv_filter(robot.get_camera_images()[1])

    # Runs once when starting the game
    if stateManager.checkState("init"):
        seq.startSequence()
        seqDelaySec(0.5)
        # Calculates offsets in the robot position, in case it doesn't start perfectly centerd
        seq.simpleEvent(calibratePositionOffsets)
        # Informs the mapping components of the starting position of the robot
        seq.simpleEvent(mapper.register_start, robot.position)
        # Calibrates the rotation of the robot using the gps
        seqCalibrateRobotRotation()
        # Starts mapping walls
        if seq.simpleEvent():
            do_mapping = True
        # Changes state and resets the sequence
        seq.simpleEvent(stateManager.changeState, "explore")
        seq.seqResetSequence()

    elif stateManager.checkState("stop"):
        seq.startSequence()
        seqMoveWheels(0, 0)

    # Explores and maps the maze
    elif stateManager.checkState("explore"):
        seq.startSequence()

        grid = mapper.get_node_grid()
        move = closest_position_agent.get_action(grid)
        if SHOW_DEBUG:
            print("move: ", move)
        node = mapper.robot_node

        if seqMoveToRelativeTile(move[0], move[1]):
            mapper.set_robot_node(robot.position)
        seq.seqResetSequence()

        if SHOW_DEBUG:
            print("rotation:", robot.rotation)
            print("position:", robot.position)
    
    elif stateManager.checkState("go_to_exit"):
        seq.startSequence()
        if seqMoveToRelativeTile(0, 0):
            mapper.set_robot_node(robot.position)
        seq.seqResetSequence()
    
    elif stateManager.checkState("end"):
        print("END")
        final_path = get_final_path()
        robot.comunicator.sendPathToRobot(final_path)
        robot.comunicator.sendEndOfPlay()
    
    elif stateManager.checkState("stuck"):
        if SHOW_DEBUG:
            print("IS IN STUCK")
        seq.startSequence()
        if seq.simpleEvent():
            robot.auto_decide_rotation = False
            robot.rotation_sensor = "gyro"
        seqMoveWheels(-0.5, -0.5)
        seqDelaySec(0.2)
        seqMoveWheels(0, 0)
        if seq.simpleEvent():
            robot.auto_decide_rotation = True
        seq.simpleEvent(stateManager.changeState, "explore")
        seq.seqResetSequence()

    if SHOW_DEBUG:
        print("robot time:", robot.comunicator.remainingTime)
    robot.comunicator.update()
        


