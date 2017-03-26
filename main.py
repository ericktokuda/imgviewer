#!/usr/bin/env python3
""" Image viewer based on Tkinter and integrated to the database.
"""
##########################################################IMPORTS
import argparse
import os
import tkinter
import tkinter.messagebox
import tkinter.filedialog
import tkinter.font
import PIL
import PIL.Image
import PIL.ImageTk
import utils
import time
import logging
import random

##########################################################DEFINES
GNDTRUTHID = 2
DETECTIONID = 7

class MyApp(tkinter.Frame):
    def __init__(self, parent=None, initialdir=os.getcwd()):
        super().__init__()
        self.parent = parent
        self.curid = 0
        self.curdir = initialdir
        self.images = listfiles(initialdir)
        self.conn = utils.db_connect('config/db.json')
        self.parent.bind("<Key>", self.onkeypress)
        self.create_canvas()
        self.colors = ['black'] + loadcolorsfromfile('tkcolors.txt')
        self.update_canvas()
        self.parent.title(self.images[self.curid])
        #self.create_controls()
        self.pack(fill=tkinter.BOTH, expand=tkinter.YES)

    def create_canvas(self):
        frame = tkinter.Frame(self)
        self.canvas = tkinter.Canvas(frame, background='black')
        frame.pack(fill=tkinter.BOTH, expand=tkinter.YES)
        self.canvas.pack(fill=tkinter.BOTH, expand=tkinter.YES)

    def update_canvas(self):
        self.im = None
        self.canvas.delete("all")

        imagepath = self.images[self.curid]
        w = self.parent.winfo_width()
        h = self.parent.winfo_height()

        #canvasratio = w/(h-30)
        canvasratio = w/(h)
        pilim = PIL.Image.open(os.path.join(self.curdir, imagepath))
        imratio = pilim.size[0]/pilim.size[1]

        if imratio > canvasratio:
            factor = w/pilim.size[0]
        else:
            factor = (h)/pilim.size[1]

        self.imfactor = factor
        t0 = time.time()
        pilim = pilim.resize((int(pilim.size[0]*factor), int(pilim.size[1]*factor)))
        self.curimage = PIL.ImageTk.PhotoImage(pilim)

        posx = int(w/2)
        posy = int(h/2)

        self.im = self.canvas.create_image(posx, posy, image=self.curimage)
        t1 = time.time()
        logging.debug('{:.1f} seconds to display image.'.format(t1-t0))
        #self.canvas.create_text((posx, posy), text=imagepath)
        self.draw_detections()
        self.draw_gndtruths()
        self.update()

    def create_controls(self):
        frame = tkinter.Frame(self, pady=5)
        obutton = tkinter.Button(frame, text='Open folder', command=
                lambda: self.openfolder(0))
        pbutton = tkinter.Button(frame, text='Previous picture', command=
                lambda: self.change_image(-1))
        nbutton = tkinter.Button(frame, text='Next picture', command=
                lambda: self.change_image(+1))
        qbutton = tkinter.Button(frame, text='Quit', command=self.parent.quit)


        obutton.pack(side=tkinter.LEFT)
        pbutton.pack(side=tkinter.LEFT)
        nbutton.pack(side=tkinter.LEFT)
        qbutton.pack(side=tkinter.LEFT)
        frame.pack()

    def onkeypress(self, event):
        k = event.keysym

        if k == 'Left':
            self.change_image(-1)
        elif k == 'Right':
            self.change_image(1)
        elif k == 'O':
            self.openfolder()
        elif k == 'S':
            self.createsubtitledialog()

    def createsubtitledialog(self):
        logging.debug('here inside createsubtitledialog')
        top = tkinter.Toplevel()
        top.title('Colors subtitle')

        classesrows = db_getclasses(self.conn)

        for i in range(0, 20):
            can = tkinter.Canvas(top,width=10,height=10)
            can.grid(row=i+1, column=1)
            can.create_rectangle(0,0,10,10,fill=self.colors[i+1])
            myfont = tkinter.font.Font(family="Arial", size=24)
            msg = tkinter.Message(top, text=classesrows[i][1], font=myfont, aspect=500)
            msg.grid(row=i+1, column=2, sticky=tkinter.W)

    def change_image(self, delta):
        newid = self.curid + delta 
        self.curid = newid % len(self.images)
        #if self.curid < 0: self.curid = len(self.images) - 1
        #elif self.curid >= len(self.images): self.curid = 0
        self.update_canvas()
        self.parent.title(self.images[self.curid])

    def openfolder(self, event):
        self.curdir = tkinter.filedialog.askdirectory()
        logging.debug("Now I have to update to " + self.curdir)

    def draw_gndtruths(self):
        self.draw_bboxes(GNDTRUTHID, 'black', (2,4))

    def draw_detections(self):
        self.draw_bboxes(DETECTIONID)

    def draw_bboxes(self, methodid, color=None, dash=(2, 4)):
        t0 = time.time()
        imageid = os.path.splitext(self.images[self.curid])[0]
        bboxes = db_getbboxes(self.conn, imageid, methodid)

        t1 = time.time()
        logging.debug('{:.1f} seconds to fetch from DB.'.format(t1-t0))

        imcoords = self.canvas.coords(self.im)
        dx = imcoords[0] - int(self.curimage.width()/2)
        dy = imcoords[1] - int(self.curimage.height()/2)
        delta = [dx, dy, dx, dy]
        bboxline = imcoords[0]/100

        for b in bboxes:
            p = []
            for i in range(0,4):
                p.append(int(b[i]*self.imfactor) + delta[i])

            classid = b[5]
            logging.debug(classid)
            col = color if color else self.colors[classid]
            self.canvas.create_rectangle(p[0], p[1], p[2], p[3],
                    width=bboxline, outline=col, dash=dash)

def listfiles(indir, ext='jpg'):
    images = []
    files = os.listdir(indir)

    for f in files:
        _file = os.path.join(indir, f)
        if os.path.isdir(_file) or not _file.lower().endswith(ext):
            continue
        images.append(f)

    return images

def db_getbboxes(conn, imageid, methodid, classid=None):
    cur = conn.cursor()
    query = """SELECT x_min, y_min, x_max, y_max, prob, classid FROM Bbox """ \
            """ WHERE imageid={} AND methodid={} """. \
            format(imageid, methodid);
    if classid: query += """AND classid={}""".format(classid)

    cur.execute(query)
    conn.commit()
    rows = cur.fetchall()
    return rows

def db_getclasses(conn):
    cur = conn.cursor()
    query = """SELECT id,name FROM Class ORDER BY id""" \

    cur.execute(query)
    conn.commit()
    rows = cur.fetchall()
    return rows

def loadcolorsfromfile(filepath):
    random.seed(0)
    with open(filepath) as f:
        lines = f.read().splitlines()
    random.shuffle(lines)
    return lines
#########################################################

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--path', default=None)
    parser.add_argument('-v', '--verbose', action='store_true')
    args = parser.parse_args()
    return args

def main():
    args = parse_args()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.WARNING)
    indir = args.path if args.path else os.getcwd()
    root = tkinter.Tk()
    root.geometry('600x400')
    root.update()
    #root.geometry('1280x960')
    myapp = MyApp(root, indir)
    root.mainloop()

if __name__ == "__main__":
    main()

