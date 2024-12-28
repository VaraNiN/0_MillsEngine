import torch
import re
from typing import List
from colorama import Fore as cf, Style as cs

board_state = torch.zeros((3,3,3), dtype=int)
num_neighbors = torch.zeros((3,3,3), dtype=int)

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


def show_position(state : torch.Tensor, check_validity : bool = True) -> None:
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
        neighbour_indices[i][0][0].append((i, 1, 0)) # Top left corners
        neighbour_indices[i][0][0].append((i, 0, 1)) # Top left corners

        neighbour_indices[i][2][0].append((i, 1, 0)) # Top right corners
        neighbour_indices[i][2][0].append((i, 2, 1)) # Top right corners

        neighbour_indices[i][0][2].append((i, 1, 2)) # Bottom left corners
        neighbour_indices[i][0][2].append((i, 0, 1)) # Bottom left corners

        neighbour_indices[i][2][2].append((i, 1, 2)) # Bottom right corners
        neighbour_indices[i][2][2].append((i, 2, 1)) # Bottom right corners

    return neighbour_indices

def update_neighbors(state : torch.Tensor) -> torch.Tensor:
    return



board_state[2, 1, 2] = 1

nei = initialize_neighbour_map()
print(nei[0][0][0])
print(nei)
exit()

show_position(board_state)

exit()

input_next_move(board_state, 1)

show_position(board_state)