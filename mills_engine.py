import torch
import re
from typing import List
from colorama import Fore as cf, Style as cs

board_state = torch.zeros((3,3,3), dtype=int)

neighbors_mult = torch.zeros((3,3,3), dtype=float)

board_value = torch.Tensor([
    [[1.0, 1.2, 1.0], 
     [1.2, 0.0, 1.2], 
     [1.0, 1.2, 1.0]],
    [[1.0, 1.5, 1.0], 
     [1.5, 0.0, 1.5], 
     [1.0, 1.5, 1.0]],
    [[1.0, 1.2, 1.0], 
     [1.2, 0.0, 1.2], 
     [1.0, 1.2, 1.0]]
])

def red(string : str) -> None:
    print(cf.RED + string + cs.RESET_ALL)

def check_position(state: torch.Tensor) -> bool:
    if state.size() != (3, 3, 3):
        red("Warning: Invalid Board State - Incorrect size")
        print(state)
        return False
    
    if not torch.isin(state, torch.tensor([1, 0, -1])).all():
        red("Warning: Invalid Board State - Contains invalid values")
        print(state)
        return False
    
    if not torch.isin(state[:, 1, 1], torch.tensor([0])).all():
        red("Warning: Invalid Board State - Center positions must be 0")
        print(state)
        return False
    
    if torch.sum(state == 1) > 9:
        red("Warning: Invalid Board State - Too many white stones")
        print(state)
        return False
    
    if torch.sum(state == -1) > 9:
        red("Warning: Invalid Board State - Too many black stones")
        print(state)
        return False
    
    return True


def show_position(state : torch.Tensor, check_validity : bool = True, replace_symbols : bool = True) -> None:
    if check_validity:
        if not check_position(state):
            return
        
    board_template = """
        {0}-----------{3}-----------{6}
        |           |           |
        |   {9}-------{12}-------{15}   |
        |   |       |       |   |
        |   |   {18}---{21}---{24}   |   |
        |   |   |       |   |   |
        {1}---{10}---{19}       {25}---{16}---{7}
        |   |   |       |   |   |
        |   |   {20}---{23}---{26}   |   |
        |   |       |       |   |
        |   {11}-------{14}-------{17}   |
        |           |           |
        {2}-----------{5}-----------{8}
        """
    
    input = state.flatten().tolist()
    if replace_symbols:
        input = ["X" if x ==  1 else x for x in input]
        input = ["O" if x == -1 else x for x in input]
        input = [" "  if x ==  0 else x for x in input]
    
    print(board_template.format(*input))

def input_next_move(state: torch.Tensor, colour: int) -> None:
    while True:
        move = input("Please provide the next move in the format: ring x y: ")
        if re.match(r'^\d \d \d$', move):
            coords = tuple(map(int, move.split()))
            if all(n in {0, 1, 2} for n in coords):
                if not (coords[1] == 1 and coords[2] == 1):
                    if state[coords] == 0:
                        break
                    else:
                        print("Invalid values. There is already a stone there.")
                else:
                    print("Invalid values. x and y cannot both be 1")
            else:
                print("Invalid values. All have to be 0, 1 or 2")
        else:
            print("Invalid format.")

    state[coords] = colour

def initialize_neighbour_map() -> List:
    neighbour_indices = [[[[] for _ in range(3)] for _ in range(3)] for _ in range(3)]

    for i in range(3): # Corners
        for j in [0, 2]:
            for k in [0, 2]:
                if j == 0:
                    neighbour_indices[i][j][k].append((i, j+1, k))
                else:
                    neighbour_indices[i][j][k].append((i, j-1, k))

                if k == 0:
                    neighbour_indices[i][j][k].append((i, j, k+1))
                else:
                    neighbour_indices[i][j][k].append((i, j, k-1))

    for i in range(3): # Crossings
        for j, k in [[0, 1], [1, 0], [2, 1], [1, 2]]:
            if j == 1:
                neighbour_indices[i][j][k].append((i, j+1, k))
                neighbour_indices[i][j][k].append((i, j-1, k))

            if k == 1:
                neighbour_indices[i][j][k].append((i, j, k+1))
                neighbour_indices[i][j][k].append((i, j, k-1))

            if i == 0:
                neighbour_indices[i][j][k].append((i+1, j, k))
            if i == 1:
                neighbour_indices[i][j][k].append((i+1, j, k))
                neighbour_indices[i][j][k].append((i-1, j, k))
            if i == 2:
                neighbour_indices[i][j][k].append((i-1, j, k))
            

    return neighbour_indices

neighbors_map = initialize_neighbour_map()

def get_neighbors(state : torch.Tensor, neigh_map : List = neighbors_map) -> torch.Tensor:
    """ Returns number of free neighbouring cells """
    if check_position(state):
        neigh_count = torch.zeros(state.size(), dtype=int)
        for i in range(3):
            for j in range(3):
                for k in range(3):
                    neigh_count[i, j ,k] = len(neigh_map[i][j][k])
                    for neigh in neigh_map[i][j][k]:
                        if state[neigh] != 0:
                            neigh_count[i, j ,k] -= 1

        return neigh_count
    else:
        exit()



board_state[2, 1, 2] = 1
board_state[1, 2, 2] = -1

show_position(board_state)
free_neighbours = get_neighbors(board_state)
show_position(free_neighbours, check_validity=False, replace_symbols=False)