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

mills.ENABLE_TIMING = True


# TODO: Use AI to train weights
# TODO: Implement Draw condition
# TODO: Use hidden values at (i, 1, 1) to encode which players turn it is, and if it's in the late game or not

def red(string : str) -> None:
    print(cf.RED + string + cs.RESET_ALL)

PLAYER_COLOUR = -1
CPU_THINK_TIME_EARLY = 3     #[s] How long the computer is allowed to think in the early game
CPU_THINK_TIME_MID = 8     #[s] How long the computer is allowed to think in the mid and late game

board_state = np.zeros((3,3,3), dtype=int)
board_state_history = [np.copy(board_state)]

BASE_ALPHA = float('-inf')
BASE_BETA = float('inf')


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

if False:
    board_state_history = np.load("CPU/Move_History.npy")
    board_state_history = [board_state_history[i] for i in range(board_state_history.shape[0])]
    board_state = np.copy(board_state_history[-4])
    move_number = len(board_state_history) - 4

if False:
    board_state_history = np.load("CPU/Sample_Mid.npy")
    board_state_history = [board_state_history[i] for i in range(board_state_history.shape[0])]
    board_state = np.copy(board_state_history[-1])
    move_number = len(board_state_history) - 1


if False:
    board_state_history = np.load("CPU/Sample_Late.npy")
    board_state_history = [board_state_history[i] for i in range(board_state_history.shape[0])]
    board_state = np.copy(board_state_history[-3])
    move_number = len(board_state_history) - 3





### Logic start

def run_minimax(event : threading.Event, q : queue.Queue, board_state, move, BASE_ALPHA, BASE_BETA, COMPUTER_MAX, endgame_white, endgame_black, time_limit):
    minimax_result = mills.iterative_deepening(board_state, move, BASE_ALPHA, BASE_BETA, COMPUTER_MAX, endgame_white, endgame_black, time_limit)
    #minimax_result = mills.minimax(board_state, 4, move, BASE_ALPHA, BASE_BETA, COMPUTER_MAX, endgame_white, endgame_black)
    q.put(minimax_result)
    event.set()

# Function to check if the minimax computation is complete
def check_minimax_result(root : tk.Tk, event : threading.Event):
    if event.is_set():
        root.destroy() # Close the show_board window
    else:
        root.after(100, check_minimax_result, root, event)# Check again after 100 ms

current_eval = 0
move_number = 0
finished_flag = False
endgame_white = False
endgame_black = False
total_elapsed_time = 0

if move_number % 2 == 0:
    if PLAYER_COLOUR == 1:
        COMPUTER_MAX = False
        player_turn = True
    else: 
        COMPUTER_MAX = True
        player_turn = False
else:
    if PLAYER_COLOUR == 1:
        COMPUTER_MAX = False
        player_turn = False
    else:
        COMPUTER_MAX = True
        player_turn = True


try:
    while not finished_flag:
        mills.show_position(board_state)
        print("\nMove %i with eval %.2f:" %(move_number + 1, current_eval))

        # Early Game
        if move_number < 18:
            if player_turn: # Player Move
                if PLAYER_COLOUR == 1:
                    print("Please place white stone %i / 9" %(move_number // 2 + 1))
                else:
                    print("Please place black stone %i / 9" %(move_number // 2 + 1))
                move = mills.input_next_add(board_state, PLAYER_COLOUR, move_number + 1, current_eval)
                if move == "ABORT":
                    mills.total_elapsed = total_elapsed_time
                    mills.report_save_quit(board_state_history)
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
                    move_number += 1
                    board_state_history.append(np.copy(board_state))
                    player_turn = False
            else: # Computer Move
                if PLAYER_COLOUR == 1:
                    display = "Computer places black stone %i" %(move_number // 2 + 1)
                else:
                    display = "Computer places white stone %i" %(move_number // 2 + 1)
                start_time = time.time()
                if False: #mills.book_moves(board_state, -PLAYER_COLOUR) is not None:
                    eval, board_state = mills.book_moves(board_state, -PLAYER_COLOUR)
                    calls = 1
                    max_depth = "Bookmove"
                else:
                    event = threading.Event()
                    q = queue.Queue()
                    mills.call_count = 0
                    minimax_thread = threading.Thread(target = run_minimax, args=(event, q, board_state, move_number, BASE_ALPHA, BASE_BETA, COMPUTER_MAX, False, False, CPU_THINK_TIME_EARLY))
                    minimax_thread.start()
                    root = gui.show_board(texttop="Move %i with eval %.2f:" %(move_number + 1, current_eval), textbottom=display, state=board_state)
                    root.after(100, check_minimax_result, root, event)
                    root.mainloop()
                    minimax_thread.join()
                    #eval, board_state = q.get()
                    eval, board_state, max_depth = q.get()
                    calls = mills.call_count
                
                end_time = time.time()# Calculate the elapsed time
                elapsed_time = end_time - start_time
                total_elapsed_time += elapsed_time

                # Convert elapsed time to minutes, seconds, and milliseconds
                minutes = int(elapsed_time // 60)
                seconds = int(elapsed_time % 60)
                milliseconds = int((elapsed_time * 1000) % 1000)

                print(f"Move made after {calls:,} calls at depth {max_depth}: {minutes} minutes, {seconds} seconds, {milliseconds} milliseconds")

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
            endgame_white, endgame_black = mills.get_phase(board_state)

            if player_turn: # Player Move
                if PLAYER_COLOUR == 1:
                    move = mills.input_next_move(board_state, PLAYER_COLOUR, endgame_white, move_number + 1, current_eval)
                else:
                    move = mills.input_next_move(board_state, PLAYER_COLOUR, endgame_black, move_number + 1, current_eval)
                if move == "ABORT":
                    mills.total_elapsed = total_elapsed_time
                    mills.report_save_quit(board_state_history)
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
                display = "Computer is thinking..."

                start_time = time.time()
                event = threading.Event()
                q = queue.Queue()
                mills.call_count = 0
                minimax_thread = threading.Thread(target = run_minimax, args=(event, q, board_state, move_number, BASE_ALPHA, BASE_BETA, COMPUTER_MAX, endgame_white, endgame_black, CPU_THINK_TIME_MID))
                minimax_thread.start()
                root = gui.show_board(texttop="Move %i with eval %.2f:" %(move_number + 1, current_eval), textbottom=display, state=board_state)
                root.after(100, check_minimax_result, root, event)
                root.mainloop()
                minimax_thread.join()
                eval, board_state, max_depth = q.get()
                calls = mills.call_count

                end_time = time.time()# Calculate the elapsed time

                elapsed_time = end_time - start_time
                total_elapsed_time += elapsed_time

                # Convert elapsed time to minutes, seconds, and milliseconds
                minutes = int(elapsed_time // 60)
                seconds = int(elapsed_time % 60)
                milliseconds = int((elapsed_time * 1000) % 1000)

                print(f"Move made after {calls:,} calls at depth {max_depth}: {minutes} minutes, {seconds} seconds, {milliseconds} milliseconds")
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

mills.total_elapsed = total_elapsed_time
mills.report_save_quit(board_state_history)