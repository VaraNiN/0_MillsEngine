import torch
import re
from typing import List
from colorama import Fore as cf, Style as cs

board_state = torch.zeros((3,3,3), dtype=int)

neighbors_mult = torch.zeros((3,3,3), dtype=float)

THREE_NEIGH_POSITIONS_MULTI = 1.2
FOUR_NEIGH_POSITIONS_MULTI  = 1.3
ACTUAL_FREE_NEIGH_MULTI     = 0.1








def red(string : str) -> None:
    print(cf.RED + string + cs.RESET_ALL)

def check_position(state: torch.tensor) -> bool:
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


def show_position(state : torch.tensor, check_validity : bool = True, replace_symbols : bool = True) -> None:
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

def input_next_move(state: torch.tensor, colour: int) -> None:
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

def initialize_boardvalues(big_cross : int = FOUR_NEIGH_POSITIONS_MULTI, little_cross : int = THREE_NEIGH_POSITIONS_MULTI) -> torch.tensor:
    board_value = torch.tensor([
        [[1.0, little_cross, 1.0], 
        [little_cross, 0.0, little_cross], 
        [1.0, little_cross, 1.0]],
        [[1.0, big_cross, 1.0], 
        [big_cross, 0.0, big_cross], 
        [1.0, big_cross, 1.0]],
        [[1.0, little_cross, 1.0], 
        [little_cross, 0.0, little_cross], 
        [1.0, little_cross, 1.0]]
    ])
    return board_value

board_value = initialize_boardvalues(big_cross=FOUR_NEIGH_POSITIONS_MULTI, little_cross=THREE_NEIGH_POSITIONS_MULTI)


def get_neighbors(state : torch.tensor, neigh_map : List = neighbors_map, free_weight : float = ACTUAL_FREE_NEIGH_MULTI) -> torch.tensor:
    """ Returns number of free neighbouring cells """
    neigh_count = torch.ones(state.size(), dtype=float)
    for i in range(3):
        for j in range(3):
            for k in range(3):
                neigh_count[i, j ,k] += free_weight * len(neigh_map[i][j][k])
                for neigh in neigh_map[i][j][k]:
                    if state[neigh] != 0:
                        neigh_count[i, j ,k] -= free_weight

    return neigh_count

def evaluate_position(state : torch.tensor, board_value : torch.tensor = board_value, neigh_map : List = neighbors_map) -> float:
    free_neighbours = get_neighbors(board_state)    
    
    piece_value = state * board_value * free_neighbours
    show_position(piece_value, check_validity=False, replace_symbols=False)
    return float(piece_value.sum())

def check_mill(state : torch.tensor, move : tuple[int]) -> bool:
    colour = state[move]
    if colour != 1 and colour != -1:
        red("Something went wrong while checking if a mill occured. state[move] = 0")
        exit()
    ring, x, y = move

    if state[ring - 1, x, y] == colour and state[ring - 2, x, y] == colour:
        return True
    elif state[ring, x - 1, y] == colour and state[ring, x - 2, y] == colour:
        return True
    elif state[ring, x, y - 1] == colour and state[ring, x, y - 2] == colour:
        return True
    else:
        return False



board_state[2, 1, 2] = 1
board_state[1, 1, 2] = 1

board_state[1, 0, 2] = -1
board_state[2, 2, 2] = 1
board_state[1, 2, 2] = -1
board_state[0, 1, 2] = 1
board_state[2, 0, 2] = 1
board_state[1, 0, 1] = -1
board_state[1, 0, 0] = -1

show_position(board_state)
print(check_mill(board_state, (1, 2, 2)))