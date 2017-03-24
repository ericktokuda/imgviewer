import tkinter
import tkinter.messagebox
import tkinter.filedialog
import PIL
import PIL.Image
import PIL.ImageTk

class MyApp(tkinter.Frame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent

        self.current = 0
        self.image_list = ['cat.jpg', 'dog.jpg']
        self.text_list = [ 'cat', 'dog']

        self.create_canvas()
        self.create_controls()
        self.pack()

    def create_canvas(self):
        self.canvas = tkinter.Canvas(self)
        self.imoncanvas = self.canvas.create_image(100,100)
        self.canvas.pack()

    def setimageoncanvas(self, imagepath):
        photo = PIL.ImageTk.PhotoImage(PIL.Image.open(imagepath))
        self.im = photo  # Avoid garbage collector (self.parent.im ?)
        self.canvas.itemconfig(self.imoncanvas, image=photo)

        self.canvas.create_line(0,0,100,100, width=5)

    def create_controls(self):
        obutton = tkinter.Button(self, text='Open folder', command=
                lambda: self.openfolder(0))
        pbutton = tkinter.Button(self, text='Previous picture', command=
                lambda: self.move(-1))
        nbutton = tkinter.Button(self, text='Next picture', command=
                lambda: self.move(+1))
        qbutton = tkinter.Button(self, text='Quit', command=self.parent.quit)

        self.parent.bind("<Left>", self.moveback)
        self.parent.bind("<Right>", self.movenext)
        self.parent.bind("<O>", self.openfolder)


        obutton.pack(side=tkinter.LEFT)
        pbutton.pack(side=tkinter.LEFT)
        nbutton.pack(side=tkinter.LEFT)
        qbutton.pack(side=tkinter.LEFT)

    def movenext(self, event):
        print("next")
        self.move(1)

    def moveback(self, event):
        print("back")
        self.move(-1)

    def move(self, delta):
        #if not (0 <= self.current + delta < len(self.image_list)):
            #tkinter.messagebox.showinfo('End', 'No more image.')
            #return

        imagepath = "dog.jpg" if delta == 1 else "cat.jpg"
        self.setimageoncanvas(imagepath)

    def openfolder(self, event):
        self.curdir = tkinter.filedialog.askdirectory()
        print("Now I have to update to " + self.curdir)

#########################################################
root = tkinter.Tk()
root.geometry('800x600')
myapp = MyApp(root)
root.mainloop()
