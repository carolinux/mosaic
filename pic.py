import skimage.io as io
import random
import skimage
from skimage import transform as tf
from skimage.transform import resize 
from matplotlib import pyplot as plt
from part import ImagePart
from util import *
import graph_util as gu

def read(fn):
    print fn
    return skimage.img_as_ubyte(io.imread(fn))

def compare(fns, parts):
    avg = {}
    for fn in fns:
        img = read(fn)
        avg[fn] = gu.get_average_color(img)

    for i in range(len(parts)):
        for j in range(len(parts[0])):
            c = gu.get_average_color(parts[i][j].matrix)
            random.shuffle(fns)
            for fn in fns:
                if gu.rgb_colors_are_similar(c, avg[fn]):
                    parts[i][j].fillWithImage(read(fn))



def comparisons(directory, main_pic):
    main_pic = io.imread(main_pic)
    main_pic = skimage.img_as_ubyte(main_pic)
    main_pic = resize(main_pic, (500,500),mode='nearest') 
    comps = get_all_pictures_in_directory(directory, recursive=True)
    main_part = ImagePart.from_whole_image(main_pic)
    parts = divide_into_parts(main_pic, 20,20)
    
    compare(comps, parts)

    new_pic = assemble_from_parts(parts, border=False, text=False)
    plt.imshow(new_pic)
    plt.show()
    
if __name__=="__main__":
    comparisons("./pictures","/home/carolinux/Documents/luigi.jpg")
