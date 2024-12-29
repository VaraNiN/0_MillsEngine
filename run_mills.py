import torch
import numpy as np
import re
import time
from typing import List, Any
from colorama import Fore as cf, Style as cs
import mills_engine as mills


def red(string : str) -> None:
    print(cf.RED + string + cs.RESET_ALL)


PLAYER_COLOUR = 1
EARLY_DEPTH = 5
MID_DEPTH = 7
END_DEPTH = 6
MAX_APPROX_EVAL_CALLS = 1e4

board_state = torch.zeros((3,3,3), dtype=int)
board_state_history = [[np.nan, torch.clone(board_state)]]

BASE_ALPHA = float('-inf')
BASE_BETA = float('inf')

if PLAYER_COLOUR == 1:
    player_turn = True
    COMPUTER_MAX = False
else:
    player_turn = False
    COMPUTER_MAX = True


current_eval = 0
move_number = 0
finished_flag = False
endgame_white = False
endgame_black = False

if False:
    board_state[0, 2, 0] = 1
    board_state[1, 1, 0] = 1
    board_state[1, 2, 0] = 1
    board_state[1, 2, 1] = 1
    board_state[1, 0, 2] = 1
    board_state[1, 2, 2] = 1
    board_state[2, 2, 1] = 1
    board_state[2, 1, 2] = 1
    board_state[2, 2, 2] = 1

    board_state[0, 1, 0] = -1
    board_state[0, 2, 1] = -1
    board_state[0, 0, 2] = -1
    board_state[1, 0, 0] = -1
    board_state[1, 0, 1] = -1
    board_state[1, 1, 2] = -1
    board_state[2, 0, 0] = -1
    board_state[2, 2, 0] = -1

    move_number = 18
    board_state_history.append([np.nan, torch.clone(board_state)])


if False:
    board_state[1, 0, 2] = 1
    board_state[1, 2, 0] = 1
    board_state[1, 2, 2] = 1

    board_state[0, 0, 1] = -1
    board_state[1, 0, 1] = -1
    board_state[2, 0, 1] = -1
    board_state[0, 1, 0] = -1
    board_state[1, 1, 0] = -1

    move_number = 46
    board_state_history.append([np.nan, torch.clone(board_state)])

try:
    while not finished_flag:
        mills.show_position(board_state)
        print("Move %i with eval %.2f:" %(move_number + 1, current_eval))

        # Early Game
        if move_number < 18:
            if player_turn: # Player Move
                if PLAYER_COLOUR == 1:
                    print("Please place white stone %i / 9" %(move_number // 2 + 1))
                else:
                    print("Please place black stone %i / 9" %(move_number // 2 + 1))
                move = mills.input_next_add(board_state, PLAYER_COLOUR)
                if move == "z":
                    if move_number >= 2:
                        move_number -= 2
                        board_state = torch.clone(board_state_history[move_number][1])
                        board_state_history.pop(-1)
                        board_state_history.pop(-1)
                        print("Going back a full move.")
                    else:
                        red("Cannot go further back.")
                elif move == "zzz":
                    if move_number >= 1:
                        move_number -= 1
                        board_state = torch.clone(board_state_history[move_number][1])
                        board_state_history.pop(-1)
                        print("Going back half a move.")
                        red("This switches sides!")
                        PLAYER_COLOUR *= -1
                        COMPUTER_MAX = not COMPUTER_MAX
                    else:
                        red("Cannot go further back.")
                else:
                    if mills.check_mill(board_state, move):
                        mills.show_position(board_state)
                        mills.input_next_remove(board_state, PLAYER_COLOUR)
                    board_state_history.append([np.nan, torch.clone(board_state)])
                    player_turn = False
                    move_number += 1
            else: # Computer Move
                if PLAYER_COLOUR == 1:
                    print("Computer places black stone %i / 9 with search depth %i" %(move_number // 2 + 1, EARLY_DEPTH))
                else:
                    print("Computer places white stone %i / 9 with search depth %i" %(move_number // 2 + 1, EARLY_DEPTH))
                start_time = time.time()
                eval, board_state = mills.minimax_early(board_state, EARLY_DEPTH, BASE_ALPHA, BASE_BETA, COMPUTER_MAX)
                end_time = time.time()# Calculate the elapsed time
                elapsed_time = end_time - start_time

                # Convert elapsed time to minutes, seconds, and milliseconds
                minutes = int(elapsed_time // 60)
                seconds = int(elapsed_time % 60)
                milliseconds = int((elapsed_time * 1000) % 1000)

                print(f"Move made after: {minutes} minutes, {seconds} seconds, {milliseconds} milliseconds")
                current_eval = eval
                board_state_history.append([eval, torch.clone(board_state)])
                player_turn = True
                move_number += 1
            # Check for win
            check_win = mills.is_terminal_node(board_state, is_early_game = True)
            if check_win == PLAYER_COLOUR:
                print("Congratulations! You won!")
                finished_flag = True
            if check_win == -PLAYER_COLOUR:
                print("The computer won. Better Luck next time!!")
                finished_flag = True

        # Mid and End Game
        else:
            # Check for end game
            white_stones_left, black_stones_left = mills.count_stones(board_state)
            if white_stones_left <= 3:
                endgame_white = True
            if black_stones_left <= 3:
                endgame_black = True

            if player_turn: # Player Move
                if PLAYER_COLOUR == 1:
                    move = mills.input_next_move(board_state, PLAYER_COLOUR, endgame_white)
                else:
                    move = mills.input_next_move(board_state, PLAYER_COLOUR, endgame_black)
                if move == "z":
                    move_number -= 2
                    board_state = torch.clone(board_state_history[move_number][1])
                    board_state_history.pop(-1)
                    board_state_history.pop(-1)
                    print("Going back a full move.")
                elif move == "zzz":
                    move_number -= 1
                    board_state = torch.clone(board_state_history[move_number][1])
                    board_state_history.pop(-1)
                    print("Going back half a move.")
                    red("This switches sides!")
                    PLAYER_COLOUR *= -1
                    COMPUTER_MAX = not COMPUTER_MAX
                else:
                    if mills.check_mill(board_state, move):
                        mills.show_position(board_state)
                        mills.input_next_remove(board_state, PLAYER_COLOUR)
                    board_state_history.append([np.nan, torch.clone(board_state)])
                    player_turn = False
                    move_number += 1
            else: # Computer Move
                if endgame_white or endgame_black:
                    depth = END_DEPTH
                else:
                    depth = MID_DEPTH
                print("Computer thinking with depth %i" %depth)
                start_time = time.time()
                eval, board_state = mills.minimax_mid(board_state, depth, BASE_ALPHA, BASE_BETA, COMPUTER_MAX, endgame_white, endgame_black)
                end_time = time.time()# Calculate the elapsed time
                elapsed_time = end_time - start_time

                # Convert elapsed time to minutes, seconds, and milliseconds
                minutes = int(elapsed_time // 60)
                seconds = int(elapsed_time % 60)
                milliseconds = int((elapsed_time * 1000) % 1000)

                print(f"Move made after: {minutes} minutes, {seconds} seconds, {milliseconds} milliseconds")
                current_eval = eval
                board_state_history.append([eval, torch.clone(board_state)])
                player_turn = True
                move_number += 1

            # Check for win
            check_win = mills.is_terminal_node(board_state)
            if check_win == PLAYER_COLOUR:
                mills.show_position(board_state)
                print("Congratulations! You won!")
                finished_flag = True
            if check_win == -PLAYER_COLOUR:
                mills.show_position(board_state)
                print("The computer won. Better Luck next time!!")
                finished_flag = True

except KeyboardInterrupt:
    print()
    pass

mills.TIMER.print_report()