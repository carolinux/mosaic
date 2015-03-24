import copy
import numpy as np
from skimage.transform import resize 

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
        matrix = img
        return ImagePart(matrix, (0,0))

    @staticmethod
    def from_image(img, w, h, origin=(0,0)):
        """Create an image part out of part of an image"""
        matrix = img
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

    def addBorder(self):
        pass #TODO
