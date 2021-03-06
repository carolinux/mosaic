import numpy as np
import math
import itertools
import os
import random
import re
import pickle

import scandir

import skimage.io as io
from skimage import img_as_ubyte

from part import ImagePart
from kdtree import KDTree
import graph_util as gu

def get_all_pictures_in_directory(directory_path,recursive=False, extensions=None, ignore_regex=None):
    if extensions is None:
        extensions = [".jpg",".png",".jpeg",".JPG",".JPEG"]
    picture_fns = []
    for filename in os.listdir(directory_path):
        full_path = os.path.join(directory_path,filename)
        if recursive and os.path.isdir(full_path):
            picture_fns+=get_all_pictures_in_directory(full_path, recursive=True, extensions=extensions,ignore_regex=ignore_regex)
        if not os.path.isdir(full_path):
            _,extension = os.path.splitext(full_path)
            if ignore_regex is not None and re.match(ignore_regex, full_path):
                continue
            #print "{} doenst match ignore regext {}".format(full_path,ignore_regex)
            if extension in extensions:
                picture_fns.append(full_path)
    return picture_fns

def get_all_pictures_in_directory_optimized(directory_path, ignore_regex=None):
    """ Works for large directory with just image files in it """
    picture_fns = []
    i = 0
    for fn_it in scandir.scandir(directory_path):
        full_path = os.path.abspath(fn_it.path)
        i+=1
        if i%200 == 0:
            print "Scanned {} images".format(i)
        if ignore_regex is not None and re.match(ignore_regex, full_path):
            continue
        if not os.path.isdir(full_path):
                picture_fns.append(full_path)
    return picture_fns

def create_index_from_pictures(fns, pickle_file, leaf_size_hint=5):
    if os.path.exists(pickle_file):
        print ("Index with tag already exists")
        index = pickle.load(open(pickle_file, 'rb'))
        return index
    avg={}
    for i,fn in enumerate(fns):
        if fn in avg.keys():
            continue
        if i%50 ==0:
            print "Calculated average of {} pictures out of {}".format(i, len(fns))
        try:
            img = img_as_ubyte(io.imread(fn))
            avg[fn] = gu.get_average_color_lab(img)
        except Exception,e:
            print "weird file {}: {} - skipped from index".format(fn,e)
            continue

    print "Building tree nao"
    bounds = [[0,100],[-128,128],[-128,128]] # TODO What iz bounds of lab color space?
    index = KDTree(bounds, leaf_size_hint)
    index.bulk_insert_dict_value_to_spatial(avg)
    pickle.dump(index, open(pickle_file, 'wb'))
    return index

# in place!
def checkerboard(img, parts):
    """Replace all image parts with black and white (just for fun)"""
    parts = list(itertools.chain.from_iterable(parts)) # flatten the list of lists
    for i,part in enumerate(parts):
        pixels = part.get_all_pixels()
        for px in pixels:
            img[px] = (0,0,0) if i%2==0 else (255,255,255)


# in place!
def tile_one_part(img, parts):
    """Get a random part to tile all over the image"""
    #FIXME what happens if part is smaller? (idx=14) not robust now
    parts = list(itertools.chain.from_iterable(parts)) # flatten the list of lists
    for i,part in enumerate(parts):
        pixels = part.get_all_pixels()
        origin = part.get_origin()
        for px in pixels:
            c = parts[16].get_color(*px, origin=origin)
            img[px]=c

def divide_into_tiles(img,tile=(10,10)):
    width_x, width_y = tile
    parts = []
    num = 0
    for i in range(0,img.shape[0],width_x):
        parts.append([])
        for j in range(0,img.shape[1],width_y):
            parts[-1].append(ImagePart.from_image(img,width_x, width_y, origin=(i,j), number=num))
            num+=1
    return parts

def divide_into_parts(img, numXtiles, numYtiles):
    """Divide the image equally int X*Y parts"""
    width_x = int(math.ceil(img.shape[0]*1.0/numXtiles))
    width_y = int(math.ceil(img.shape[1]*1.0/numYtiles))
    return divide_into_tiles(img,(width_x, width_y))

def expand(parts, iteration=1, squares_only = False, do_merging_factor=0.5):
    """Expand parts to join with their neighbours if
    they are similar color
    Args
        do_merging_factor: the higher the more likely that neighbouring tiles with same color will be merged
    """
    inactive = 0
    for i in range(len(parts)):
        if i%50==0:
            print "expanding row {}".format(i)
        for j in range(len(parts[0])):
            part = parts[i][j]
            if not part.active:
                inactive+=1
                continue
            # if >0.2, means that is is more likely the merging will be skipped
            if  random.random()> do_merging_factor: #stable thingey: 0.5
                continue

            part.expand(parts, i, j, iteration=iteration,squares_only=squares_only)
    print "Inactive parts {}".format(inactive)

def assemble_from_parts(parts, border=False, text=False, bordercolor=(0,0,0)):
    """Assemble an image from image parts,
    optionally with a border around the tiles"""
    h = sum([p.h for p in parts[0] if p.active])
    w = sum([p.w for p in np.transpose(parts)[0] if p.active])
    img = np.zeros((w,h,3), dtype=np.uint8)
    print "Assembling picture from parts"
    flat_parts = list(itertools.chain.from_iterable(parts)) # flatten the list of lists
    for i,part in enumerate(flat_parts):
        if not part.active:
            continue
        if text:
            part.addText()
        if border:
            part.addBorder(bordercolor)
        #print "Avg color for part {}:{}".format(part.number, part.get_average_color())
        origin = part.get_origin()
        try:
            img[origin[0]:origin[0]+part.w,origin[1]:origin[1]+part.h] = part.get_matrix()
        except Exception as e:
            import ipdb; ipdb.set_trace()
            print e
    return img

