import skimage.io as io
import skimage
from skimage import transform as tf
from skimage.transform import resize 
from matplotlib import pyplot as plt
from part import ImagePart
from util import *

def read(fn):
    print fn
    return io.imread(fn)

def comparisons(directory, main_pic):
    main_pic = io.imread(main_pic)
    main_pic = skimage.img_as_ubyte(main_pic)
    #scale = tf.SimilarityTransform(scale=0.33)
    #main_pic = tf.warp(main_pic, scale)
    main_pic = resize(main_pic, (500,500),mode='nearest') 
    comps = get_all_pictures_in_directory(directory, recursive=True)
    print comps
    main_part = ImagePart.from_whole_image(main_pic)
    parts = divide_into_parts(main_pic, 50,50)
    new_pic = assemble_from_parts_luigi_test(parts, border=False, text=False)
    new_pic = new_pic.astype(np.uint8)
    #new_pic = assemble_from_parts(parts, border=True, text=False)
    plt.imshow(new_pic)
    plt.show()
    import ipdb;ipdb.set_trace()
    #pics = map(lambda x: read(x), comps[:3])
    #part = parts[3][5] # just a random part
    #for pic in pics:
        #part.compareWithImage(pic, show=True)
    
if __name__=="__main__":
    comparisons("./pictures","/home/carolinux/Documents/luigi.jpg")
