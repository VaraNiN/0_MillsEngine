import tkinter as tk

def on_click(event):
    x, y = event.x, event.y
    print(f"Clicked at: ({x}, {y})")

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