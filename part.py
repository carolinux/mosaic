import copy
import numpy as np
from skimage import color
from skimage import filter
from skimage import img_as_float
from skimage import img_as_int
from skimage.transform import resize 
from skimage import measure
import skimage.io as io
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

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

    def compareWithImage(self, image, show=False):
        """ See if an image matches the dominant colors etc of this particular part nicely"""
        # first resize image to fit:
        image = resize(image, (self.w,self.h),mode='nearest')
        this_image = self.toImage()
        image = img_as_int(image)
        image = filter.gaussian_filter(image, 3) # TODO to calculate a good blur value
        #image = filter.sobel(image)
        gray = image.sum(-1)
        contour = measure.find_contours(gray, 0.8)
        #import ipdb;ipdb.set_trace()
        # show side by side
        if show:
            fig = plt.figure()
            # this image
            a=fig.add_subplot(2,2,1)
            imgplot = plt.imshow(this_image)
            a.set_title('Base')
            plt.colorbar(ticks=[0.1,0.3,0.5,0.7], orientation ='horizontal')
            # the other image
            a=fig.add_subplot(2,2,2)
            imgplot = plt.imshow(image)
            imgplot.set_clim(0.0,0.7)
            a.set_title('Comparison')
            plt.colorbar(ticks=[0.1,0.3,0.5,0.7], orientation='horizontal')

            # the contour of the part
            a=fig.add_subplot(2,2,3)
            r, g, b = np.rollaxis(this_image, -1)
            plt.contourf(r, cmap=plt.cm.Reds)
            plt.contourf(g, cmap=plt.cm.Greens)
            plt.contourf(b, cmap=plt.cm.Blues)
            a.set_title("Contour base")

            # the contour of the image
            a=fig.add_subplot(2,2,4)
            r, g, b = np.rollaxis(image, -1)
            foo=plt.contourf(r, cmap=plt.cm.Reds)
            plt.contourf(g, cmap=plt.cm.Greens)
            plt.contourf(b, cmap=plt.cm.Blues)
            dat0 =foo.allsegs[0][0]
            plt.plot(dat0[:,0],dat0[:,1])
            a.set_title("Contour comparison")

            plt.show()
        return image

    def fillWithImage(self, image):
        self.matrix = copy.deepcopy(image)

    def addBorder(self): # TODO image as float? color (1,1,1) ?
        width = 1 # can change later
        color = (255,255,255)
        for x in range(width):
            for y in range(self.h):
                self.matrix[x][y] = color
                self.matrix[self.w-width][y] = color

        for y in range(width):
            for x in range(self.w):
                self.matrix[x][y] = color
                self.matrix[x][self.h-width] = color
