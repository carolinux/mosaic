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
from skimage.color import deltaE_ciede2000 as deltalab

from part import ImagePart
from util import *
import graph_util as gu

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
            args.append((parts[lb:hb], tree, 0, 0))

        res = pool.map(process_parts,args)
        return np.concatenate(res)
    else:
        print "executing in one core"
        return process_parts((parts, tree, 0,0))

def process_parts(args):
    try:
        parts = args[0]
        avg = args[1]
        startx= args[2]
        starty = args[3]
        for i in range(len(parts)):
            print "processing row {}".format(i)
            for j in range(len(parts[0])):
                process_part(parts, avg, i+startx, j+starty)
        return parts
    except Exception,e:
        raise Exception(e)

def process_part(parts, tree, i, j):
    if not parts[i][j].active:
        return
    c = gu.get_average_color_lab(parts[i][j].matrix)
    for delta in(3,5,10,15):
        low = [c[0]-delta, c[1]-delta,c[2]-delta]
        high = [c[0]+delta, c[1]+delta, c[2]+delta]
        keys,fns = tree.range_query(low, high)
        #if keys is not None:
            #for k in keys:
                #print c,k
                #print "delta= {}".format(gu.delta(c,k))
        if fns is not None:
            fn = np.random.choice(fns)
            parts[i][j].fillWithImage(read(fn))
            return
            #print "found tile for part {},{}".format(i,j)
        else:
            #print "not found tile for part {},{}".format(i,j)
            continue

def comparisons(directories, main_pic, par=1):
    main_pic = io.imread(main_pic)
    main_pic = skimage.img_as_ubyte(main_pic)
    main_pic = resize(main_pic, (600,600),mode='nearest')
    comps = []
    for directory in directories.split(","):
        comps += get_all_pictures_in_directory(directory, recursive=True, ignore_regex=".*info.*")
    main_part = ImagePart.from_whole_image(main_pic)
    parts = divide_into_parts(main_pic, 150,150)
    merging_iterations = 4
    for i in range(merging_iterations):
        expand(parts, iteration=i+1, squares_only=True)
    tree = create_index_from_pictures(comps)
    parts = compare(tree, parts, parallelization=par)
    #new_pic = assemble_from_parts(parts, border=True, text=True)
    new_pic = assemble_from_parts(parts, border=False, text=False)
    plt.imshow(new_pic)
    plt.show()
    
    io.imsave("pic_{}.jpg".format(datetime.now().microsecond),new_pic)
    
if __name__=="__main__":
    parallelism=1
    if len(sys.argv)>3:
        parallelism = int(sys.argv[3])
    comparisons(sys.argv[2],sys.argv[1], parallelism)
