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
        self.curdir = initialdir
        self.images = listfiles(initialdir)

        self.create_canvas()
        self.update_canvas()
        self.create_controls()
        self.pack(fill=tkinter.BOTH, expand=tkinter.YES)

    def create_canvas(self):
        frame = tkinter.Frame(self)
        self.canvas = tkinter.Canvas(frame)
        frame.pack(fill=tkinter.BOTH, expand=tkinter.YES)
        self.canvas.pack(fill=tkinter.BOTH, expand=tkinter.YES)

    def update_canvas(self):
        self.im = None
        self.canvas.delete("all")

        imagepath = self.images[self.curid]
        w = self.parent.winfo_width()
        h = self.parent.winfo_height()
        print(w,h)

        canvasratio = w/(h-30)
        pilim = PIL.Image.open(os.path.join(self.curdir, imagepath))
        imratio = pilim.size[0]/pilim.size[1]

        if imratio > canvasratio:
            factor = w/pilim.size[0]
        else:
            factor = (h)/pilim.size[1]

        self.imfactor = factor
        pilim = pilim.resize((int(pilim.size[0]*factor), int(pilim.size[1]*factor)))
        self.curimage = PIL.ImageTk.PhotoImage(pilim)

        posx = int(w/2)
        posy = int(h/2)

        self.im = self.canvas.create_image(posx, posy, image=self.curimage)
        imagerect = self.canvas.bbox(self.im)
        #self.canvas.create_line(imagerect[0],imagerect[1], 100,100, fill='yellow', width=5)
        self.draw_bboxes()
        self.update()

    def create_controls(self):
        frame = tkinter.Frame(self, pady=5)
        obutton = tkinter.Button(frame, text='Open folder', command=
                lambda: self.openfolder(0))
        pbutton = tkinter.Button(frame, text='Previous picture', command=
                lambda: self.move(-1))
        nbutton = tkinter.Button(frame, text='Next picture', command=
                lambda: self.move(+1))
        qbutton = tkinter.Button(frame, text='Quit', command=self.parent.quit)

        self.parent.bind("<Left>", lambda x: self.move(-1))
        self.parent.bind("<Right>", lambda x: self.move(1))
        self.parent.bind("<O>", self.openfolder)

        obutton.pack(side=tkinter.LEFT)
        pbutton.pack(side=tkinter.LEFT)
        nbutton.pack(side=tkinter.LEFT)
        qbutton.pack(side=tkinter.LEFT)
        frame.pack()

    def move(self, delta):
        self.curid += 1
        if self.curid < 0: self.curid = len(self.images) - 1
        elif self.curid >= len(self.images): self.curid = 0

        self.update_canvas()

    def openfolder(self, event):
        self.curdir = tkinter.filedialog.askdirectory()
        print("Now I have to update to " + self.curdir)

    def draw_bboxes(self):
        imageid = os.path.splitext(self.images[self.curid])[0]
        print(imageid)
        bboxes = db_getbboxes(conn, imageid)
        print(bboxes)
        for b in bboxes:
            a = []
            for i in range(0,4): a.append(int(b[i]*self.imfactor))
            self.canvas.create_rectangle(a[0], a[1], a[2], a[3], width=5)


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
initialdir = '/home/dufresne/temp/carmera_images/fff/'
conn = utils.db_connect('config/db.json')
root = tkinter.Tk()
root.geometry('600x400')
root.update()
#root.geometry('1280x960')
myapp = MyApp(root, initialdir)
root.mainloop()
