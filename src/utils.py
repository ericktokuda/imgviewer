#!/usr/bin/env python3
"""Rename wrong names

"""

import os
import argparse
import cv2

def main():
    outdir = '/tmp/clahe'
    indir = '/home/frodo/temp/test115/'
    apply_clahe(indir, outdir)


def get_images_cameras_from_list(files):
    imgs = {}
    for f in files:
        if not f.endswith('.jpg'): continue
        cam1 = f.split('-')[0]

        if cam1 in imgs.keys():
            imgs[cam1].append(f)
        else:
            imgs[cam1] = [f]

    cams = set(imgs.keys())
    return imgs, cams

def save_imgs_from_paired(imgs, paired, outpath):
    fh = open(outpath, 'w')
    for cam, imgs in imgs.items():
        if cam not in paired: continue
        for img in imgs:
            fh.write(img + '\n')
    fh.close()

def get_cameras_intersection(dir1, dir2):
    files1 = sorted(os.listdir(dir1))
    imgs1, cams1 = get_images_cameras_from_list(files1)

    files2 = sorted(os.listdir(dir2))
    imgs2, cams2 = get_images_cameras_from_list(files2)
    paired = cams2.intersection(cams1)

    print(len(cams1))
    print(len(cams2))
    print(len(cams1.difference(cams2)))
    print(len(cams2.difference(cams1)))
    print(len(paired))
    
    outpath1 = '/tmp/sunny_from_paired.txt'
    outpath2 = '/tmp/rainy_from_paired.txt'
    save_imgs_from_paired(imgs1, paired, outpath1)
    save_imgs_from_paired(imgs2, paired, outpath2)

def get_cameras_intersection_old(dir1, dir2):
    cams1num = {}
    cams1 = set()

    for f in os.listdir(dir1):
        if not f.endswith('.jpg'): continue
        cam1 = f.split('-')[0]
        cams1.add(cam1)

        if cam1 in cams1num.keys():
            cams1num[cam1] += 1
        else:
            cams1num[cam1] = 0

    cams2num = {}
    cams2 = set()
    for f in os.listdir(dir2):
        if not f.endswith('.jpg'): continue
        cam2 = f.split('-')[0]
        cams2.add(cam2)

        if cam2 in cams2num.keys():
            cams2num[cam2] += 1
        else:
            cams2num[cam2] = 0

    paired = cams2.intersection(cams1)

    acc1 = 0
    for cam1 in paired:
        acc1 += cams1num[cam1]

    acc2 = 0
    for cam2 in paired:
        acc2 += cams2num[cam2]

    print('Cameras sunny:{}'.format(len(cams1)))
    print('Cameras rainy:{}'.format(len(cams2)))
    print('Cameras sunny - rainy:{}'.format(len(cams1.difference(cams2))))
    print('Cameras rainy - sunny:{}'.format(len(cams2.difference(cams1))))
    print('Cameras paired:{}'.format(len(cams2.intersection(cams1))))
    print('Num sunny images from paired cameras:{}'.format(acc1))
    print('Num rainy images from paired cameras:{}'.format(acc2))
    
    fh = open('/tmp/sunnypaired.txt', 'w')
    for f in sorted(os.listdir(dir1)):
        if not f.endswith('.jpg'): continue
        cam1 = f.split('-')[0]
        if cam1 in paired:
            fh.write(f + '\n')
    fh.close()

    fh = open('/tmp/rainypaired.txt', 'w')
    for f in sorted(os.listdir(dir2)):
        if not f.endswith('.jpg'): continue
        cam2 = f.split('-')[0]
        if cam2 in paired:
            fh.write(f + '\n')
    fh.close()
    #print(paired)

def renameall(imdir, commandsfilename='/tmp/renameall.sh'):

    fh = open(commandsfilename, 'w')
    for f in sorted(os.listdir(imdir)):
        print(f)
        if '-' in f:
            if int(f.split('-')[0]) < 20160101:
                continue
            else:
                input('Error on {}'.format(f))
        else:
            arr = f.split('_')
            if int(arr[0]) < 20160101:
                newf = arr[0] + '-' + '_'.join(arr[1:])
            else:
                newf = arr[1] + '-' + arr[0] + '_'.join(arr[2:])
            fh.write('mv {} {}\n'.format(f, newf))
    fh.close()

def apply_clahe(imgs, outdir, cliplimit=2.0):
    if os.path.isdir(imgs):
        indir = imgs
        for f in sorted(os.listdir(indir)):
            imgpath = os.path.join(indir, f)
            apply_clahe_single(imgpath, outdir, cliplimit=2.0)
    elif os.path.isfile(imgs):
        apply_clahe_single(imgs, outdir, cliplimit=2.0)

def apply_clahe_single(imgpath, outdir, cliplimit=2.0):
    gridsize = 8
    bgr = cv2.imread(imgpath)
    lab = cv2.cvtColor(bgr, cv2.COLOR_BGR2LAB)
    lab_planes = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=cliplimit, tileGridSize=(gridsize, gridsize))
    lab_planes[0] = clahe.apply(lab_planes[0])
    lab = cv2.merge(lab_planes)
    clahedimg = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)

    imgname = os.path.basename(imgpath)
    #img = cv2.imread(imgpath)
    #clahe = cv2.createCLAHE(clipLimit=cliplimit, tileGridSize=(8,8))
    #clahedimg = clahe.apply(img)

    outpath = os.path.join(outdir, imgname)
    cv2.imwrite(outpath, clahedimg)

if __name__ == "__main__":
    main()

