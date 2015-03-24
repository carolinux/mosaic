import skimage.io as io
from skimage import transform as tf
from skimage.transform import resize 
import math
import numpy as np
import os
import copy
from matplotlib import pyplot as plt


# in place!
def checkerboard(img, parts):
    """Replace all image parts with black and white (just for fun)"""
    for i,part in enumerate(parts):
        pixels = part.get_all_pixels()
        for px in pixels:
            img[px] = (0,0,0) if i%2==0 else (255,255,255)


# in place!
def tile_one_part(img, parts):
    """Get a random part to tile all over the image"""
    #FIXME what happens if part is smaller? (idx=14) not robust now
    for i,part in enumerate(parts):
        pixels = part.get_all_pixels()
        origin = part.get_origin()
        for px in pixels:
            c = parts[16].get_color(*px, origin=origin)
            img[px]=c

def divide_into_parts(img, numXtiles, numYtiles):
    """Divide the image equally int X*Y parts"""
    width_x = int(math.ceil(img.shape[0]*1.0/numXtiles))
    width_y = int(math.ceil(img.shape[1]*1.0/numYtiles))
    parts = []
    for i in range(0,img.shape[0],width_x):
        for j in range(0,img.shape[1],width_y):
            parts.append(ImagePart.from_image(img,width_x, width_y, origin=(i,j)))
                    
    return parts

def assemble_from_parts(parts, border=False):
    """Assemble an image from image parts,
    optionally with a border around the tiles"""
    #TODO: border
    w = 1000 #sum([p.w for p in parts[0]])
    h = 1000 #sum([p.h for p in parts[0]]) #FIXME incorrect
    img = np.zeros((w,h,3))    
    for i,part in enumerate(parts):
        pixels = part.get_all_pixels()
        origin = part.get_origin()
        for px in pixels:
            c = part.get_color(*px, origin=origin)
            #import ipdb;ipdb.set_trace()
            img[px]=list(c)
    return img

def get_image_matrix(img):
   return img


class ImagePart(object):
    """A class that represents part of an image"""

    matrix = None # the np.arr of teh  pixels
    ll = None # lower left point - origin
    w = None
    h = None
    def __init__(self, matrix, ll):
        self.w =len(matrix)
        self.h=len(matrix[0])
        self.ll =ll
        self.matrix = matrix
        self.original_matrix = copy.deepcopy(matrix)

    def toImage(self):
        return self.matrix

    @staticmethod
    def from_whole_image(img):
        """Create an image part out of a whole image"""
        matrix = get_image_matrix(img)
        return ImagePart(matrix, (0,0))

    @staticmethod
    def from_image(img, w, h, origin=(0,0)):
        """Create an image part out of part of an image"""
        matrix = get_image_matrix(img)
        maxw = len(matrix)
        maxh = len(matrix[0])
        (i,j) = origin
        matrix_part = matrix[i:(i+w if i+w<maxw else maxw),j:(j+h if j+h<maxh else maxh)]

        return ImagePart(matrix_part, origin)

    def get_matrix(self):
         return self.matrix

    def set_origin(self, x,y):
        self.ll = (x,y)

    def get_origin(self):
        return self.ll

    def get_all_pixels(self):
        """Return all the  pixel coordinates (as x,y tuples) of the original image that this part covers"""
        return [(self.ll[0]+x,self.ll[1]+y) for (x,y,_),_ in np.ndenumerate(self.matrix)] # (x,y,_),_ wtf lawl

    def get_color(self,x,y, origin=None):
        if origin is None:
            origin = self.ll
        return tuple(self.matrix[x-origin[0]][y-origin[1]])

    def compareWithImage(self, image):
        """ See if an image matches the dominant colors etc of this particular part nicely"""
        # first resize image to fit:
        image = resize(image, (self.w,self.h),mode='nearest')
        #TODO :more
        return image

    def fillWithImage(self, image):
        self.matrix = copy.deepcopy(image)


def get_all_pictures_in_directory(directory_path,recursive=False, extensions=None):
    if extensions is None:
        extensions = [".jpg",".png"]
    picture_fns = []
    for filename in os.listdir(directory_path):
        full_path = os.path.join(directory_path,filename)
        if recursive and os.path.isdir(full_path):
            picture_fns+=get_all_pictures_in_directory(full_path, recursive=True, extensions=extensions)
        if not os.path.isdir(full_path):
            _,extension = os.path.splitext(full_path)
            if extension in extensions:
                picture_fns.append(full_path)
    return picture_fns

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

def comparisons(directory, main_pic):
    main_pic = io.imread(main_pic)
    #scale = tf.SimilarityTransform(scale=0.33)
    #main_pic = tf.warp(main_pic, scale)
    main_pic = resize(main_pic, (1000,1000),mode='nearest') 
    comps = get_all_pictures_in_directory(directory, recursive=True)
    print comps
    main_part = ImagePart.from_whole_image(main_pic)
    parts = divide_into_parts(main_pic, 10,10)
    new_pic = assemble_from_parts(parts)
    plt.imshow(new_pic)
    plt.show()
    pics = map(lambda x: io.imread(x), comps)

if __name__=="__main__":
    comparisons("/home/carolinux/Pictures","/home/carolinux/Documents/luigi.jpg")
