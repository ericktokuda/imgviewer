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
import time
import logging
import random

##########################################################DEFINES
WINSIZE = '800x600'

class MyApp(tkinter.Frame):
    def __init__(self, parent=None, imdir='', annotdir=''):
        super().__init__()
        self.parent = parent
        self.classes = []
        self.curid = 0
        self.images = listfiles(imdir)
        self.imdir = imdir
        self.annotdir = annotdir

        self.parent.bind("<Key>", self.onkeypress)
        self.create_canvas()
        self.colors = loadcolorsfromfile('tkcolors.txt') + ['black'] 
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

        canvasratio = w/(h)
        pilim = PIL.Image.open(os.path.join(self.imdir, imagepath))
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
        self.canvas.create_text((posx, posy), text=imagepath)

        imageid = os.path.splitext(self.images[self.curid])[0]
        bboxes = getbboxes_from_txt(imageid, self.annotdir)
        self.draw_detections(bboxes)
        #self.draw_gndtruths(bboxes)
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

        for i in range(len(self.classes)):
            can = tkinter.Canvas(top,width=10,height=10)
            can.grid(row=i+1, column=1)
            can.create_rectangle(0,0,10,10,fill=self.colors[i+1])
            myfont = tkinter.font.Font(family="Arial", size=12)
            msg = tkinter.Message(top, text=self.classes[i], font=myfont, aspect=500)
            msg.grid(row=i+1, column=2, sticky=tkinter.W)

    def change_image(self, delta):
        newid = self.curid + delta 
        self.curid = newid % len(self.images)
        self.update_canvas()
        self.parent.title(self.images[self.curid])

    def openfolder(self, event):
        self.curdir = tkinter.filedialog.askdirectory()
        logging.debug("Now I have to update to " + self.curdir)

    def draw_gndtruths(self, bboxes):
        self.draw_bboxes(bboxes, GNDTRUTHID, 'black', 0.5, 1)

    def draw_detections(self, bboxes):
        self.draw_bboxes(bboxes)

    def draw_bboxes(self, bboxes, color=None, width=1.0, dash=(2, 10)):
        imcoords = self.canvas.coords(self.im)
        dx = imcoords[0] - int(self.curimage.width()/2)
        dy = imcoords[1] - int(self.curimage.height()/2)
        delta = [dx, dy, dx, dy]
        bboxline = imcoords[0]/100 * width

        for b in bboxes:
            p = []
            for i in range(0, 4):
                p.append(int(b[i+2]*self.imfactor) + delta[i])

            col = self.get_class_color(b[0])
            self.canvas.create_rectangle(p[0], p[1], p[2], p[3],
                    width=bboxline, outline=col)

    def get_class_color(self, clsname):
        if clsname not in self.classes:
            self.classes.append(clsname)
        return self.colors[self.classes.index(clsname)]

def listfiles(indir, ext='jpg'):
    images = []
    files = os.listdir(indir)

    for f in files:
        _file = os.path.join(indir, f)
        if os.path.isdir(_file) or not _file.lower().endswith(ext):
            continue
        images.append(f)

    return images

def getbboxes_from_txt(imid, annotdir):
    annotpath = os.path.join(annotdir, imid + '.txt')
    fh = open(annotpath)

    bboxes = []
    for l in fh:
        arr = l.strip().split(' ')
        arr[1] = float(arr[1])
        arr[2] = int(arr[2])
        arr[3] = int(arr[3])
        arr[4] = int(arr[4])
        arr[5] = int(arr[5])
        bboxes.append(arr)
        #print(arr)
    fh.close()
    return  bboxes
    #annotpath = os.path.join(annotdir, imid + '.txt')

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
    parser.add_argument('--annotdir', required=True)
    parser.add_argument('-v', '--verbose', action='store_true')
    args = parser.parse_args()
    return args

def main():
    args = parse_args()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.WARNING)
    root = tkinter.Tk()
    root.geometry(WINSIZE)
    root.update()
    myapp = MyApp(root, args.imdir, args.annotdir)
    root.mainloop()

if __name__ == "__main__":
    main()

