import tkinter as tk

#Courtesy of Co-Pilot
#TODO: Draw the game board (probably with red and blue or sth)
#TODO: Connect with actual game

def on_click(event):
    x, y = event.x, event.y
    vicinity = get_vicinity(x, y)
    if vicinity:
        print(f"Clicked at: {vicinity}")

def get_vicinity(x, y):
    vertices = {
        0: (40, 40), 1: (300, 40), 2: (560, 40),
        3: (120, 120), 4: (300, 120), 5: (480, 120),
        6: (200, 200), 7: (300, 200), 8: (400, 200),
        9: (40, 300), 10: (120, 300), 11: (200, 300),
        12: (400, 300), 13: (480, 300), 14: (560, 300),
        15: (200, 400), 16: (300, 400), 17: (400, 400),
        18: (120, 480), 19: (300, 480), 20: (480, 480),
        21: (40, 560), 22: (300, 560), 23: (560, 560)
    }
    
    radius = 20
    for index, (vx, vy) in vertices.items():
        if (vx - radius <= x <= vx + radius) and (vy - radius <= y <= vy + radius):
            return index + 1
    return None

def create_mills_board(canvas, width, height):
    # Outer square
    canvas.create_rectangle(40, 40, width-40, height-40)
    # Middle square
    canvas.create_rectangle(120, 120, width-120, height-120)
    # Inner square
    canvas.create_rectangle(200, 200, width-200, height-200)
    
    # Connecting lines
    canvas.create_line(width//2, 40, width//2, 200)
    canvas.create_line(width//2, height-40, width//2, height-200)
    canvas.create_line(40, height//2, 200, height//2)
    canvas.create_line(width-40, height//2, width-200, height//2)
    
    # Draw circles at vertices
    vertices = [
        (40, 40), (300, 40), (560, 40),
        (120, 120), (300, 120), (480, 120),
        (200, 200), (300, 200), (400, 200),
        (40, 300), (120, 300), (200, 300),
        (400, 300), (480, 300), (560, 300),
        (200, 400), (300, 400), (400, 400),
        (120, 480), (300, 480), (480, 480),
        (40, 560), (300, 560), (560, 560)
    ]
    
    for vx, vy in vertices:
        canvas.create_oval(vx-20, vy-20, vx+20, vy+20, fill="black")

def main():
    root = tk.Tk()
    root.title("Mills Board Click Tracker")

    width, height = 600, 600

    canvas = tk.Canvas(root, width=width, height=height)
    canvas.pack()

    create_mills_board(canvas, width, height)
    canvas.bind("<Button-1>", on_click)

    root.mainloop()

if __name__ == "__main__":
    main()