import numpy as np
import cv2 as cv
import copy
import utilities

"""
Requirements:

1 = Node type (tile, vortex, wall)
2 = Status (ocupied, not_occupied, undefined)
3 = Tile type (only if tile: undefined, start, normal, connection1-2, connection1-3, connection2-3, swamp, hole)

undefined = no conozco el tipo de casilla
"""
class Fixture:
    def __init__(self, exists=False, reported=False, type="N") -> None:
        self.exists = exists
        self.reported = reported
        self.type = type
        self.detection_angle = None

class Node:
    def __init__(self, node_type:str, status:str="undefined", tile_type:str="undefined", curved:int=0, explored:bool=False, is_robots_position:bool=False):
        self.node_type = node_type
        self.status = status
        self.tile_type = tile_type if node_type == "tile" else "undefined"
        self.explored = explored
        self.is_robots_position = is_robots_position
        self.fixture = Fixture()
        self.fixtures_in_wall = []
        self.is_start = False
        self.is_curved = False

        self.mark1 = 0
        self.mark2 = 0
        
        self.valid_node_type = ("tile", 
                                "vortex",
                                "wall") #tuple with valid values for the variables of the node
        
        self.valid_status = (   "occupied",
                                "undefined",
                                "not_occupied") #same tuple

        self.valid_tile_types = ("undefined",
                                "normal",
                                "start",
                                "connection1-2",
                                "connection1-3", 
                                "connection2-3", 
                                "swamp", 
                                "hole",
                                "checkpoint") #same tuple

        self.tile_type_to_string = {
            "undefined": "0",
            "normal": "0",
            "checkpoint": "4",
            "start": "5",
            "connection1-2": "6",
            "connection1-3": "7",
            "connection2-3": "8",
            "swamp": "3",
            "hole": "2"
        }
       


    def get_representation(self) -> str:
        if self.node_type == "tile":
            return self.tile_type_to_string[self.tile_type]

        elif self.node_type == "vortex":
            return str(int(self.status == "occupied" and not self.is_curved))
        
        elif self.node_type == "wall":
            if len(self.fixtures_in_wall) > 0:
                return str("".join(self.fixtures_in_wall))
            return str(int(self.status == "occupied"))
        
        else:
            return "0"

    # Returns a visual representation of the node in ASCII 
    def get_string(self):

        if self.mark1:
            return "\033[1;36;36m██" + "\033[0m"

        if self.status == "undefined":
            if not(self.node_type == "tile" and self.tile_type != "undefined"):    
                return "??"
        

        if self.status == "occupied":
            if self.node_type == "vortex" and self.explored:
                return "\033[1;31;47m██"+ "\033[0m"

            if self.node_type == "wall" and len(self.fixtures_in_wall) > 0:
                return f"\033[1;35;40m{self.fixtures_in_wall[0]*2}" + "\033[0m"
            
            return "\033[1;30;40m██" + "\033[0m"
        
        
        #elif self.is_robots_position:
        #    return "\033[1;32;47m██"+ "\033[0m"
        
        elif self.node_type == "wall":
            """
            if self.status == "not_occupied":
                return "\033[1;37;47m██"+ "\033[0m"
            """
            return "\033[1;30;47m||"+ "\033[0m"
        elif self.node_type == "vortex": #vertice
            """
            if self.status == "not_occupied":
                return "\033[1;37;47m██"+ "\033[0m"
            """
            if self.explored:
                return "\033[1;32;47m██"+ "\033[0m"

            return "\033[1;30;47m<>"+ "\033[0m"
        
        elif self.node_type == "tile":

            if self.explored:
                if self.tile_type == "start":
                    return "\033[1;32;47m█E"+ "\033[0m"
                if self.tile_type == "hole":
                    return "\033[0m  "+ "\033[0m"
                if self.tile_type == "swamp":
                    return "\033[1;33;40m█E"+ "\033[0m"
                if self.tile_type == "checkpoint":
                    return "\033[0m█E"+ "\033[0m"
                if self.tile_type == "connection1-3":
                    return "\033[1;35;47m█E"+ "\033[0m"
                if self.tile_type == "connection1-2":
                    return "\033[1;34;47m█E"+ "\033[0m"
                if self.tile_type == "connection2-3" or self.tile_type == "red_swamp":
                    return "\033[1;31;47m█E"+ "\033[0m"
                if self.tile_type == "normal":
                    return "\033[1;37;47m█E"+ "\033[0m"
            
            if self.tile_type == "start":
                return "\033[1;32;47m██"+ "\033[0m"
            if self.tile_type == "hole":
                return "\033[0m  "+ "\033[0m"
            if self.tile_type == "swamp":
                return "\033[1;33;40m██"+ "\033[0m"
            if self.tile_type == "checkpoint":
                return "\033[0m██"+ "\033[0m"
            if self.tile_type == "connection1-3":
                return "\033[1;35;47m██"+ "\033[0m"
            if self.tile_type == "connection1-2":
                return "\033[1;34;47m██"+ "\033[0m"
            if self.tile_type == "connection2-3" or self.tile_type == "red_swamp":
                return "\033[1;31;47m██"+ "\033[0m"
            if self.tile_type == "normal":
                return "\033[1;37;47m██"+ "\033[0m"

            return "\033[1;30;47m??"+ "\033[0m"
            
        
        
    def __str__(self) -> str:
        return self.get_string()

    def __repr__(self) -> str:
        return self.get_string()

class Grid:
    def __init__(self, initial_shape):
        self.offsets = [initial_shape[0] // 2, initial_shape[1] // 2]
        self.shape = initial_shape
        self.grid = np.empty(initial_shape, dtype=object)
        self.fill_nodes(self.grid)
        self.fill_node_types()
    
    def get_node_type(self, point):
        x_div = point[0] % 2 == 0
        y_div = point[1] % 2 == 0
        if x_div and y_div:
            return "vortex"
        elif x_div and not y_div:
            return "wall"
        elif not x_div and y_div:
            return "wall"
        elif not x_div and not y_div:
            return "tile"
    
    def get_type_node_poses(self, node_type):
        grid = []
        for y, row in enumerate(self.grid):
            new_row = []
            for x, node in enumerate(row):
                if node.node_type == node_type:
                    new_row.append((x, y))
            grid.append(row)
        return grid
    
    def fill_nodes(self, grid):
        for i in range(grid.shape[0]):
            for j in range(grid.shape[1]):
                grid[i, j] = Node("undefined")

    def fill_node_types(self, x_min=0, y_min=0, x_max=None, y_max=None):
        if x_max is None:
            x_max = self.shape[1]
        if y_max is None:
            y_max = self.shape[0]
        
        for y in range(y_min, y_max):
            for x in range(x_min, x_max):
                self.grid[y, x].node_type = self.get_node_type((x + self.offsets[0], y + self.offsets[1]))
                self.grid[y, x].status = "not_occupied"

    def add_end_row(self, size):
        self.shape = (self.shape[0]+ size, self.shape[1] )
        row = np.empty((size, self.shape[1]), dtype=object)
        self.fill_nodes(row)
        self.grid = np.vstack((self.grid, row))
        self.fill_node_types(y_min=self.shape[0]-size)
    
    def add_begining_row(self, size):
        self.offsets[1] += size
        self.shape = (self.shape[0]+ size, self.shape[1] )
        row = np.empty((size, self.shape[1]), dtype=object)
        self.fill_nodes(row)
        self.grid = np.vstack((row, self.grid))
        self.fill_node_types(y_max=size)
    
    def add_end_column(self, size):
        self.shape = (self.shape[0], self.shape[1] + size)
        column = np.empty((self.shape[0], size), dtype=object)
        self.fill_nodes(column)
        self.grid = np.hstack((self.grid, column))
        self.fill_node_types(x_min=self.shape[1]-size)

    def add_begining_column(self, size):
        self.offsets[0] += size
        self.shape = (self.shape[0], self.shape[1] + size)
        column = np.empty((self.shape[0], size), dtype=object)
        self.fill_nodes(column)
        self.grid = np.hstack((column, self.grid))
        self.fill_node_types(x_max=size)

    def expand_grid_to_point(self, point):
        x, y = point
        x, y = x + self.offsets[0], y + self.offsets[1]

        if y + 1 > self.shape[0]:
            self.add_end_row(y - self.shape[0] +1)
        if x + 1 > self.shape[1]:
            self.add_end_column(x - self.shape[1] +1)
        if y < 0:
            self.add_begining_row(-y)
        if x < 0:
            self.add_begining_column(-x)
    
    def get_node(self, point, expand=True, phantom=False):
        if expand:
            self.expand_grid_to_point(point)
        elif not self.is_in_grid(point):
            if phantom:
                return Node(self.get_node_type(point))
            return None
        x, y = point
        x, y = x + self.offsets[0], y + self.offsets[1]
        return self.grid[y, x]
    
    def is_in_grid(self, point):
        x, y = point
        x, y = x + self.offsets[0], y + self.offsets[1]
        return 0 <= x < self.grid.shape[1] and 0 <= y < self.grid.shape[0]

    def fill_verticies_around_wall(self, wall_node):
        assert self.get_node(wall_node).node_type == "wall"
        for a in ([-1, 0], [1, 0], [0, -1], [0, 1]):
            x, y = wall_node
            x += a[1]
            y += a[0]
            node = self.get_node((x, y))
            if node.node_type == "vortex":
                node.status = "occupied"

    def load_straight_wall(self, tile, direction):
        assert self.get_node(tile).node_type == "tile"
        list_direction = utilities.dir2list(direction)
        wall = [t + d for t, d in zip(tile, list_direction)]

        self.get_node((wall[0], wall[1])).status = "occupied"
        self.fill_verticies_around_wall((wall[0], wall[1]))


    def print_grid(self):
        for row in self.grid:
            for node in row:
                print(node, end="")
            print()
        print()
    
if __name__ == "__main__":
    grid = Grid((10, 10))
    
    grid.get_node((0, 0)).status = "occupied"
    grid.get_node((-5, -5)).status = "occupied"
    grid.get_node((-5, 4)).status = "occupied"
    grid.get_node((4, -5)).status = "occupied"
    grid.get_node((4, 4)).status = "occupied"
    grid.print_grid()

    """
    grid.add_end_row(2)
    grid.print_grid()
    grid.add_begining_row(2)
    grid.print_grid()
    grid.add_end_column(2)
    grid.print_grid()
    grid.add_begining_column(2)
    grid.print_grid()
    """

     
    
