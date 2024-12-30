import torch
import threading
import queue
import mills_engine as mills
import tkinter as tk
import gui
import time

def run_minimax_early(q : queue.Queue, board_state, depth, BASE_ALPHA, BASE_BETA, COMPUTER_MAX, event : threading.Event):
    minimax_result = mills.minimax_early(board_state, depth, BASE_ALPHA, BASE_BETA, COMPUTER_MAX)
    q.put(minimax_result)
    event.set()

# Function to check if the minimax computation is complete
def check_minimax_result(root : tk.Tk):
    if event.is_set():
        gui.close_board(root)  # Close the show_board window
    else:
        time.sleep(0.1)
        root.after(100, check_minimax_result(root))  # Check again after 100 ms

BASE_ALPHA = float('-inf')
BASE_BETA = float('inf')
board_state = torch.zeros((3,3,3), dtype=int)
COMPUTER_MAX = False

root = gui.show_board("Test")
event = threading.Event()
q = queue.Queue()
minimax_thread = threading.Thread(target = run_minimax_early, args=(q, board_state, 2, BASE_ALPHA, BASE_BETA, COMPUTER_MAX, event))
minimax_thread.start()
#eval, board_state, calls = mills.minimax_early(board_state, depth, BASE_ALPHA, BASE_BETA, COMPUTER_MAX)
root.after(1000, check_minimax_result(root))
root.mainloop()
minimax_thread.join()
eval, board_state, calls = q.get()

print(eval)