import tkinter as tk
from tkinter import ttk
import asyncio
import random as r
#import time as t

WINDOW_WIDTH = 500
WINDOW_HEIGHT = 500
mouse_x, mouse_y = 0, 0
programOn = True

def on_mouse_move(event):
    global mouse_x, mouse_y
    mouse_x = max(0, min(event.x, WINDOW_WIDTH))
    mouse_y = max(0, min(event.y, WINDOW_HEIGHT))       

async def main():
    global programOn

    root = tk.Tk()
    root.title("ESP32 Mouse Controller")
    root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
    AutoRunTF = tk.BooleanVar(value = False)

    def AutoRunOnOff():
        if AutoRunTF.get():
            print("Auto Mode Enabled")
        else:
            print("Manual Mode Enabled")

    def annihilation():
        global programOn
        nonlocal root
        programOn = False
        print("Terminating Program")
        root.destroy()
        exit()

    canvas = tk.Canvas(root, width=WINDOW_WIDTH, height=WINDOW_HEIGHT, bg="lightgray")
    canvas.pack()
    tk.Checkbutton(canvas, font = ("Times New Roman", 10), text = "Auto Mode", bd = 3, variable = AutoRunTF, command = AutoRunOnOff).place(relx = .5, rely = .5, anchor = 'center')
    tk.Button(root, font = ("Times New Roman", 12), text = "Exit", command = annihilation, fg = "red").place(relx = .5, anchor = 'n')
    positionLabel = tk.Label(canvas, font = ("Times New Roman", 8), text = "Move Mouse In Window", bg = "lightgray")
    positionLabel.place(anchor = 'nw')
    canvas.create_line(0, WINDOW_HEIGHT/2, WINDOW_WIDTH, WINDOW_HEIGHT/2, activewidth = 3)
    canvas.create_line(WINDOW_WIDTH/2, 0, WINDOW_WIDTH/2, WINDOW_HEIGHT, activewidth = 3)
    canvas.bind("<Motion>", on_mouse_move)
    
    root.update_idletasks()
    root.update()

    async def tk_loop():
        global programOn
        while programOn:
            try:
                root.update()
                positionLabel['text'] = f"X:{mouse_x}, Y:{WINDOW_HEIGHT - mouse_y}"
                await asyncio.sleep(0.01)
            except tk.TclError:
                break
    
    async def autoRunFunction():
        global mouse_x, mouse_y
        while programOn:
            if AutoRunTF.get():
                mouse_x = r.randint(0, WINDOW_WIDTH)
                mouse_y = r.randint(0, WINDOW_WIDTH)

            await asyncio.sleep(3)

    
    await asyncio.gather(tk_loop(), autoRunFunction())


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except asyncio.CancelledError:
        print("Program Exited")