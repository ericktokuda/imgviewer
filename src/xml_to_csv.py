#!/usr/bin/env python3
"""Convert pascal xml format to delimiter space values
"""

import argparse


import os
import glob
import pandas as pd
import xml.etree.ElementTree as ET


def xml_to_csv(inxml, outcsv):
    tree = ET.parse(inxml)
    root = tree.getroot()
    xml_list = []
    for member in root.findall('object'):
        value = (member[0].text,
                 int(member[4][0].text),
                 int(member[4][1].text),
                 int(member[4][2].text),
                 int(member[4][3].text)
                 )
        xml_list.append(value)
    column_name = ['class', 'xmin', 'ymin', 'xmax', 'ymax']
    xml_df = pd.DataFrame(xml_list, columns=column_name)
    xml_df.to_csv(outcsv, index=None, header=False, sep=' ')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--indir', required=True, help='XML directory')
    parser.add_argument('--outdir', required=True, help='Output directory')
    args = parser.parse_args()

    xmldir = args.indir
    csvdir = args.outdir

    for f in os.listdir(xmldir):
        if not f.endswith('.xml'): continue
        name, _ = os.path.splitext(f)
        xmlpath = os.path.join(xmldir, f)
        csvpath = os.path.join(csvdir, name + '.csv')
        xml_to_csv(xmlpath, csvpath)
    print('Successfully converted xml to csv.')

if __name__ == "__main__":
    main()
