import skimage.io as io
from skimage import transform as tf
from skimage.transform import resize 
from matplotlib import pyplot as plt
from part import ImagePart
from util import *

def kitteh():      
    filename="./kitteh.jpg"
    im = io.imread(filename)
    num_x=10
    num_y=5
    parts = divide_into_parts(im, num_x, num_y)
    checkerboard(im,parts)
    #tile_one_part(im,parts)
    plt.imshow(im) 
    plt.show()

def read(fn):
    print fn
    return io.imread(fn)

def comparisons(directory, main_pic):
    main_pic = io.imread(main_pic)
    #scale = tf.SimilarityTransform(scale=0.33)
    #main_pic = tf.warp(main_pic, scale)
    main_pic = resize(main_pic, (1000,1000),mode='nearest') 
    comps = get_all_pictures_in_directory(directory, recursive=True)
    print comps
    main_part = ImagePart.from_whole_image(main_pic)
    parts = divide_into_parts(main_pic, 10,10)
#    new_pic = assemble_from_parts(parts, border=True)
#    plt.imshow(new_pic)
#    plt.show()
    pics = map(lambda x: read(x), comps[:3])
    part = parts[3][5] # just a random part
    for pic in pics:
        part.compareWithImage(pic, show=True)
    
if __name__=="__main__":
    comparisons("./pictures","/home/carolinux/Documents/luigi.jpg")
