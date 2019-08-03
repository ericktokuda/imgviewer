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
import xml.etree.ElementTree as ET

CLASSES = ['car', 'person', 'truck', 'bus',
           'motorcycle', 'bicycle']


def parse_dsv_annot(annotpath, withscore=False, delim=' '):
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

    return pd.read_csv(annotpath, names=classnames, sep=delim)


def parse_rec(filename):
    """ Parse a PASCAL VOC xml file """
    tree = ET.parse(filename)
    objects = []
    for obj in tree.findall('object'):
        obj_struct = {}
        obj_struct['name'] = obj.find('name').text
        obj_struct['pose'] = obj.find('pose').text
        obj_struct['truncated'] = int(obj.find('truncated').text)
        obj_struct['difficult'] = int(obj.find('difficult').text)
        bbox = obj.find('bndbox')
        obj_struct['bbox'] = [int(bbox.find('xmin').text),
                              int(bbox.find('ymin').text),
                              int(bbox.find('xmax').text),
                              int(bbox.find('ymax').text)]
        objects.append(obj_struct)

    return objects

def count_all_annotations(gnddir, minthresh=0.5,
                                 annot_ext='.txt'):
    classes = CLASSES
    mystr = 'filename'
    totalcount = {}
    for cls in classes:
        mystr += ',{}'.format(cls)
        totalcount[cls] = 0

    print(mystr)
    for xmlfile in os.listdir(gnddir):
        if not xmlfile.endswith('.xml'): continue
        gndannot = os.path.join(gnddir, xmlfile)
        boxes = parse_rec(gndannot)
        counter = dict.fromkeys(classes, 0)
        for box in boxes:
            cls = box['name']
            counter[cls] += 1

        mystr = '{}'.format(xmlfile.replace('.xml', '.jpg'))
        for cls in classes:
            mystr += ',{}'.format(counter[cls])
            totalcount[cls] += counter[cls]
        print(mystr)

    mystr = 'TOTALCOUNT'
    for cls in classes:
        mystr += ',{}'.format(totalcount[cls])
    print(mystr)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('gnddir', help='Ground-truth annotations directory')
    args = parser.parse_args()

    params = list(product([args.gnddir]))

    pool = Pool(1)
    pool.starmap(count_all_annotations, params)

if __name__ == "__main__":
    main()

