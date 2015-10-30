import skimage.io as io
import random
import skimage
from datetime import datetime
from skimage import transform as tf
import sys
from skimage.transform import resize 
from matplotlib import pyplot as plt
import numpy as np
from skimage.color import deltaE_ciede2000 as deltalab

from util import *
import graph_util as gu


def main(main_pic, numx,numy, wh_ratio=None):
    print "start"
    main_pic = io.imread(main_pic)
    main_pic = skimage.img_as_ubyte(main_pic)
    h,w = main_pic.shape[:-1]
    print "width to height ratio:",w*1.0/h
    if wh_ratio is not None:
        neww = int( h * wh_ratio )
        main_pic = resize(main_pic, (h,neww))
        h,w = main_pic.shape[:-1]
        print "new width to height ratio:",w*1.0/h

    print "Dividing into parts"
    parts = divide_into_parts(main_pic, numx, numy )
    tiled = assemble_from_parts(parts, border=True)
    plt.imshow(tiled)
    plt.show()
    
if __name__=="__main__":
    pic = sys.argv[1]
    dims = map(int,sys.argv[2].split("x"))
    ratio = map(float, sys.argv[3].split(":")) if len(sys.argv)==4 else None

    if ratio is None:
        main(pic, *dims)
    else:
        main(pic, *dims, wh_ratio = ratio[1]*1.0/ratio[0])
