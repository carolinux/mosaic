import skimage.io as io
import random
import skimage
from datetime import datetime
from skimage import transform as tf
import sys
from skimage.transform import resize 
from matplotlib import pyplot as plt
from multiprocessing import Pool

from part import ImagePart
from util import *
import graph_util as gu

def read(fn):
    #print fn
    return skimage.img_as_ubyte(io.imread(fn))

def compare(fns, parts, parallelization=1):
    avg = {}
    for fn in fns:
        img = read(fn)
        #print fn
        try:
            avg[fn] = gu.get_average_color(img)
        except:
            print "weird file {}".format(fn)
            continue

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
            args.append((parts[lb:hb], avg, 0, 0))

        res = pool.map(process_parts,args)
        return np.concatenate(res)
    else:
        print "executing in one core"
        return process_parts((parts, avg, 0,0))

def process_parts(args):
    try:
        parts = args[0]
        avg = args[1]
        startx= args[2]
        starty = args[3]
        for i in range(len(parts)):
            for j in range(len(parts[0])):
                process_part(parts, avg, i+startx, j+starty)
        return parts
    except Exception,e:
        raise Exception(e)

def process_part(parts, avg, i, j):
    fns = avg.keys()
    if not parts[i][j].active:
        return
    c = gu.get_average_color(parts[i][j].matrix)
    random.shuffle(fns)
    found=False
    for fn in fns:
        if found:
            break
        if gu.rgb_colors_are_similar(c, avg[fn]):
            parts[i][j].fillWithImage(read(fn))
            found=True


def comparisons(directory, main_pic, par=1):
    main_pic = io.imread(main_pic)
    main_pic = skimage.img_as_ubyte(main_pic)
    main_pic = resize(main_pic, (600,600),mode='nearest') 
    comps = get_all_pictures_in_directory(directory, recursive=True)
    main_part = ImagePart.from_whole_image(main_pic)
    parts = divide_into_parts(main_pic, 80,80)
    merging_iterations = 3
    for i in range(merging_iterations):
        expand(parts, iteration=i+1, squares_only=True)
    parts = compare(comps, parts, parallelization=par)
    new_pic = assemble_from_parts(parts, border=False, text=False)
    #plt.imshow(new_pic)
    #plt.show()i
    
    io.imsave("pic_{}.jpg".format(datetime.now().microsecond),new_pic)
    
if __name__=="__main__":
    comparisons(sys.argv[1],"/home/carolinux/Documents/luigi.jpg", int(sys.argv[2]))
