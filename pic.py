from PIL import Image
import math
import numpy as np
import copy


def checkerboard(img, parts):
        """Replace all image parts with black and white (just for fun)"""
        pix = img.load()
        for i,part in enumerate(parts):
                pixels = part.get_all_pixels()
                for px in pixels:
                        pix[px] = (0,0,0) if i%2==0 else (255,255,255)

def tile_one_part(img, parts):
        """Get a random part to tile all over the image"""
        #FIXME what happens if part is smaller? (idx=14) not robust now
        pix = img.load()
        for i,part in enumerate(parts):
                pixels = part.get_all_pixels()
                origin = part.get_origin()

                for px in pixels:
                        c = parts[16].get_color(*px, origin=origin)
                        pix[px]=c


def get_image_matrix(img):
        """
        Retun a 2D array of the colors of every pixel
        img (PIL.Image): image
        """
        #im = Image.open(filename) #Can be many different formats.
        #img = img.resize((basewidth,hsize), PIL.Image.ANTIALIAS)
        pix = img.load()

        matrix = []

        for w in range(img.size[0]):
                matrix.append([])
                for h in range(img.size[1]):
                        matrix[w].append(pix[w,h])
        return np.array(matrix)


class ImagePart(object):
        """A class that represents part of an image"""

        matrix = None # the np.arr of teh pixels
        ll = None # lower left point - origin
        w = None
        y = None
        def __init__(self, matrix, ll):

                self.w =len(matrix)
                self.y=len(matrix[0])
                self.ll =ll
                self.matrix = matrix
                self.original_matrix = copy.deepcopy(matrix) 

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
                """Return all the pixel coordinates (as x,y tuples) of the original image that this part covers"""

                return [(self.ll[0]+x,self.ll[1]+y) for (x,y,_),_ in np.ndenumerate(self.matrix)] # (x,y,_),_ wtf lawl

        def get_color(self,x,y, origin=None):
                if origin is None:
                        origin = self.ll
                return tuple(self.matrix[x-origin[0]][y-origin[1]])

        def match_score(self, other_part):
                """ See if a picture matches the dominant colors etc of this particular part nicely"""
                #blur both and have diff thresholds for lightness and hue,sat? lightness may be importanter for contrast...?
                # maybe a tile should have a contrast score too
                pass
        def set_color(self,x,y):
                # set the matrix with colors to the colors of a new picture
                pass

        
        
filename="./kitteh.jpg"
im = Image.open(filename)
num_x=10
num_y=5



def get_parts(img, numXtiles, numYtiles):
        width_x = int(math.ceil(img.size[0]*1.0/numXtiles))
        width_y = int(math.ceil(img.size[1]*1.0/numYtiles))
        parts = []

        for i in range(0,img.size[0],width_x):
                for j in range(0,img.size[1],width_y):
                        parts.append(ImagePart.from_image(img,width_x, width_y, origin=(i,j)))
                        

        return parts


parts = get_parts(im, num_x, num_y)
checkerboard(im,parts)
#tile_one_part(im,parts)


im.show()
