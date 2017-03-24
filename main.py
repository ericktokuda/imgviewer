import tkinter
from tkinter import *
from tkinter import messagebox
from PIL import Image,ImageTk



image_list = ['cat.jpg', 'dog.jpg']
text_list = [ 'cat', 'dog']
current = 0




def movenext(event):
    move(1)

def moveback(event):
    move(-1)



def move(delta):
    global current, image_list
    if not (0 <= current + delta < len(image_list)):
        messagebox.showinfo('End', 'No more image.')
        return
    current += delta
    image = Image.open(image_list[current])
    photo = ImageTk.PhotoImage(image)
    label['text'] = text_list[current]
    label['image'] = photo
    label.photo = photo


canvas_width = 800
canvas_height = 600

master = Tk()
fram = Frame()
fram.pack()

canvas = Canvas(fram, width=canvas_width, height=canvas_height)
canvas.pack()

#img = ImageTk.PhotoImage(Image.open('cat.jpg'))

#canvas.create_image(20,20, anchor=NW, image=img)
#canvas.create_line(0, 0, 200, 100, fill="red", width=5)


label = tkinter.Label(fram, compound=tkinter.TOP)
label.pack()

tkinter.Button(canvas, text='Previous picture', command=lambda: move(-1)).pack(side=tkinter.LEFT)
tkinter.Button(canvas, text='Next picture', command=lambda: move(+1)).pack(side=tkinter.LEFT)
tkinter.Button(canvas, text='Quit', command=master.quit).pack(side=tkinter.LEFT)


#master.bind("<Button-1>", callback)
master.bind("<Right>", movenext)
master.bind("<Left>", moveback)


move(0)

mainloop()
