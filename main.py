#!/usr/bin/env python3
import os
import tkinter
import tkinter.messagebox
import tkinter.filedialog
import PIL
import PIL.Image
import PIL.ImageTk
import utils

class MyApp(tkinter.Frame):
    def __init__(self, parent=None, initialdir=os.getcwd()):
        super().__init__()
        self.parent = parent

        self.curid = 0
        self.images = listfiles(initialdir)
        self.text_list = self.images
        self.curimage = {}

        self.create_canvas()

        self.create_controls()
        self.pack(fill=tkinter.BOTH, expand=tkinter.YES)

    def create_canvas(self):
        self.canvas = tkinter.Canvas(self)
        self.imlabel = tkinter.Label(self.canvas, text='Please choose a folder')
        self.imlabel.pack(fill=tkinter.BOTH, expand=tkinter.YES)
        self.canvas.create_line(0,0,100,100, fill='yellow', width=5)

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

        #self.canvas.create_line(0,0,500,100, fill='yellow', width=5)
        self.imlabel.config(text=text, fg='white', bg='black', image=im, compound=c)


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

        self.curid += 1
        if self.curid < 0: self.curid = len(self.images) - 1
        elif self.curid >= len(self.images): self.curid = 0

        self.setimageoncanvas(self.images[self.curid])

    def openfolder(self, event):
        self.curdir = tkinter.filedialog.askdirectory()
        print("Now I have to update to " + self.curdir)

def listfiles(indir, ext='jpg'):
    images = []
    files = os.listdir(indir)

    for f in files:
        _file = os.path.join(indir, f)
        if os.path.isdir(_file) or not _file.lower().endswith(ext):
            continue
        images.append(f)

    return images

def db_getbboxes(conn, imageid):

    cur = conn.cursor()
    query = """SELECT x_min, y_min, x_max, y_max, prob, classid FROM Bbox """ \
    """ WHERE imageid={} AND methodid=7""".format(imageid);
    cur.execute(query)
    conn.commit()
    rows = cur.fetchall()
    return rows

#########################################################
conn = utils.db_connect('config/db.json')
#db_getbboxes(conn, '124')
root = tkinter.Tk()
root.geometry('1280x960')
myapp = MyApp(root, )
root.mainloop()
