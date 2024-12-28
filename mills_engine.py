import torch
import re
from typing import List, Any
from colorama import Fore as cf, Style as cs

CORNER_POSITION_MULTI = 1.0
THREE_NEIGH_POSITIONS_MULTI = 1.2
FOUR_NEIGH_POSITIONS_MULTI  = 1.3
OPEN_MILL_WEIGHT            = 0.2
LEGAL_MOVES_WEIGHT          = 0.3

#TODO: Implement list of all past board states and the ability to go back to the previous board state
#TODO: Add Openingbook where the program always sets in the four crossings first
#TODO: Optimize away all the triple for loops






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

def initialize_boardvalues(big_cross : float = FOUR_NEIGH_POSITIONS_MULTI, 
                            little_cross : float = THREE_NEIGH_POSITIONS_MULTI, 
                            corner : float = CORNER_POSITION_MULTI) -> torch.tensor:
    board_value = torch.tensor([
        [[corner, little_cross, corner], 
         [little_cross, 0.0, little_cross], 
         [corner, little_cross, corner]],
        [[corner, big_cross, corner], 
         [big_cross, 0.0, big_cross], 
         [corner, big_cross, corner]],
        [[corner, little_cross, corner], 
         [little_cross, 0.0, little_cross], 
         [corner, little_cross, corner]]
    ])
    return board_value

board_value = initialize_boardvalues(big_cross=FOUR_NEIGH_POSITIONS_MULTI, little_cross=THREE_NEIGH_POSITIONS_MULTI)

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
    pieces = torch.nonzero(state == 0).tolist()
    for index in pieces:
        if not (index[1] == 1 and index[2] == 1):
            moves.append(tuple(index))
    return moves

def legal_moves_mid(state : torch.tensor, colour : int, free_spaces : Any = None) -> List:
    moves = []

    if free_spaces is None:
        free_spaces = get_neighbor_free(state)

    pieces = torch.nonzero(state == colour).tolist()
    for index in pieces:
        i, j, k = index
        if not (j == 1 and k == 1):
            for free in free_spaces[i][j][k]:
                moves.append([(i, j, k), free])
    return moves

def legal_moves_end(state : torch.tensor, colour : int, free_spaces : Any = None) -> List:
    moves = []
    pieces = torch.nonzero(state == colour).tolist()
    empty = legal_moves_early(state)
    for index in pieces:
        if not (index[1] == 1 and index[2] == 1):
            for emp in empty:
                moves.append([tuple(index), tuple(emp)])
    return moves


def removeable_pieces(state : torch.tensor, colour : int) -> List:
    pieces = torch.nonzero(state == -colour).tolist()
    i = 0
    while i < len(pieces):
        if check_mill(state, tuple(pieces[i])):
            pieces.pop(i)
        else:
            i += 1
    if len(pieces) > 0:
        return pieces
    else:
        return torch.nonzero(state == -colour).tolist()

def new_board_state_early(state : torch.tensor, move : tuple[int], colour : int) -> List:
    new_states = []
    original_state = torch.clone(state)
    original_state[move] = colour
    if check_mill(original_state, move):
        for index in removeable_pieces(original_state, colour):
            dummy_state = torch.clone(original_state)
            dummy_state[tuple(index)] = 0
            new_states.append(dummy_state)
    else:
        new_states.append(original_state)
    return new_states

def new_board_state_mid(state : torch.tensor, move : List[tuple[int]], colour : int) -> List:
    new_states = []
    original_state = torch.clone(state)
    move_from = move[0]
    move_to = move[1]
    original_state[move_from] = 0
    original_state[move_to] = colour
    if check_mill(original_state, move_to):
        for index in removeable_pieces(original_state, colour):
            dummy_state = torch.clone(original_state)
            dummy_state[tuple(index)] = 0
            new_states.append(dummy_state)
    else:
        new_states.append(original_state)
    return new_states
        

def evaluate_position(state : torch.tensor, 
                        board_value : torch.tensor = board_value, 
                        is_early_game : bool = False, 
                        open_mill_weight : float = OPEN_MILL_WEIGHT, 
                        legal_move_weight : float = LEGAL_MOVES_WEIGHT) -> float:

    free_spaces = get_neighbor_free(state)
    terminal = is_terminal_node(state, is_early_game, free_spaces)
    if abs(terminal) == 1:
        return terminal * 9001

    legal_moves_white = len(legal_moves_mid(state, 1, free_spaces))
    legal_moves_black = len(legal_moves_mid(state, -1, free_spaces))

    open_mill_white = len(check_possible_mills(state, 1))
    open_mill_black = len(check_possible_mills(state, -1))


    piece_value = state * board_value
    return float(piece_value.sum()) + legal_move_weight * (legal_moves_white - legal_moves_black) + open_mill_weight * (open_mill_white - open_mill_black)

def get_children_early(state : torch.tensor, colour : int):
    children = []
    moves = legal_moves_early(state)
    for i, move in enumerate(moves):
        children += new_board_state_early(state, move, colour)
    return children

def is_terminal_node(state : torch.tensor, 
                        is_early_game : bool = False,
                        free_spaces : Any  = None) -> int:

    num_white_stones = torch.sum(state == 1)
    num_black_stones = abs(torch.sum(state == -1))
    if free_spaces is None:
        free_spaces = get_neighbor_free(state)
    legal_moves_white = len(legal_moves_mid(state, 1, free_spaces))
    legal_moves_black = len(legal_moves_mid(state, -1, free_spaces))

    # Check for win
    if not is_early_game:
        if num_white_stones < 3:
            return -1 # Black has won
        if num_black_stones < 3:
            return 1 # White has won

    if num_white_stones > 3:
        if legal_moves_white == 0:
            return -1 # Black has won
    if num_black_stones > 3:
        if legal_moves_black == 0:
            return 1 # White has won
    
    return 0 # Still undecided

def minimax_early(node, depth, alpha, beta, maximizingPlayer):
    if depth == 0 or abs(is_terminal_node(node, is_early_game = True))==1:
        return evaluate_position(node, is_early_game = True), node

    best_node = None

    if maximizingPlayer:
        maxEval = float('-inf')
        for child in get_children_early(node, 1):
            eval, _ = minimax_early(child, depth - 1, alpha, beta, False)
            if eval > maxEval:
                maxEval = eval
                best_node = child
            alpha = max(alpha, eval)
            if beta <= alpha:
                break  # Beta cut-off
        return maxEval, best_node
    else:
        minEval = float('inf')
        for child in get_children_early(node, -1):
            eval, _ = minimax_early(child, depth - 1, alpha, beta, True)
            if eval < minEval:
                minEval = eval
                best_node = child
            beta = min(beta, eval)
            if beta <= alpha:
                break  # Alpha cut-off
        return minEval, best_node


board_state = torch.zeros((3,3,3), dtype=int)


board_state[2, 1, 2] = 1
board_state[1, 1, 2] = 1
board_state[1, 2, 1] = 1
board_state[2, 2, 0] = 1
board_state[2, 2, 2] = 1
board_state[0, 1, 2] = 1
board_state[2, 0, 2] = 1

board_state[1, 0, 0] = -1
board_state[1, 0, 1] = -1
board_state[1, 0, 2] = -1
board_state[1, 2, 0] = -1
board_state[0, 0, 1] = -1
board_state[1, 2, 2] = -1

show_position(board_state)

#print(get_children_early(board_state, 1))

# Starting point
root_node = board_state  # Define the root node of the game tree
depth = 3  # Define the depth to search
alpha = float('-inf')
beta = float('inf')
maximizingPlayer = True  # Define if the starting player is maximizing

best_value, best_node = minimax_early(root_node, depth, alpha, beta, True)
print("Best value:", best_value)
print("Best node:")
show_position(best_node)

exit()

for i in range(len(get_children_early(board_state, 1))):
    print(i)
    show_position(get_children_early(board_state, 1)[i])

exit()

print(legal_moves_mid(board_state, 1))

exit()

board_state = new_board_state_mid(board_state, [tuple([1, 2, 1]), tuple([2, 2, 1])], 1)

show_position(board_state[0])

exit()

print(removeable_pieces(board_state, -1))

exit()

print(legal_moves_mid(board_state, -1))

print(evaluate_position(board_state))

exit()

input_next_move(board_state, colour=1, is_late_game=True)

show_position(board_state)



###################
###################
##### OLD CODE ####


ACTUAL_FREE_NEIGH_MULTI     = 0.1

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