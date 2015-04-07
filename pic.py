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
#@profile
def process_parts(args):
    try:
        parts = args[0]
        tree = args[1]
        startx= args[2]
        starty = args[3]
        part_to_fn = {}
        for i in range(len(parts)):
            print "processing row {} out of {}".format(i,len(parts))
            for j in range(len(parts[0])):
                process_part(parts, tree, part_to_fn, i, j)
        cache = {}
        h = min([x.h for x in parts[len(parts)/2]])
        w = min([x.w for x in parts[len(parts[0])/2]])
        for i,fn in enumerate(set(part_to_fn.values())):
            print "reading file {} out of {}".format(i, len(set(part_to_fn.values())))
            #FIXME: 4 is a magic number, h, w may be badly computed
            cache[fn] = resize(read(fn), (60*h,60*w),mode='nearest')
        for i, (k,v) in enumerate(part_to_fn.iteritems()):
            if i%50==0:
                print "loaded {} image parts from {}".format(i, len(parts)*len(parts[0]))
            parts[k[0]][k[1]].fillWithImage(cache[v])

        return parts

    except Exception,e:
        raise Exception(e)

def process_part(parts, tree,part_to_fn, i,j ):
    if not parts[i][j].active:
        return
    c = parts[i][j].get_average_color()
    startdelta = np.random.choice(np.array([3,5,7]))
    for delta in(startdelta,10,15):
        low = [c[0]-delta, c[1]-delta,c[2]-delta]
        high = [c[0]+delta, c[1]+delta, c[2]+delta]
        keys,fns = tree.range_query(low, high)
        #if keys is not None:
            #for k in keys:
                #print c,k
                #print "delta= {}".format(gu.delta(c,k))
        if fns is not None:
            fn = np.random.choice(fns)
            part_to_fn[(i,j)] = fn
            break
            #print "found tile for part {},{}".format(i,j)
        else:
            #print "not found tile for part {},{}".format(i,j)
            continue


def comparisons(directories, main_pic, par=1):
    print "start"
    main_pic = io.imread(main_pic)
    size = float(2*len(main_pic[0]))
    main_pic = skimage.img_as_ubyte(main_pic)
    y = int(len(main_pic[0])*(size/len(main_pic)))
    print "resizing to {}".format((size,y))
    main_pic = resize(main_pic, (size,y))
    print "resized"
    comps = []
    if inp is not None:
        for directory in directories.split(","):
            comps += get_all_pictures_in_directory(directory, recursive=True, ignore_regex=".*info.*")
    main_part = ImagePart.from_whole_image(main_pic)
    print "Dividing into parts"
    parts = divide_into_tiles(main_pic, (int(size/150),int(size/150)))
    print "Divided"
    merging_iterations = 6
    for i in range(merging_iterations):
        print "Merging iteration {}".format(i)
        expand(parts, iteration=i+1, squares_only=True)
    print "Create index"
    tree = create_index_from_pictures(comps)
    print "Index created"
    parts = compare(tree, parts, parallelization=par)
    new_pic = assemble_from_parts(parts, border=False, text=False)
    #plt.imshow(new_pic)
    #plt.show()
    
    io.imsave("pic_{}.jpg".format(datetime.now().microsecond),new_pic)
    
if __name__=="__main__":
    parallelism=1
    if len(sys.argv)<2:
        inp =None
        pic ="/home/carolinux/Documents/luigi.jpg"
    else:
        inp = sys.argv[2]
        pic = sys.argv[1]
    if len(sys.argv)>3:
        parallelism = int(sys.argv[3])
    comparisons(inp,pic, parallelism)
