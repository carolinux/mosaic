import numpy as np
import math
import itertools
import os
import re

import skimage.io as io

from part import ImagePart

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
            #import ipdb; ipdb.set_trace()
            if ignore_regex is not None and re.match(ignore_regex, full_path):
                continue
            #print "{} doenst match ignore regext {}".format(full_path,ignore_regex)
            if extension in extensions:
                picture_fns.append(full_path)
    return picture_fns

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

def expand(parts, iteration=1, squares_only = False):
    """Expand parts to join with their neighbours if
    they are similar color"""
    for i in range(len(parts)):
        for j in range(len(parts[0])):
            part = parts[i][j] 
            if not part.active:
                continue
            part.expand(parts, i, j, iteration=iteration,squares_only=squares_only)

def assemble_from_parts(parts, border=False, text=False):
    """Assemble an image from image parts,
    optionally with a border around the tiles"""
    h = sum([p.h for p in parts[0] if p.active])
    w = sum([p.w for p in np.transpose(parts)[0] if p.active])
    #import ipdb;ipdb.set_trace()
    img = np.zeros((w,h,3), dtype=np.uint8)
    flat_parts = list(itertools.chain.from_iterable(parts)) # flatten the list of lists
    for i,part in enumerate(flat_parts):
        if not part.active:
            continue
        if text:
            part.addText()
        if border:
            part.addBorder()
        #print "Avg color for part {}:{}".format(part.number, part.get_average_color())
        pixels = part.get_all_pixels()
        origin = part.get_origin()
        for px in pixels:
            c = part.get_color(*px, origin=origin)
            #import ipdb;ipdb.set_trace()
            img[px]=list(c)
    return img

