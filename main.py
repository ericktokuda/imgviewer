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
        self.curimage = {}

        self.create_canvas()

        self.create_controls()
        self.pack(fill=tkinter.BOTH, expand=tkinter.YES)

    def create_canvas(self):
        self.canvas = tkinter.Canvas(self)
        self.imlabel = tkinter.Label(self.canvas, text='Please choose a folder')
        self.imlabel.pack(fill=tkinter.BOTH, expand=tkinter.YES)

        self.canvas.pack(fill=tkinter.BOTH, expand=tkinter.YES)

    def setimageoncanvas(self, imagepath):

        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()

        canvasratio = w/(h+0.00001)

        pilim = PIL.Image.open(imagepath)

        imratio = pilim.size[0]/pilim.size[1]

        if imratio > canvasratio:
            factor = w/pilim.size[0]
        else:
            factor = (h-30)/pilim.size[1]

        pilim = pilim.resize((int(pilim.size[0]*factor), int(pilim.size[1]*factor)))
        photo = PIL.ImageTk.PhotoImage(pilim)

        self.curimage['path'] = imagepath
        self.curimage['im'] = photo
        self.curimage['label'] = imagepath  # Avoid garbage collector (self.parent.im ?)

        text = self.curimage['label']
        im = self.curimage['im']
        c = tkinter.CENTER

        self.imlabel.config(text=text, fg='white', bg='black', image=im, compound=c)

        self.canvas.create_line(0,0,100,100, width=5)

    def create_controls(self):
        obutton = tkinter.Button(self, text='Open folder', command=
                lambda: self.openfolder(0))
        pbutton = tkinter.Button(self, text='Previous picture', command=
                lambda: self.move(-1))
        nbutton = tkinter.Button(self, text='Next picture', command=
                lambda: self.move(+1))
        qbutton = tkinter.Button(self, text='Quit', command=self.parent.quit)

        self.parent.bind("<Left>", lambda x: self.move(-1))
        self.parent.bind("<Right>", lambda x: self.move(1))
        self.parent.bind("<O>", self.openfolder)

        obutton.pack(side=tkinter.LEFT)
        pbutton.pack(side=tkinter.LEFT)
        nbutton.pack(side=tkinter.LEFT)
        qbutton.pack(side=tkinter.LEFT)

    def move(self, delta):
        if not (0 <= self.current + delta < len(self.image_list)):
            tkinter.messagebox.showinfo('End', 'Back to the first image.')

        imagepath = "dog.jpg" if delta == 1 else "cat.jpg"
        self.setimageoncanvas(imagepath)

    def openfolder(self, event):
        self.curdir = tkinter.filedialog.askdirectory()
        print("Now I have to update to " + self.curdir)

#########################################################
root = tkinter.Tk()
root.geometry('600x400')
#root.geometry('1280x960')
myapp = MyApp(root)
root.mainloop()
