from tkinter import *

win= Tk()

win.geometry("500x500")

def callback(e):
    x = e.x
    y = e.y
    print("Pointer is currently at %d, %d" %(x, y))
win.bind('<Motion>', callback)
win.mainloop()