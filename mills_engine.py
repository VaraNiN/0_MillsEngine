import torch
import re
from typing import List
from colorama import Fore as cf, Style as cs

board_state = torch.zeros((3,3,3), dtype=int)

neighbors_mult = torch.zeros((3,3,3), dtype=float)

THREE_NEIGH_POSITIONS_MULTI = 1.2
FOUR_NEIGH_POSITIONS_MULTI  = 1.3
ACTUAL_FREE_NEIGH_MULTI     = 0.1

#TODO: Implement list of all past board states and the ability to go back to the previous board state
#TODO: Add Openingbook where the program always sets in the four crossings first






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
    
    if abs(torch.sum(state == -1)) > 9:
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

def input_next_add(state: torch.tensor, colour: int) -> None:
    while True:
        move = input("Where should a stone be added? (Format: ring x y): ")
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

def input_next_remove(state: torch.tensor, colour: int) -> None:
    while True:
        move = input("Where should a stone be removed? (Format: ring x y): ")
        if re.match(r'^\d \d \d$', move):
            coords = tuple(map(int, move.split()))
            if all(n in {0, 1, 2} for n in coords):
                if not (coords[1] == 1 and coords[2] == 1):
                    if state[coords] == -colour:
                        break
                    elif state[coords] == colour:
                        print("Invalid values. Cannot remove your own stones.")
                    else:
                        print("Invalid values. No stone there.")
                else:
                    print("Invalid values. x and y cannot both be 1")
            else:
                print("Invalid values. All have to be 0, 1 or 2")
        else:
            print("Invalid format.")

    state[coords] = 0

def input_next_move(state: torch.tensor, colour: int, is_late_game : bool = False) -> None:
    while True:
        move = input("Please provide the next move in the format (ring_from x_from y_from ring_to x_to y_to): ")
        if re.match(r'^\d \d \d \d \d \d$', move):
            ring_from, x_from, y_from, ring_to, x_to, y_to = map(int, move.split())
            all_coords = tuple(map(int, move.split()))
            coords_from = tuple((ring_from, x_from, y_from))
            coords_to = tuple((ring_to, x_to, y_to ))
            if all(n in {0, 1, 2} for n in all_coords):
                if not (coords_from[1] == 1 and coords_from[2] == 1):
                    if not (coords_to[1] == 1 and coords_to[2] == 1):
                        if state[coords_from] == colour:
                            if state[coords_to] == 0:
                                if is_late_game:
                                    break
                                else:
                                    if coords_to in get_neighbor_free(state)[ring_from][x_from][y_from]:
                                        break
                                    else:
                                        print("Invalid values. Cannot reach target from origin!")
                            else:
                                print("Invalid values. Target is not empty!")
                        else:
                            print("Invalid values. None of your stones is at origin!")
                    else:
                        print("Invalid values. x and y cannot both be 1")
                else:
                    print("Invalid values. x and y cannot both be 1")
            else:
                print("Invalid values. All have to be 0, 1 or 2")
        else:
            print("Invalid format.")

    state[coords_from] = 0
    state[coords_to] = colour

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


def get_neighbor_weights(state : torch.tensor, neigh_map : List = neighbors_map, free_weight : float = ACTUAL_FREE_NEIGH_MULTI) -> torch.tensor:
    """ Returns weighting based on free neighboring cells"""
    neigh_count = torch.ones(state.size(), dtype=float)
    for i in range(3):
        for j in range(3):
            for k in range(3):
                neigh_count[i, j ,k] += free_weight * len(neigh_map[i][j][k])
                for neigh in neigh_map[i][j][k]:
                    if state[neigh] != 0:
                        neigh_count[i, j ,k] -= free_weight

    return neigh_count

def get_neighbor_free(state : torch.tensor, neigh_map : List = neighbors_map) -> List:
    """ Returns list of free neighboring cells for each cell"""
    free_neighs = [[[[] for _ in range(3)] for _ in range(3)] for _ in range(3)]
    for i in range(3):
        for j in range(3):
            for k in range(3):
                for neigh in neigh_map[i][j][k]:
                    if state[neigh] == 0:
                        free_neighs[i][j][k].append(neigh)

    return free_neighs

def evaluate_position(state : torch.tensor, board_value : torch.tensor = board_value, neigh_map : List = neighbors_map, is_early_game : bool = False) -> float:
    if not is_early_game:
        if torch.sum(state == 1) < 3:
            return -9001 # Black has won
        
        if abs(torch.sum(state == -1)) < 3:
            return 9001 # White has won
    
    free_neighbours = get_neighbor_weights(board_state)    
    piece_value = state * board_value * free_neighbours
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
    

def check_possible_mills(state : torch.tensor, colour : int) -> List:
    #TODO optimize this
    possible_mills = []
    for i in range(3):
        for j in range(3):
            for k in range(3):
                if state[i, j, k] == colour:
                    if state[i - 1, j, k] == colour and state[i - 2, j, k] == 0:
                        possible_mills.append(((i - 2) % 3, j, k))
                    if state[i - 1, j, k] == 0 and state[i - 2, j, k] == colour:
                        possible_mills.append(((i - 1) % 3, j, k))

                    if state[i, j - 1, k] == colour and state[i, j - 2, k] == 0:
                        possible_mills.append((i, (j - 2) % 3, k))
                    if state[i, j - 1, k] == 0 and state[i, j - 2, k] == colour:
                        possible_mills.append((i, (j - 1) % 3, k))

                    if state[i, j, k - 1] == colour and state[i, j, k - 2] == 0:
                        possible_mills.append((i, j, (k - 2) % 3))
                    if state[i, j, k - 1] == 0 and state[i, j, k - 2] == colour:
                        possible_mills.append((i, j, (k - 1) % 3))
    return list(dict.fromkeys(possible_mills))



def legal_moves_early(state : torch.tensor) -> List:
    moves = []
    for i in range(3):
        for j in range(3):
            for k in range(3):
                if not (j == 1 and k == 1):
                    if state[i, j, k] == 0:
                        moves.append((i, j, k))
    return moves





board_state[2, 1, 2] = 1
board_state[1, 1, 2] = 1
board_state[2, 2, 0] = 1
board_state[1, 2, 0] = -1
board_state[0, 0, 1] = -1
board_state[1, 0, 2] = -1
board_state[2, 2, 2] = 1
board_state[1, 2, 2] = -1
board_state[0, 1, 2] = 1
board_state[2, 0, 2] = 1
board_state[1, 0, 1] = -1
board_state[1, 0, 0] = -1

show_position(board_state)

print(check_possible_mills(board_state, colour=-1))

exit()

input_next_move(board_state, colour=1, is_late_game=True)

show_position(board_state)