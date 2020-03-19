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
# import utils
import time
import logging
from logging import debug, info
import random
# import os
# import os.path
from os.path import join as pjoin

##########################################################DEFINES
GNDTRUTHID = 2
DETECTIONID = 7

class MyApp(tkinter.Frame):
    def __init__(self, parent, initialdir=os.getcwd(), annotdir='/tmp'):
        super().__init__()
        self.parent = parent
        self.curid = 0
        self.curdir = initialdir
        self.images = listfiles(initialdir)
        self.labels = set()
        self.labelschanged = False
        imgslist = []

        self.annotdir = annotdir
        self.parent.bind("<Key>", self.onkeypress)
        self.create_canvas()
        self.colors = ['black'] + loadcolorsfromfile('tkcolors.txt')
        self.update_canvas()
        self.parent.title(self.images[self.curid])
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
        debug('{:.1f} seconds to display image.'.format(t1-t0))

        imageid = os.path.splitext(self.images[self.curid])[0]
        imgname = self.images[self.curid]
        annotpath = pjoin(self.annotdir, imgname.replace('.jpg', '.txt'))
        text_ = ''

        if os.path.exists(annotpath):
            with open(annotpath) as fh:
                # text_ += ': ' + fh.read().strip()
                text_ = fh.read().strip()
                self.labels = set(filter(len, text_.split(',')))
        else:
            self.labels = set()

        self.canvas.create_text(600, 700, fill='black',
                                font="Times 80 bold", text=text_)
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

    def add_label(self, key):
        if key == 'minus': annotid = '-1'
        else: annotid = key
        # print(annotid, self.classes)

        if annotid in self.labels:
            info('Removing label {}'.format(annotid))
            self.labels.remove(annotid)
        else:
            self.labels.add(annotid)

    def save_annotation(self, imgid):
        if not self.labelschanged: return
        if len(self.labels) > 1 and '-1' in self.labels:
            self.labels.remove('-1')
        annotpath = pjoin(self.annotdir, imgid + '.txt')
        fh = open(annotpath, 'w')
        fh.write(','.join(sorted(self.labels)))
        fh.close()

    def onkeypress(self, event):
        k = event.keysym

        if k == 'Left':
            self.save_annotation(self.images[self.curid].replace('.jpg', ''))
            self.change_image(-1)
            self.labelschanged = False
        elif k == 'Right':
            self.save_annotation(self.images[self.curid].replace('.jpg', ''))
            self.change_image(1)
            self.labelschanged = False
        elif k == 'O':
            self.openfolder()
        elif k == 'S':
            self.createsubtitledialog()
        elif k == 'q':
            self.parent.destroy()
        elif k == '1' or k == '2' or k == '3' or k == 'minus':
            self.labelschanged = True
            self.add_label(k)

    def createsubtitledialog(self):
        debug('here inside createsubtitledialog')
        top = tkinter.Toplevel()
        top.title('Colors subtitle')

        # classesrows = db_getclasses(self.conn)

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
        info('Id:{}'.format(self.curid))

    def openfolder(self, event):
        self.curdir = tkinter.filedialog.askdirectory()
        debug("Now I have to update to " + self.curdir)

    def draw_gndtruths(self, bboxes):
        self.draw_bboxes(bboxes, GNDTRUTHID, 'black', 0.5, 1)

    def draw_detections(self, bboxes):
        self.draw_bboxes(bboxes, DETECTIONID)

    def draw_bboxes(self, bboxes, methodid, color=None, width=1.0, dash=(2, 10)):
        imcoords = self.canvas.coords(self.im)
        dx = imcoords[0] - int(self.curimage.width()/2)
        dy = imcoords[1] - int(self.curimage.height()/2)
        delta = [dx, dy, dx, dy]
        bboxline = imcoords[0]/100 * width

        for b in bboxes:
            p = []
            if b[6] != methodid: continue
            for i in range(0,4):
                p.append(int(b[i]*self.imfactor) + delta[i])

            classid = b[5]
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

def db_getbboxes(conn, imageid, classid=None):
    cur = conn.cursor()
    query = """SELECT x_min, y_min, x_max, y_max, prob, classid, methodid """ \
            """ FROM Bbox WHERE imageid={}""". \
            format(imageid);
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
    parser.add_argument('--imdir', required=True)
    parser.add_argument('--outdir', default='/tmp/')
    parser.add_argument('-v', '--verbose', action='store_true')
    args = parser.parse_args()
    return args

def main():
    args = parse_args()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)
    indir = args.imdir if args.imdir else os.getcwd()
    root = tkinter.Tk()
    root.geometry('1200x800')
    root.update()
    #root.geometry('1280x960')
    myapp = MyApp(root, indir, args.outdir)
    root.mainloop()

if __name__ == "__main__":
    main()

