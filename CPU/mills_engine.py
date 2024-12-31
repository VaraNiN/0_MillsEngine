import numpy as np
import re
import time
from typing import List, Any
from colorama import Fore as cf, Style as cs
import gui
import threading

ENABLE_TIMING = False
total_elapsed = 0.

CORNER_POSITION_MULTI = 1.0
THREE_NEIGH_POSITIONS_MULTI = 1.1
FOUR_NEIGH_POSITIONS_MULTI  = 1.15
LEGAL_MOVES_WEIGHT          = 0.1
OPEN_MILL_WEIGHT            = 0.2

# TODO: Rewrite everything for numpy and add multi-threading
# TODO: Use AI to train weights
# TODO: Get better timing class - timings are way off!
# TODO: Add maximum think time per move of computer



### This timer class is based on that of Gertjan van den Burg
### See their article at https://gertjanvandenburg.com/blog/timing_decorator/
class Timer(object):
    def __init__(self):
        self.timers = {}
        self.call_counts = {}
        self._stack = []
        self.start = None
        self.player_moves = ["input_next_add", "input_next_remove", "input_next_move"]

    def add_to_timer(self, name, duration):
        if name not in self.timers:
            self.timers[name] = 0
            self.call_counts[name] = 0
        self.timers[name] += duration
        self.call_counts[name] += 1

    def stack(self, name):
        # stop running timer, start new timer, add name to stack
        if len(self._stack):
            self.add_to_timer(self._stack[0], time.time() - self.start)
        self.start = time.time()
        self._stack.insert(0, name)

    def pop(self):
        # pop name from stack, restart previous timer
        self.add_to_timer(self._stack.pop(0), time.time() - self.start)
        self.start = time.time()

    def report(self):
        if not self.timers:
            print("No timers to report.")
            return
        
        print("Timing Report:")
        
        # Calculate the maximum length of function names
        max_name_length = max(len(name) for name in self.timers.keys())
        
        # Print the header with dynamic width for function names
        print(f"{'Function':<{max_name_length}} {'Time (s)':<10} {'Calls':<10} {'Avg Time (µs)':<15}")
        print("-" * (max_name_length + 45))
        
        total_player_time = 0.
        total_computer_time = 0.
        # Print each function's timing report with dynamic width for function names
        for name, duration in self.timers.items():
            avg_time_us = (duration / self.call_counts[name]) * 1e6
            print(f"{name:<{max_name_length}} {duration:<10.4f} {self.call_counts[name]:<10} {avg_time_us:<15.2f}")
            if name in self.player_moves:
                total_player_time += duration
            else:
                total_computer_time += duration
        
        print("-" * (max_name_length + 45))

        # Print total player and computer times
        print(f"{'Player Time':<{max_name_length}} {total_player_time:<10.4f}")
        print(f"{'Computer Time (indiv.)':<{max_name_length}} {total_computer_time:<10.4f}")
        print(f"{'Computer Time (comb.)':<{max_name_length}} {total_elapsed:<10.4f}")

TIMER = Timer()

def timer_wrap(func):
    def wrapper(*args, **kwargs):
        if ENABLE_TIMING:
            name = func.__name__
            TIMER.stack(name)
            ans = func(*args, **kwargs)
            TIMER.pop()
            return ans
        else:
            return func(*args, **kwargs)
    return wrapper

def print_report():
    TIMER.report()


def red(string : str) -> None:
    print(cf.RED + string + cs.RESET_ALL)

@timer_wrap
def check_position(state: np.array) -> bool:
    if state.shape != (3, 3, 3):
        red("Warning: Invalid Board State - Incorrect size")
        print(state)
        return False
    
    if not np.isin(state, np.array([1, 0, -1])).all():
        red("Warning: Invalid Board State - Contains invalid values")
        print(state)
        return False
    
    if not np.isin(state[:, 1, 1], np.array([0])).all():
        red("Warning: Invalid Board State - Center positions must be 0")
        print(state)
        return False
    
    if np.sum(state == 1) > 9:
        red("Warning: Invalid Board State - Too many white stones")
        print(state)
        return False
    
    if abs(np.sum(state == -1)) > 9:
        red("Warning: Invalid Board State - Too many black stones")
        print(state)
        return False
    
    return True

@timer_wrap
def show_position(state : np.array, check_validity : bool = True, replace_symbols : bool = True) -> None:
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

@timer_wrap
def count_stones(state: np.array) -> List[int]:
    white = (state == 1).sum().item()
    black = (state == -1).sum().item()
    return [white, black]

@timer_wrap
def get_phase(state: np.array) -> List[bool]:
    w, b = count_stones(state)
    if w > 3:
        ww = False
    else:
        ww = True

    if b > 3:
        bb = False
    else:
        bb = True
    
    return ww, bb

@timer_wrap
def input_next_add(state: np.array, colour: int, moven : int, eval : float) -> tuple[int]:
    invalid_flag = False
    toptext = "Move %i with eval %.2f" %(moven, eval)
    while True:
        if not invalid_flag:
            move = gui.input(1, texttop=toptext, textbottom="Where should a stone be added?", state=state)[0]
        else:
            move = gui.input(1, texttop=toptext, textbottom="There is already a stone there!\nWhere should a stone be added?", state=state)[0]

        if move == "z" or move == "zzz" or move == "ABORT":
            return move
        
        if state[move] == 0:
            break
        else:
            invalid_flag = True

    state[move] = colour
    return move

@timer_wrap
def input_next_remove(state: np.array, colour: int, moven : int, eval : float) -> None:
    invalid_nostone = False
    invalid_ownstone = False
    cannot_back = False
    toptext = "Move %i with eval %.2f" %(moven, eval)
    while True:
        if not invalid_nostone and not invalid_ownstone and not cannot_back:
            move = gui.input(1, texttop=toptext, textbottom="Please remove an opposing stone.", state=state)[0]
        elif cannot_back:
            move = gui.input(1, texttop=toptext, textbottom="Cannot go back/quit at this stage!\nPlease make a move and go back after.", state=state)[0]
            cannot_back = False
        elif invalid_nostone and not invalid_ownstone:
            move = gui.input(1, texttop=toptext, textbottom="There is no stone there!\nPlease remove an opposing stone.", state=state)[0]
        elif not invalid_nostone and invalid_ownstone:
            move = gui.input(1, texttop=toptext, textbottom="That's your own stone!\nPlease remove an opposing stone.", state=state)[0]

        if move == "z" or move == "zzz" or move == "ABORT":
            cannot_back = True
        else:
            if state[move] == -colour:
                break
            elif state[move] == colour:
                invalid_nostone = False
                invalid_ownstone = True
            else:
                invalid_nostone = True
                invalid_ownstone = False
    state[move] = 0

@timer_wrap
def input_next_move(state: np.array, colour: int, is_late_game : bool, moven : int, eval : float) -> tuple[int]:
    toptext = "Move %i with eval %.2f" %(moven, eval)
    base = "Please move a stone."
    bottomtext = base
    while True:
        move = gui.input(2, texttop = toptext, textbottom = bottomtext, state = state)
        if move[0] == "z" or move[0] == "zzz" or move[0] == "ABORT":
            move = move[0]
            return move
        
        coords_from = move[0]
        coords_to = move[1]
        if state[coords_from] == colour:
            if state[coords_to] == 0:
                if is_late_game:
                    break
                else:
                    if coords_to in get_neighbor_free(state)[coords_from[0]][coords_from[1]][coords_from[2]]:
                        break
                    else:
                        bottomtext = "Cannot reach target from origin!\n" + base
            else:
                bottomtext = "Target at second click is not empty!\n" + base
        else:
            bottomtext = "None of your stones is at the first click!\n" + base

    state[coords_from] = 0
    state[coords_to] = colour
    return coords_to

@timer_wrap
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

@timer_wrap
def initialize_boardvalues(big_cross : float = FOUR_NEIGH_POSITIONS_MULTI, 
                            little_cross : float = THREE_NEIGH_POSITIONS_MULTI, 
                            corner : float = CORNER_POSITION_MULTI) -> np.array:
    board_value = np.array([
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

@timer_wrap
def get_neighbor_free(state : np.array, neigh_map : List = neighbors_map) -> List:
    """ Returns list of free neighboring cells for each cell"""
    free_neighs = [[[[] for _ in range(3)] for _ in range(3)] for _ in range(3)]
    indices = np.where(state == 0)
    positions = list(zip(*indices))
    for index in positions:
        i, j, k = index
        for neigh in neigh_map[i][j][k]:
            l, m, n = neigh
            free_neighs[l][m][n].append(index)

    return free_neighs

@timer_wrap
def check_mill(state: np.array, move: tuple[int]) -> bool:
    colour = state[move]
        
    ring, x, y = move

    if state[ring, x, y - 1] == colour and state[ring, x, y - 2] == colour:
        return True
    if state[ring, x - 1, y] == colour and state[ring, x - 2, y] == colour:
        return True
    if (x == 1 or y == 1) and state[ring - 1, x, y] == colour and state[ring - 2, x, y] == colour:
        return True
    
    return False
    

@timer_wrap
def legal_moves_early(state : np.array) -> List:
    moves = []
    indices = np.where(state == 0)
    pieces = list(zip(*indices))
    for index in pieces:
        if not (index[1] == 1 and index[2] == 1):
            moves.append(tuple(index))
    return moves

@timer_wrap
def legal_moves_mid(state : np.array, colour : int, free_spaces : Any = None) -> List:
    moves = []

    if free_spaces is None:
        free_spaces = get_neighbor_free(state)

    indices = np.where(state == colour)
    pieces = list(zip(*indices))
    for index in pieces:
        i, j, k = index
        for free in free_spaces[i][j][k]:
            moves.append([tuple((i, j, k)), tuple(free)])
    return moves

@timer_wrap
def legal_moves_end(state : np.array, colour : int) -> List:
    moves = []
    indices = np.where(state == colour)
    pieces = list(zip(*indices))
    empty = legal_moves_early(state)
    for index in pieces:
        for emp in empty:
            moves.append([tuple(index), tuple(emp)])
    return moves

@timer_wrap
def removeable_pieces(state : np.array, colour : int) -> List:
    indices = np.where(state == -colour)
    pieces = list(zip(*indices))
    i = 0
    while i < len(pieces):
        if check_mill(state, tuple(pieces[i])):
            pieces.pop(i)
        else:
            i += 1
    if len(pieces) > 0:
        return pieces
    else:
        return list(zip(*indices))

@timer_wrap
def new_board_state_early(state : np.array, move : tuple[int], colour : int) -> List:
    new_states = []
    original_state = np.copy(state)
    original_state[move] = colour
    if check_mill(original_state, move):
        for index in removeable_pieces(original_state, colour):
            dummy_state = np.copy(original_state)
            dummy_state[tuple(index)] = 0
            new_states.append(dummy_state)
    else:
        new_states.append(original_state)
    return new_states

@timer_wrap
def new_board_state_mid(state : np.array, move : List[tuple[int]], colour : int) -> List:
    new_states = []
    original_state = np.copy(state)
    move_from = move[0]
    move_to = move[1]
    original_state[move_from] = 0
    original_state[move_to] = colour
    if check_mill(original_state, move_to):
        for index in removeable_pieces(original_state, colour):
            dummy_state = np.copy(original_state)
            dummy_state[tuple(index)] = 0
            new_states.append(dummy_state)
    else:
        new_states.append(original_state)
    return new_states
        
@timer_wrap
def evaluate_position(state : np.array, 
                        move : int, 
                        board_value : np.array = board_value, 
                        legal_move_weight : float = LEGAL_MOVES_WEIGHT,
                        open_mill_weight : float = OPEN_MILL_WEIGHT,
                        terminal_result : int = None) -> float:

    num_white_stones, num_black_stones = count_stones(state)
    free_spaces = get_neighbor_free(state)

    if move < 18:
        is_early_game = True
    else:
        is_early_game = False

    if is_early_game or num_white_stones == 3 or num_black_stones == 3:
        legal_moves_white = 0
        legal_moves_black = 0
    else:
        legal_moves_white = len(legal_moves_mid(state, 1, free_spaces))
        legal_moves_black = len(legal_moves_mid(state, -1, free_spaces))

    if terminal_result is None:
        terminal_result = is_terminal_node(state, is_early_game, free_spaces, legal_moves_white, legal_moves_black, num_white_stones, num_black_stones)
    if abs(terminal_result) == 1:
        return terminal_result * 9001

    piece_value = state * board_value
    open_white, open_black = check_possible_mills_array(state)
    return float(piece_value.sum()) + legal_move_weight * (legal_moves_white - legal_moves_black) + open_mill_weight * (open_white - open_black)

@timer_wrap
def get_children_early(state : np.array, colour : int):
    children = []
    moves = legal_moves_early(state)
    for i, move in enumerate(moves):
        children += new_board_state_early(state, move, colour)
    return children

@timer_wrap
def get_children_mid(state : np.array, colour : int, is_late_game : bool = False):
    children = []
    if is_late_game:
        moves = legal_moves_end(state, colour)
    else:
        moves = legal_moves_mid(state, colour)
    for i, move in enumerate(moves):
        children += new_board_state_mid(state, move, colour)
    return children

@timer_wrap
def is_terminal_node(state : np.array, 
                        is_early_game : bool = False,
                        free_spaces : int  = None,
                        legal_moves_white : int = None,
                        legal_moves_black : int = None,
                        num_white_stones : int = None,
                        num_black_stones : int = None) -> int:
    
    if num_white_stones is None or num_black_stones is None:
        num_white_stones, num_black_stones = count_stones(state)

    if free_spaces is None:
        free_spaces = get_neighbor_free(state)

    # Check for win
    if not is_early_game:
        if num_white_stones < 3:
            return -1 # Black has won
        if num_black_stones < 3:
            return 1 # White has won
        
        if legal_moves_white is None:
            legal_moves_white = len(legal_moves_mid(state, 1, free_spaces))
        if legal_moves_black is None:
            legal_moves_black = len(legal_moves_mid(state, -1, free_spaces))

        if num_white_stones > 3:
            if legal_moves_white == 0:
                return -1 # Black has won
        if num_black_stones > 3:
            if legal_moves_black == 0:
                return 1 # White has won
    
    return 0 # Still undecided
    

transposition_table = {}

@timer_wrap
def board_to_key(board: np.array) -> str:
    return board.tostring()


@timer_wrap
def minimax(node: np.array, 
            depth: int, 
            move: int,
            alpha: float, 
            beta: float, 
            maximizingPlayer: bool, 
            maximinzing_end: bool,
            minimizing_end: bool,
            call_count: int = 0,
            eval_pre : float = None) -> tuple[float, np.array, int]:
    call_count += 1  # Increment the counter each time the function is called
    
    #Transposition table
    key = board_to_key(node)
    if key in transposition_table and transposition_table[key][1] >= depth:
        return transposition_table[key][0], node, call_count


    if move < 18:
        is_terminal = is_terminal_node(node, is_early_game=True)
    else:
        is_terminal = is_terminal_node(node, is_early_game=False)

    if depth == 0 or abs(is_terminal) == 1:
        if eval_pre is None:
            eval = evaluate_position(node, move=move, terminal_result=is_terminal)
            transposition_table[key] = (eval, depth)
            return eval, node, call_count
        else:
            transposition_table[key] = (eval_pre, depth)
            return eval_pre, node, call_count

    best_node = None

    if maximizingPlayer:
        maxEval = float('-inf')

        #Get Children
        if move < 18:
            children = get_children_early(node, 1)
        else:
            children = get_children_mid(node, 1, maximinzing_end)

        # Evaluate and sort moves
        evaluated_children = [(child, evaluate_position(child, move = move + 1)) for child in children]
        evaluated_children.sort(key=lambda x: x[1], reverse=True)

        if move < 18:
            for child, pre_eval in evaluated_children:
                eval, _, call_count = minimax(child, depth - 1, move + 1, alpha, beta, False, False, False, call_count, pre_eval)
                if eval > maxEval:
                    maxEval = eval
                    best_node = child
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break  # Beta cut-off
            transposition_table[key] = (maxEval, depth)
            return maxEval, best_node, call_count
        else:
            for child, pre_eval in evaluated_children:
                maximinzing_end, minimizing_end = get_phase(child)
                eval, _, call_count = minimax(child, depth - 1, move + 1, alpha, beta, False, maximinzing_end, minimizing_end, call_count, pre_eval)
                if eval > maxEval:
                    maxEval = eval
                    best_node = child
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break  # Beta cut-off
            transposition_table[key] = (maxEval, depth)
            return maxEval, best_node, call_count
    else:
        minEval = float('inf')


        #Get Children
        if move < 18:
            children = get_children_early(node, -1)
        else:
            children = get_children_mid(node, -1, minimizing_end)

        # Evaluate and sort moves
        evaluated_children = [(child, evaluate_position(child, move = move + 1)) for child in children]
        evaluated_children.sort(key=lambda x: x[1])

        if move < 18:
            for child, pre_eval in evaluated_children:
                eval, _, call_count = minimax(child, depth - 1, move + 1, alpha, beta, True, False, False, call_count, pre_eval)
                if eval < minEval:
                    minEval = eval
                    best_node = child
                beta = min(beta, eval)
                if beta <= alpha:
                    break  # Alpha cut-off
            transposition_table[key] = (minEval, depth)
            return minEval, best_node, call_count
        else:
            for child, pre_eval in evaluated_children:
                maximinzing_end, minimizing_end = get_phase(child)
                eval, _, call_count = minimax(child, depth - 1, move + 1, alpha, beta, True, maximinzing_end, minimizing_end, call_count, pre_eval)
                if eval < minEval:
                    minEval = eval
                    best_node = child
                beta = min(beta, eval)
                if beta <= alpha:
                    break  # Alpha cut-off
            transposition_table[key] = (minEval, depth)
            return minEval, best_node, call_count
    
@timer_wrap
def calc_depth_for_eval_calls(state : np.array, 
                              move_counter : int, 
                              late_game_white : bool, 
                              late_game_black : bool, 
                              max_calls : int = int(1e5), 
                              pruning_factor : float = 1.5) -> List[int]:
    approx_calls_all = []
    depths = []
    depth_count = 1
    approx_calls = 0
    while approx_calls < max_calls:
        if move_counter < 4:
            approx_calls = ((len(get_children_early(state, 1)) + len(get_children_early(state, -1)))/2.)**(depth_count/pruning_factor)
        elif move_counter < 19:
            approx_calls = ((len(get_children_early(state, 1)) + len(get_children_early(state, -1)))/2.)**(depth_count/pruning_factor)
        else:
            approx_calls = ((len(get_children_mid(state, 1, late_game_white)) + len(get_children_mid(state, -1, late_game_black)))/2.)**(depth_count/pruning_factor)
        approx_calls_all.append(approx_calls)
        depths.append(depth_count)
        depth_count += 1
    return depths[-2], int(np.floor(approx_calls_all[-2]))

@timer_wrap
def book_moves(state: np.array, colour : int) -> Any:
    white, black = check_possible_mills_array(state)
    if white > 0:
        return None
    elif black > 0:
        return None
    else:
        for j, k in [[0, 1], [1, 0], [2, 1], [1, 2]]:
            if state[1, j, k] == 0:
                return 0., new_board_state_early(state, tuple((1, j, k)), colour)[0], 1
            
    return None

@timer_wrap
def initialize_mill_array() -> List:
    mills = []
    for i in range(3):
        for j in [0, 2]:
            mills.append([(i, 0, j) , (i, 1, j), (i, 2, j)])
            mills.append([(i, j, 0) , (i, j, 1), (i, j, 2)])
    
    for i, j in [[0, 1], [1, 0], [1, 2], [2, 1]]:
        mills.append([(0, i, j), (1, i, j), (2, i, j)])
    return np.array(mills)

mills_array = initialize_mill_array()

@timer_wrap
def check_possible_mills_array(state: np.array) -> List:
    results = np.sum(state[tuple(mills_array.T)], axis=0)

    possible_white_mills = np.count_nonzero(results == 2)
    possible_black_mills = np.count_nonzero(results == -2)
    
    return possible_white_mills, possible_black_mills
