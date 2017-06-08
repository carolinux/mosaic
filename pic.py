import argparse
import pickle
import os

import skimage.io as io
import random
import skimage
from datetime import datetime
from skimage import transform as tf
import sys
from skimage.transform import resize 
from matplotlib import pyplot as plt
from multiprocessing import Pool
import numpy as np

from util import *


def read(fn):
    #print fn
    return skimage.img_as_ubyte(io.imread(fn))

def compare(tree, parts, parallelization=1):
    if parallelization>1:
        print "executing in {} cores".format(parallelization)
        pool = Pool()
        args = []
        procs = parallelization 
        for i in range(procs):
            step = len(parts)/procs
            lb = i * step
            hb = (i+1) * step if i<procs-1 else len(parts)
            #print parts[lb:hb]
            args.append((parts[lb:hb], tree))

        res = pool.map(process_parts,args)
        return np.concatenate(res)
    else:
        print "executing in one core"
        return process_parts((parts, tree))


def find_nearest_active_vertical_neighbour_fn(part_to_fn, i, j):
    """ Finds the closet tile above the current i,j that is active
        and returns its filename
    """
    while(i>=1):
        i = i-1
        if (i, j) in part_to_fn:
            return part_to_fn[(i, j)]
    return None


def process_parts(args):
    try:
        parts = args[0]
        tree = args[1]

        part_to_fn = {}
        for i in range(len(parts)):
            #print "processing row {} out of {}".format(i,len(parts))
            previously_used_fn = None
            for j in range(len(parts[0])):
                fn = process_part(parts, tree, part_to_fn, i, j)
                if fn is not None and (fn == previously_used_fn or find_nearest_active_vertical_neighbour_fn(part_to_fn, i, j) == fn):
                    # try one more time with bigger delta for horizontal/vertical diversity
                    # print fn, previously_used_fn
                    fn = process_part(parts, tree, part_to_fn, i, j, deltas=(18,20,25))
                    # print 'gimp "{}" "{}"'.format(fn, previously_used_fn)
                if fn is not None:
                    previously_used_fn = fn
        cache = {}
        h = min([x.h for x in parts[len(parts)/2]])
        try:
            w = min([x.w for x in parts[len(parts[0])/2]])
        except:
            w = h
        for i,fn in enumerate(set(part_to_fn.values())):
            #print "reading file {} out of {}".format(i, len(set(part_to_fn.values())))
            #FIXME: 60 is a magic number, h, w may be badly computed
            cache[fn] = resize(read(fn), (60*h,60*w),mode='nearest')
        for i, (k,v) in enumerate(part_to_fn.iteritems()):
            if i%1000==0:
                print "loaded {} image parts from {}".format(i, len(parts)*len(parts[0]))
            parts[k[0]][k[1]].fillWithImage(cache[v])

        return parts

    except Exception,e:
        import traceback
        raise Exception("{}:{}, {}, {}".format(e, traceback.format_exc(), parts[0], len(parts[0])))

def process_part(parts, tree, part_to_fn, i,j, deltas=None):
    if not parts[i][j].active:
        return None
    c = parts[i][j].get_average_color()
    if deltas is None:
        startdelta = np.random.choice(np.array([3,5,7]))
        deltas = (startdelta,10,15)
    for delta in deltas:
        low = [c[0]-delta, c[1]-delta,c[2]-delta]
        high = [c[0]+delta, c[1]+delta, c[2]+delta]
        keys, fns = tree.range_query(low, high)
        #if keys is not None:
            #for k in keys:
                #print c,k
                #print "delta= {}".format(gu.delta(c,k))
        if fns is not None:
            fn = np.random.choice(fns)
            part_to_fn[(i,j)] = fn
            return fn
            #print "found tile for part {},{}".format(i,j)
        else:
            #print "not found tile for part {},{}".format(i,j)
            continue
    return None

def add_suffix(fn, suffix):
    b, ext = os.path.splitext(fn)
    return b + suffix + ext

def comparisons(main_fn, tree, tiles=150, target_width=2000, parallelism=1):

    print "start"
    main_pic = io.imread(main_fn)
    size = target_width * 1.0
    main_pic = skimage.img_as_ubyte(main_pic)
    y = int(len(main_pic[0])*(size/len(main_pic)))
    print "resizing to {}".format((size,y))
    main_pic = resize(main_pic, (size,y))
    print "resized"


    print "Dividing into parts"
    parts = divide_into_tiles(main_pic, (int(size/tiles),int(size/tiles)))
    print "Divided"
    merging_iterations = 4
    for i in range(merging_iterations):
        print "Merging iteration {}".format(i)
        expand(parts, iteration=i+1, squares_only=True)

    parts = compare(tree, parts, parallelization=parallelism)
    new_pic = assemble_from_parts(parts, border=False, text=False)

    out_fn = add_suffix(main_fn, "_mosaic_{}_tiles_{}_{}".format(target_width, tiles, datetime.now().microsecond))
    print out_fn
    io.imsave(out_fn, new_pic)
    
if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("pic")
    parser.add_argument("tree")
    parser.add_argument("-p", "--parallelism", type=int, default=1)
    parser.add_argument("-t", "--tiles", type=int, default=150)
    parser.add_argument("-w", "--width", type=int, default=2000)
    args = parser.parse_args()

    main_pic = args.pic
    tree_fn = args.tree
    parallelism= args.parallelism
    tiles = args.tiles
    target_width = args.width
    tree = pickle.load(open(tree_fn,'rb'))
    comparisons(main_pic, tree, tiles=tiles, target_width=target_width, parallelism=parallelism)
