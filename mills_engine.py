import numpy as np
import torch
from colorama import Fore as cf, Style as cs

board_state = torch.zeros((3,3,3), dtype=int)
num_neighbors = torch.zeros((3,3,3), dtype=int)

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


def show_position(state : torch.Tensor) -> bool:
    validity = check_position(state)
    if validity:
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

board_state[2, 1, 2] = 1

show_position(board_state)