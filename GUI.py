import tkinter as tk

def on_click(event):
    x, y = event.x, event.y
    vicinity = get_vicinity(x, y)
    if vicinity:
        print(f"Clicked at: {vicinity}")

def get_vicinity(x, y):
    vertices = [
        (20, 20), (150, 20), (280, 20),
        (60, 60), (150, 60), (240, 60),
        (100, 100), (150, 100), (200, 100),
        (20, 150), (60, 150), (100, 150),
        (200, 150), (240, 150), (280, 150),
        (100, 200), (150, 200), (200, 200),
        (60, 240), (150, 240), (240, 240),
        (20, 280), (150, 280), (280, 280)
    ]
    
    radius = 10
    for i, (vx, vy) in enumerate(vertices):
        if (vx - radius <= x <= vx + radius) and (vy - radius <= y <= vy + radius):
            ring = i // 9
            pos_x = (i % 9) % 3
            pos_y = (i % 9) // 3
            return (ring, pos_x, pos_y)
    return None

def create_mills_board(canvas, width, height):
    # Outer square
    canvas.create_rectangle(20, 20, width-20, height-20)
    # Middle square
    canvas.create_rectangle(60, 60, width-60, height-60)
    # Inner square
    canvas.create_rectangle(100, 100, width-100, height-100)
    
    # Connecting lines
    canvas.create_line(width//2, 20, width//2, 100)
    canvas.create_line(width//2, height-20, width//2, height-100)
    canvas.create_line(20, height//2, 100, height//2)
    canvas.create_line(width-20, height//2, width-100, height//2)
    
    # Draw circles at vertices
    vertices = [
        (20, 20), (150, 20), (280, 20),
        (60, 60), (150, 60), (240, 60),
        (100, 100), (150, 100), (200, 100),
        (20, 150), (60, 150), (100, 150),
        (200, 150), (240, 150), (280, 150),
        (100, 200), (150, 200), (200, 200),
        (60, 240), (150, 240), (240, 240),
        (20, 280), (150, 280), (280, 280)
    ]
    
    for vx, vy in vertices:
        canvas.create_oval(vx-10, vy-10, vx+10, vy+10, fill="black")

def main():
    root = tk.Tk()
    root.title("Mills Board Click Tracker")

    width, height = 300, 300

    canvas = tk.Canvas(root, width=width, height=height)
    canvas.pack()

    create_mills_board(canvas, width, height)
    canvas.bind("<Button-1>", on_click)

    root.mainloop()

if __name__ == "__main__":
    main()