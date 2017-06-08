import copy
import numpy as np
from skimage import color
from skimage import filter
from skimage import img_as_ubyte
from skimage import img_as_ubyte
from skimage import img_as_uint
from skimage.transform import resize 
from skimage import measure
import skimage.io as io
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import graph_util as gu

class ImagePart(object):
    """A class that represents part of an image"""

    matrix = None # the np.arr of teh  pixels
    ll = None # lower left point - origin
    w = None
    h = None
    average = None
    number = 0 # the number of the part going right and then up from lower left
    type = np.uint8
    active = False # a part can become inactive if it is merged with another

    def __init__(self, matrix, ll, number):
        self.w =len(matrix)
        self.h=len(matrix[0])
        self.number = number
        self.ll =ll
        self.matrix = matrix
        self.active = True
        self.dtype = matrix.dtype
        assert(self.dtype==np.uint8)
        self.original_matrix = copy.deepcopy(matrix)

    def isActive(self):
        return self.active

    def toImage(self):
        return self.matrix

    @staticmethod
    def from_whole_image(img):
        """Create an image part out of a whole image"""
        #import ipdb;ipdb.set_trace()
        matrix = img_as_ubyte(img)
        return ImagePart(matrix, (0,0), 0)

    @staticmethod
    def from_image(img, w, h, origin=(0,0), number=0):
        """Create an image part out of part of an image"""
        matrix = img
        maxw = len(matrix)
        maxh = len(matrix[0])
        (i,j) = origin
        matrix_part = matrix[i:(i+w if i+w<maxw else maxw),j:(j+h if j+h<maxh else maxh)]

        matrix_part = img_as_ubyte(matrix_part)
        return ImagePart(matrix_part, origin, number)

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

    def get_average_color(self, fast=False):
        #if fast:
            #return gu.get_average_color_lab(self.matrix, True, fast=True)
        if self.average is None:
            self.average = gu.get_average_color_lab(self.matrix)
        return self.average

    def is_similar(self, other):
        """Parts are similar if they have same size
        and very similar colour"""
        try:
            if self.matrix.shape != other.matrix.shape:

                return False
            #import ipdb; ipdb.set_trace()
            res =  gu.colors_are_similar(self.get_average_color(fast=True), other.get_average_color(fast=True), threshold=5)
            return res
        except Exception,e:
            import ipdb; ipdb.set_trace()
            print e

    def expand(self, all_parts, i, j, iteration, squares_only):
        if squares_only:
            neighbours = [(i,j+iteration),(i+iteration,j),(i+iteration,j+iteration)]
            #if i==0 and j==0:
                #import ipdb; ipdb.set_trace()

            # check if the inbetween parts are inactive (for 2nd+ iteration merging)
            for w in range(i+1,i+iteration):
                for h in range(j+1,j+iteration):
                    if w<len(all_parts) and h<len(all_parts[0]):
                        if all_parts[w][h].active:
                            return

            for x,y in neighbours:
                try:
                    neighbour = all_parts[x][y]
                    if (not neighbour.active) or (not self.is_similar(neighbour)):
                        # cannot merge
                        return
                except:
                    return
            # I can combine the part with its neighbours
            # deactivate neighbours
            for x,y in neighbours:
                all_parts[x][y].active = False
            # combine neighbouring matrices
            new_matrix = np.zeros((2*self.w,2*self.h,3),dtype=np.uint8)
            new_matrix[0:self.w,0:self.h] = copy.deepcopy(self.matrix)
            new_matrix[self.w:2*self.w,self.h:2*self.h] = all_parts[i+iteration][j+iteration].matrix
            new_matrix[self.w:2*self.w,0:self.h] = all_parts[i+iteration][j].matrix
            new_matrix[0:self.w,self.h:2*self.h] = all_parts[i][j+iteration].matrix
            self.matrix = new_matrix
            self.h = 2* self.h
            self.w = 2* self.w
        # TODO: could also do non square tiling here
        pass

    #@profile
    def fillWithImage(self, image):
        if len(image) != self.h or len(image[0])!=self.w:
            image = resize(image, (self.w,self.h),mode='nearest')
        if image.dtype!=self.dtype:
            image = img_as_ubyte(image)
        self.matrix = copy.deepcopy(image)

    def fillWithColor(self, rgb):
        rgb = map(int,rgb)
        #import ipdb;ipdb.set_trace()
        self.matrix[:,:,0] = rgb[0]
        self.matrix[:,:,1] = rgb[1]
        self.matrix[:,:,2] = rgb[2]

    def addText(self):
        import text_util as txt
        self.matrix = txt.drawTextOnImage(str(self.number), copy.deepcopy(self.matrix))

    def addBorder(self, color): # TODO image as float? color (1,1,1) ?
        width = 1 # can change later
        for x in range(width):
            for y in range(self.h):
                self.matrix[x][y] = color
                self.matrix[self.w-width][y] = color

        for y in range(width):
            for x in range(self.w):
                self.matrix[x][y] = color
                self.matrix[x][self.h-width] = color
