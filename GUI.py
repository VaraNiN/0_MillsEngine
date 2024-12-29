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
        (0, 0, 0): (40, 40),    (0, 1, 0): (300, 40),   (0, 2, 0): (560, 40),
        (1, 0, 0): (120, 120),  (1, 1, 0): (300, 120),  (1, 2, 0): (480, 120),
        (2, 0, 0): (200, 200),  (2, 1, 0): (300, 200),  (2, 2, 0): (400, 200),
        (0, 0, 1): (40, 300),   (1, 0, 1): (120, 300),  (2, 0, 1): (200, 300),
        (2, 2, 1): (400, 300),  (1, 2, 1): (480, 300),  (0, 2, 1): (560, 300),
        (2, 0, 2): (200, 400),  (2, 1, 2): (300, 400),  (2, 2, 2): (400, 400),
        (1, 0, 2): (120, 480),  (1, 1, 2): (300, 480),  (1, 2, 2): (480, 480),
        (0, 0, 2): (40, 560),   (0, 1, 2): (300, 560),  (0, 2, 2): (560, 560)
    }
    
    radius = 20
    for index, (vx, vy) in vertices.items():
        if (vx - radius <= x <= vx + radius) and (vy - radius <= y <= vy + radius):
            return index
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