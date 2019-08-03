#!/usr/bin/env python3
"""Draw bbboxes using TF-models api
"""

import cv2

import argparse
import os
from multiprocessing import Process, Pool, log_to_stderr
from itertools import product
import pandas as pd
import numpy as np

def parse_annot(annotpath, annotfmt, withscore=False):
    """Parse annotation file in the following format

    <class>,<score>,<left>,<top>,<right>,<bottom>

    where ',' can be replaced by input

    Args:
    annotpath(str) : annotation directory path
    delim(str) : Delimiter. default ','

    Returns:
    pandas.dataframe: dataframe containing the schema in the file
    """

    if annotfmt == 'yolo':
        return parse_annot_yolo(annotpath, withscore)
    return None

def parse_annot_yolo(annotpath, withscore=False):
    """Parse annotation file in the following format

    <class>,<score>,<left>,<top>,<right>,<bottom>

    where ',' can be replaced by input

    Args:
    annotpath(str) : annotation directory path
    delim(str) : Delimiter. default ','

    Returns:
    pandas.dataframe: dataframe containing the schema in the file
    """

    if withscore:
        classnames = ['cls', 'score', 'left', 'top', 'right', 'bottom']
    else:
        classnames = ['cls', 'left', 'top', 'right', 'bottom']

    annots = pd.read_csv(annotpath, names=classnames, sep=' ')
    if annots.isnull().values.any():
        print('##########################################################')
        print('Inconsistent format of {}. '.format(annotpath))
        print('##########################################################')
    return annots

def draw_boxes_and_texts(img, boxes, minthresh=0.5, color=(0, 255, 0), thickness=2):
    """Draw all boxes and text contained in the pd.dataframe @boxes
    (any kind of filtering is left to the caller)

    <class>,<score>,<left>,<top>,<right>,<bottom>
    or 
    <class>,        <left>,<top>,<right>,<bottom>

    where ',' can be replaced by input

    Args:
    img(np.array): image array
    boxes(pandas.dataframe): dataframe containg above fields
    minthresh(float): minimum detection score
    color((int, int, int)): color in rgb [0-255]
    thickness(float):line thickness

    Returns:
    pandas.dataframe: dataframe containing the schema in the file
    """

    if 'score' in boxes.columns: printscore = True
    else: printscore = False
    for _, box in boxes.iterrows():
        cv2.rectangle(img, (box.left, box.top), (box.right, box.bottom), color, thickness)
        boxtext = box.cls
        if printscore:
            boxtext += ':{:.2f}'.format(box.score)
        cv2.putText(img, boxtext, (box.left, box.top), cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, color, lineType=cv2.LINE_AA) 

def draw_all_annotations(imgpath, detdir, gnddir, outdir, annotfmt, minthresh=0.5):
    print(imgpath)
    outpath = os.path.join(outdir, os.path.basename(imgpath))
    filename = os.path.basename(imgpath)

    img = cv2.imread(imgpath)

    if annotfmt == 'yolo': annot_ext = '.txt'
    elif annotfmt == 'csv': annot_ext = '.csv'

    if detdir:
        detannot = os.path.join(detdir, filename.replace('.jpg', annot_ext))
        if os.path.exists(detannot):
            boxes = parse_annot(detannot, annotfmt, True)
            validboxes = boxes['score'] > minthresh
            draw_boxes_and_texts(img, boxes[validboxes])

    if gnddir:
        gndannot = os.path.join(gnddir, filename.replace('.jpg', annot_ext))
        if os.path.exists(gndannot):
            boxes = parse_annot(gndannot, annotfmt, False)
            draw_boxes_and_texts(img, boxes, color=(255, 0, 0))

    cv2.imwrite(outpath, img)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--imdir', required=True, help='Images directory')
    parser.add_argument('--detdir', required=False, help='Detection annotations directory')
    parser.add_argument('--gnddir', required=False, help='Ground-truth annotations directory')
    parser.add_argument('--outdir', required=True, help='Output directory')
    parser.add_argument('--annotfmt', required=True, help='Annotation format ["yolo"],"csv"')
    parser.add_argument('--parallel', action='store_true', help='Parallel execution')
    args = parser.parse_args()

    if not os.path.exists(args.outdir): os.mkdir(args.outdir)
    nproc = 4

    imgpaths = []
    for f in os.listdir(args.imdir):
        if not f.endswith('.jpg'): continue
        imgpaths.append(os.path.join(args.imdir, f))

    params = list(product(imgpaths, [args.detdir], [args.gnddir], [args.outdir],
                          [args.annotfmt]))

    if args.parallel:
        pool = Pool(nproc)
        pool.starmap(draw_all_annotations, params)
    else:
        [ draw_all_annotations(*p) for p in params ]

if __name__ == "__main__":
    main()

