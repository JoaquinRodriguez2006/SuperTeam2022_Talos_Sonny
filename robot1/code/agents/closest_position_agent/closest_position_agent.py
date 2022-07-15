from agents.agent import Agent
import utilities

from algorithms.expandable_node_grid.a_star import a_star
from algorithms.expandable_node_grid.bfs import bfs, is_bfs_addable
from algorithms.expandable_node_grid.traversable import is_traversable

from flags import SHOW_DEBUG

class ClosestPositionAgent(Agent):
    def __init__(self):
        super().__init__(["up", "down", "left", "right"])
        self.current_robot_node = self.previous_robot_node = None
        self.best_node = [None, None]
        self.a_star_path = []
        self.a_star_index = 0

        self.checkpoint_node = None

    def find_robot_node(self, grid):
        for y, row in enumerate(grid.grid):
            for x, node in enumerate(row):
                if node.is_robots_position:
                    return [x - grid.offsets[0], y - grid.offsets[1]]
    
    def find_start_node(self, grid):
        for y, row in enumerate(grid.grid):
            for x, node in enumerate(row):
                if node.is_start:
                    return [x - grid.offsets[0], y - grid.offsets[1]]
    
    def find_checkpoint_node(self, grid):
        checkpoint_counts = {}
        for y, row in enumerate(grid.grid):
            for x, node in enumerate(row):
                for adj in ((1, 1), (-1, 1), (1, -1), (-1, -1)):
                    if grid.get_node(((x - grid.offsets[0]) + adj[0], (y - grid.offsets[1]) + adj[1]), expand=False, phantom=True).tile_type == "checkpoint":
                        try:
                            checkpoint_counts[(x - grid.offsets[0], y - grid.offsets[1])] += 1
                        except KeyError:
                            checkpoint_counts[(x - grid.offsets[0], y - grid.offsets[1])] = 1
        if len(checkpoint_counts.keys()):
            return max(checkpoint_counts, key=checkpoint_counts.get)


    def get_best_node(self, possible_nodes):
        if len(possible_nodes) > 0:
            best_node = possible_nodes[0]
            if best_node[:2] == list(self.current_robot_node):
                best_node = possible_nodes[1]

            orientation = utilities.substractLists(self.current_robot_node, self.previous_robot_node)
            forward_node = utilities.sumLists(self.current_robot_node, orientation)
            for node in possible_nodes[:10]:
                if list(node[:2]) == list(forward_node):
                    best_node = forward_node

        else:
            best_node = self.current_robot_node
        #return possibleNodes[-1][:2]
        return best_node[:2]
    
    def check_path(self, grid):
        for position in self.a_star_path:
            if not is_traversable(grid, position):
                return False
        return True
    
    def predict(self, grid):
        robot_node = self.find_robot_node(grid)
        
        if robot_node != self.current_robot_node:
            self.previous_robot_node = self.current_robot_node
            self.current_robot_node = robot_node
        if self.previous_robot_node is None:
            self.previous_robot_node = self.current_robot_node

        self.prev_checkpoint_node = self.checkpoint_node
        self.checkpoint_node = self.find_checkpoint_node(grid)

        print("CHECKPOINT:", self.checkpoint_node)


        if (len(self.a_star_path) <= self.a_star_index or not self.check_path(grid)) or self.prev_checkpoint_node != self.checkpoint_node: #or not is_bfs_addable(grid, self.best_node):
            direction = utilities.substractLists(self.current_robot_node, self.previous_robot_node)
            if is_traversable(grid, self.current_robot_node):
                possible_nodes = bfs(grid, self.current_robot_node, 100)
            else:
                possible_nodes = bfs(grid, self.previous_robot_node, 100)

            #print("Possible nodes:", possible_nodes)
            if self.checkpoint_node is not None:
                self.best_node = self.checkpoint_node

            elif len(possible_nodes):
                self.best_node = self.get_best_node(possible_nodes)

            best_path = a_star(grid, self.current_robot_node, self.best_node)

            if len(best_path) > 1:
                self.a_star_path = best_path[1:]
                self.a_star_index = 0

        if SHOW_DEBUG:
            for node in self.a_star_path:
                grid.get_node(node).mark1 = True
            grid.print_grid()

        move = utilities.substractLists(self.a_star_path[self.a_star_index], self.current_robot_node)
        move = utilities.multiplyLists(move, [0.5, 0.5])

        if self.current_robot_node == list(self.a_star_path[self.a_star_index]):
            self.a_star_index += 1

        if SHOW_DEBUG:
            print("Best node:", self.best_node)
            print("Start node:", self.current_robot_node)
            print("AStar path: ", self.a_star_path)


        return [int(m) for m in move]
        