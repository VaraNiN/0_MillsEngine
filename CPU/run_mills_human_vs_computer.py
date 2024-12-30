import numpy as np
import re
import time
from typing import List, Any
from colorama import Fore as cf, Style as cs
import threading
import queue
import mills_engine as mills
import tkinter as tk
import gui
from datetime import datetime


def red(string : str) -> None:
    print(cf.RED + string + cs.RESET_ALL)

FOLDER = "CPU/Games/"

PLAYER_COLOUR = 1
MAX_APPROX_EVAL_CALLS_EARLY = 5e4        # How many eval calls are approximately allowed early
MAX_APPROX_EVAL_CALLS_MID = 5e4        # How many eval calls are approximately allowed mid to late
APPROX_PRUNING_FACTOR = 1.5        # Approximation of how well alpha-beta pruning works. Worst case = 1.; Best Case = 2.

board_state = np.zeros((3,3,3), dtype=int)
board_state_history = [np.copy(board_state)]

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
    prev_array = board_state
    for i in range(int(1e5)):
        random_array = np.random.choice([-1, 0, 1], size=(3, 3, 3))
        a, b = mills.check_possible_mills_list(random_array)
        c, d = mills.check_possible_mills_array(random_array)
        if True:   
            if a != c:
                print(i, "w", a, c)
                print(mills.check_possible_mills(random_array, 1))
                mills.show_position(random_array, check_validity=False)
            if b != d:
                print(i, "b", b, d)
                print(mills.check_possible_mills(random_array, -1))
                mills.show_position(random_array, check_validity=False)

            if np.array_equal(prev_array, random_array):
                print(random_array)
            else:
                prev_array = random_array
    mills.print_report()
    exit()


if True:
    board_state_history = np.load("CPU/Sample_Mid.npy")
    board_state_history = [board_state_history[i] for i in range(board_state_history.shape[0])]
    board_state = np.copy(board_state_history[-1])
    move_number = len(board_state_history) - 1


if False:
    board_state_history = np.load("CPU/Sample_Late.npy")
    board_state_history = [board_state_history[i] for i in range(board_state_history.shape[0])]
    board_state = np.copy(board_state_history[-1])
    move_number = len(board_state_history) - 1





### Logic start

MAX_APPROX_EVAL_CALLS_EARLY = int(MAX_APPROX_EVAL_CALLS_EARLY)
MAX_APPROX_EVAL_CALLS_MID = int(MAX_APPROX_EVAL_CALLS_MID)

def run_minimax_early(event : threading.Event, q : queue.Queue, board_state, depth, BASE_ALPHA, BASE_BETA, COMPUTER_MAX):
    minimax_result = mills.minimax_early(board_state, depth, BASE_ALPHA, BASE_BETA, COMPUTER_MAX)
    q.put(minimax_result)
    event.set()

def run_minimax_mid(event : threading.Event, q : queue.Queue, board_state, depth, BASE_ALPHA, BASE_BETA, COMPUTER_MAX, endgame_white, endgame_black):
    minimax_result = mills.minimax_mid(board_state, depth, BASE_ALPHA, BASE_BETA, COMPUTER_MAX, endgame_white, endgame_black)
    q.put(minimax_result)
    event.set()

# Function to check if the minimax computation is complete
def check_minimax_result(root : tk.Tk, event : threading.Event):
    if event.is_set():
        root.destroy() # Close the show_board window
    else:
        root.after(100, check_minimax_result, root, event)# Check again after 100 ms

try:
    while not finished_flag:
        #mills.show_position(board_state)
        print("\nMove %i with eval %.2f:" %(move_number + 1, current_eval))

        # Early Game
        if move_number < 18:
            if player_turn: # Player Move
                if PLAYER_COLOUR == 1:
                    print("Please place white stone %i / 9" %(move_number // 2 + 1))
                else:
                    print("Please place black stone %i / 9" %(move_number // 2 + 1))
                move = mills.input_next_add(board_state, PLAYER_COLOUR, move_number + 1, current_eval)
                #current_eval = mills.evaluate_position(board_state, is_early_game=True)
                if move == "ABORT":
                    mills.print_report()
                    np.save(FOLDER + datetime.now().strftime("%Y-%m-%d_%H:%M:%S") + ".npy", board_state_history)
                    exit()
                elif move == "z":
                    if move_number >= 2:
                        move_number -= 2
                        board_state = np.copy(board_state_history[move_number])
                        board_state_history.pop(-1)
                        board_state_history.pop(-1)
                        print("Going back a full move.")
                    else:
                        red("Cannot go further back.")
                elif move == "zzz":
                    if move_number >= 1:
                        move_number -= 1
                        board_state = np.copy(board_state_history[move_number])
                        board_state_history.pop(-1)
                        print("Going back half a move.")
                        red("This switches sides!")
                        PLAYER_COLOUR *= -1
                        COMPUTER_MAX = not COMPUTER_MAX
                    else:
                        red("Cannot go further back.")
                else:
                    if mills.check_mill(board_state, move):
                        #mills.show_position(board_state)
                        mills.input_next_remove(board_state, PLAYER_COLOUR, move_number + 1, current_eval)
                        #current_eval = mills.evaluate_position(board_state, is_early_game=True)
                    move_number += 1
                    board_state_history.append(np.copy(board_state))
                    player_turn = False
            else: # Computer Move
                depth, approx_calls = mills.calc_depth_for_eval_calls(board_state, True, False, False, MAX_APPROX_EVAL_CALLS_EARLY, APPROX_PRUNING_FACTOR)
                if PLAYER_COLOUR == 1:
                    display = "Computer places black stone %i / 9\nwith search depth %i (~%s calls)" %(move_number // 2 + 1, depth, f"{approx_calls:,}")
                    print(display)
                else:
                    display = "Computer places white stone %i / 9\nwith search depth %i (~%s calls)" %(move_number // 2 + 1, depth, f"{approx_calls:,}")
                    print(display)
                start_time = time.time()
                if mills.book_moves(board_state, -PLAYER_COLOUR) is not None:
                    eval, board_state, calls = mills.book_moves(board_state, -PLAYER_COLOUR)
                else:
                    if True:
                        event = threading.Event()
                        q = queue.Queue()
                        minimax_thread = threading.Thread(target = run_minimax_early, args=(event, q, board_state, depth, BASE_ALPHA, BASE_BETA, COMPUTER_MAX))
                        minimax_thread.start()
                        root = gui.show_board(texttop="Move %i with eval %.2f:" %(move_number + 1, current_eval), textbottom=display, state=board_state)
                        root.after(100, check_minimax_result, root, event)
                        root.mainloop()
                        minimax_thread.join()
                        eval, board_state, calls = q.get()
                    else:
                        #eval, board_state, calls = mills.minimax_early_multi(board_state, depth, BASE_ALPHA, BASE_BETA, COMPUTER_MAX, max_workers=MAX_THREADS)
                        eval, board_state, calls = mills.parallel_minimax_early(board_state, depth, BASE_ALPHA, BASE_BETA, COMPUTER_MAX)
                        #eval, board_state, calls = mills.minimax_early(board_state, depth, BASE_ALPHA, BASE_BETA, COMPUTER_MAX)
                
                end_time = time.time()# Calculate the elapsed time
                elapsed_time = end_time - start_time

                # Convert elapsed time to minutes, seconds, and milliseconds
                minutes = int(elapsed_time // 60)
                seconds = int(elapsed_time % 60)
                milliseconds = int((elapsed_time * 1000) % 1000)

                print(f"Move made after {calls:,} of {MAX_APPROX_EVAL_CALLS_EARLY:,} calls: {minutes} minutes, {seconds} seconds, {milliseconds} milliseconds")

                current_eval = eval
                move_number += 1
                board_state_history.append(np.copy(board_state))
                player_turn = True
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
                    move = mills.input_next_move(board_state, PLAYER_COLOUR, endgame_white, move_number + 1, current_eval)
                else:
                    move = mills.input_next_move(board_state, PLAYER_COLOUR, endgame_black, move_number + 1, current_eval)
                if move == "ABORT":
                    mills.print_report()
                    np.save(FOLDER + datetime.now().strftime("%Y-%m-%d_%H:%M:%S") + ".npy", board_state_history)
                    exit()
                elif move == "z":
                    move_number -= 2
                    board_state = np.copy(board_state_history[move_number])
                    board_state_history.pop(-1)
                    board_state_history.pop(-1)
                    print("Going back a full move.")
                elif move == "zzz":
                    move_number -= 1
                    board_state = np.copy(board_state_history[move_number])
                    board_state_history.pop(-1)
                    print("Going back half a move.")
                    red("This switches sides!")
                    PLAYER_COLOUR *= -1
                    COMPUTER_MAX = not COMPUTER_MAX
                else:
                    if mills.check_mill(board_state, move):
                        #mills.show_position(board_state)
                        mills.input_next_remove(board_state, PLAYER_COLOUR, move_number + 1, current_eval)
                    move_number += 1
                    board_state_history.append(np.copy(board_state))
                    player_turn = False
            else: # Computer Move
                depth, approx_calls = mills.calc_depth_for_eval_calls(board_state, False, endgame_white, endgame_black, MAX_APPROX_EVAL_CALLS_MID, APPROX_PRUNING_FACTOR)
                display = "Computer thinking with depth %i (~%s calls)" %(depth, f"{approx_calls:,}")
                print(display)

                start_time = time.time()
                event = threading.Event()
                q = queue.Queue()
                minimax_thread = threading.Thread(target = run_minimax_mid, args=(event, q, board_state, depth, BASE_ALPHA, BASE_BETA, COMPUTER_MAX, endgame_white, endgame_black))
                minimax_thread.start()
                root = gui.show_board(texttop="Move %i with eval %.2f:" %(move_number + 1, current_eval), textbottom=display, state=board_state)
                root.after(100, check_minimax_result, root, event)
                root.mainloop()
                minimax_thread.join()
                eval, board_state, calls = q.get()
                end_time = time.time()# Calculate the elapsed time

                elapsed_time = end_time - start_time

                # Convert elapsed time to minutes, seconds, and milliseconds
                minutes = int(elapsed_time // 60)
                seconds = int(elapsed_time % 60)
                milliseconds = int((elapsed_time * 1000) % 1000)

                print(f"Move made after {calls:,} of {MAX_APPROX_EVAL_CALLS_MID:,} calls: {minutes} minutes, {seconds} seconds, {milliseconds} milliseconds")
                current_eval = eval
                move_number += 1
                board_state_history.append(np.copy(board_state))
                player_turn = True

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
    print("\n")
    pass
except tk.TclError:
    print("\n")
    pass


mills.print_report()

np.save(FOLDER + datetime.now().strftime("%Y-%m-%d_%H:%M:%S") + ".npy", board_state_history)