import tkinter as tk
from tkinter import messagebox
import torch
import mills_engine as mills

def on_click(event : tk.Event, root : tk.Tk , result : list, inputs : int) -> list:
    x, y = event.x, event.y
    vicinity = get_vicinity(x, y)
    if vicinity and len(result) < inputs:
        result.append(vicinity)
        if len(result) == inputs:
            root.quit()

def get_vicinity(x, y, offset : int = -50, radius : int = 20):
    vertices = {
        (0, 0, 0): (40, 40 - offset),    (0, 1, 0): (300, 40 - offset),   (0, 2, 0): (560, 40 - offset),
        (1, 0, 0): (120, 120 - offset),  (1, 1, 0): (300, 120 - offset),  (1, 2, 0): (480, 120 - offset),
        (2, 0, 0): (200, 200 - offset),  (2, 1, 0): (300, 200 - offset),  (2, 2, 0): (400, 200 - offset),
        (0, 0, 1): (40, 300 - offset),   (1, 0, 1): (120, 300 - offset),  (2, 0, 1): (200, 300 - offset),
        (2, 2, 1): (400, 300 - offset),  (1, 2, 1): (480, 300 - offset),  (0, 2, 1): (560, 300 - offset),
        (2, 0, 2): (200, 400 - offset),  (2, 1, 2): (300, 400 - offset),  (2, 2, 2): (400, 400 - offset),
        (1, 0, 2): (120, 480 - offset),  (1, 1, 2): (300, 480 - offset),  (1, 2, 2): (480, 480 - offset),
        (0, 0, 2): (40, 560 - offset),   (0, 1, 2): (300, 560 - offset),  (0, 2, 2): (560, 560 - offset)
    }

    for index, (vx, vy) in vertices.items():
        if (vx - radius <= x <= vx + radius) and (vy - radius <= y <= vy + radius):
            return index
    return None

def create_mills_board(canvas : tk.Canvas, state : torch.tensor = torch.zeros((3, 3, 3), dtype=int), width : int = 600, height : int = 600, offset : int = -50, radius : int = 20):

    # Outer square
    canvas.create_rectangle(40, 40 - offset, width-40, height-40 - offset)
    # Middle square
    canvas.create_rectangle(120, 120 - offset, width-120, height-120 - offset)
    # Inner square
    canvas.create_rectangle(200, 200 - offset, width-200, height-200 - offset)
    
    # Connecting lines
    canvas.create_line(width//2, 40 - offset, width//2, 200 - offset)
    canvas.create_line(width//2, height-40 - offset, width//2, height-200 - offset)
    canvas.create_line(40, height//2 - offset, 200, height//2 - offset)
    canvas.create_line(width-40, height//2 - offset, width-200, height//2 - offset)
    
    # Draw circles at vertices
    vertices = {
        (0, 0, 0): (40, 40 - offset),    (0, 1, 0): (300, 40 - offset),   (0, 2, 0): (560, 40 - offset),
        (1, 0, 0): (120, 120 - offset),  (1, 1, 0): (300, 120 - offset),  (1, 2, 0): (480, 120 - offset),
        (2, 0, 0): (200, 200 - offset),  (2, 1, 0): (300, 200 - offset),  (2, 2, 0): (400, 200 - offset),
        (0, 0, 1): (40, 300 - offset),   (1, 0, 1): (120, 300 - offset),  (2, 0, 1): (200, 300 - offset),
        (2, 2, 1): (400, 300 - offset),  (1, 2, 1): (480, 300 - offset),  (0, 2, 1): (560, 300 - offset),
        (2, 0, 2): (200, 400 - offset),  (2, 1, 2): (300, 400 - offset),  (2, 2, 2): (400, 400 - offset),
        (1, 0, 2): (120, 480 - offset),  (1, 1, 2): (300, 480 - offset),  (1, 2, 2): (480, 480 - offset),
        (0, 0, 2): (40, 560 - offset),   (0, 1, 2): (300, 560 - offset),  (0, 2, 2): (560, 560 - offset)
    }
    
    for index, (vx, vy) in vertices.items():
        if state[index] == 1:
            canvas.create_oval(vx-radius, vy-radius, vx+radius, vy+radius, fill="dark red")
        elif state[index] == -1:
            canvas.create_oval(vx-radius, vy-radius, vx+radius, vy+radius, fill="dark blue")
        else:
            canvas.create_oval(vx-radius, vy-radius, vx+radius, vy+radius, fill="black")

def input(len : int = 1, texttop : str = "", textbottom : str = "", state : torch.tensor = torch.zeros((3, 3, 3))):
    root = tk.Tk()
    root.title("Mills Board Click Tracker")

    width, height = 600, 700

    canvas = tk.Canvas(root, width=width, height=height)
    canvas.pack()

    if textbottom:
        canvas.create_text(300, 666, text=textbottom, font=("Arial", 16))

    if texttop:
        canvas.create_text(300, 30, text=texttop, font=("Arial", 16))
        

    create_mills_board(canvas, state)

    result = []
    canvas.bind("<Button-1>", lambda event: on_click(event, root, result, len))

    # Adding buttons
    button_z = tk.Button(root, text="Go Back Full Move", command=lambda: button_click(root, result, "z"), bg="purple", fg="white")
    button_z.pack(side=tk.LEFT, padx=10, pady=10)

    button_zzz = tk.Button(root, text="Go Back Half Move", command=lambda: button_click(root, result, "zzz"), bg="purple", fg="white")
    button_zzz.pack(side=tk.RIGHT, padx=10, pady=10)

    button_abort = tk.Button(root, text="Exit Game", command=lambda: button_click(root, result, "ABORT"), bg="red", fg="white")
    button_abort.pack(side=tk.BOTTOM, padx=10, pady=10)

    root.mainloop()
    root.destroy()

    return result if result else None

def show_board(texttop : str = "", textbottom : str = "",  state : torch.tensor = torch.zeros((3, 3, 3))):
    root = tk.Tk()
    root.title("Mills Board Click Tracker")

    width, height = 600, 700

    canvas = tk.Canvas(root, width=width, height=height)
    canvas.pack()

    if textbottom:
        canvas.create_text(300, 666, text=textbottom, font=("Arial", 16))

    if texttop:
        canvas.create_text(300, 30, text=texttop, font=("Arial", 16))

    create_mills_board(canvas, state)
    
    return root

def close_board(root : tk.Tk):
    root.destroy()


def button_click(root, result, value):
    if value == "ABORT":
        if messagebox.askyesno("Confirm Exit", "Are you sure you want to exit?"):
            result.append(value)
            root.quit()
        else:
            pass
    elif value == "z" or value == "zzz":
        if messagebox.askyesno("Confirm Return", "Are you sure you want to return to previous position?"):
            result.append(value)
            root.quit()
        else:
            pass
    else:
        result.append(value)
        root.quit()

if __name__ == "__main__":
    result = input(2)
    print(f"Result: {result}")