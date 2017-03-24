from tkinter import *
from PIL import Image,ImageTk

canvas_width = 800
canvas_height = 600

master = Tk()

canvas = Canvas(master, 
           width=canvas_width, 
           height=canvas_height)
canvas.pack()

img = ImageTk.PhotoImage(Image.open('cat.jpg'))

canvas.create_image(20,20, anchor=NW, image=img)
canvas.create_line(0, 0, 200, 100, fill="red", width=5)

mainloop()
