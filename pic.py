from PIL import Image
import math
import numpy as np
import copy


class ImagePart(object):
	"""A class that represents part of a pickchur"""

	matrix = None # the np.arr of teh pixels
	ll = None # lower left point
	w = None
	y = None
	def __init__(self, matrix, ll):

		self.w =len(matrix)
		self.y=len(matrix[0])
		self.ll =ll
		self.matrix = matrix
		self.original_matrix = copy.deepcopy(matrix) 


	def get_all_pixels(self):
		"""Return all the pixels (as x,y tuples) of the original image that this part covers"""

		return [(self.ll[0]+x,self.ll[1]+y) for (x,y,_),_ in np.ndenumerate(self.matrix)] # (x,y,_),_ wtf lawl

	def get_color_original_pixels(self,x,y):
		return self.get_color(x,y,origin=self.ll)

	def get_color(self, x,y, origin=None):
		if origin is None:
			origin=(0,0)
		return tuple(self.matrix[x-origin[0]][y-origin[1]])


	def match_score():
		""" See if a picture matches the dominant colors etc of this particular part nicely"""
		#blur both and have diff thresholds for lightness and hue,sat? lightness may be importanter for contrast...?
		# maybe a tile should have a contrast score too
		pass
	def set_color_to_image(im):
		# set the matrix with colors to the colors of a new picture
		pass

	
	
filename="./kitteh.jpg"
im = Image.open(filename) #Can be many different formats.
#img = img.resize((basewidth,hsize), PIL.Image.ANTIALIAS)
pix = im.load()

num_x=5
num_y=5
width_x = int(math.ceil(im.size[0]*1.0/num_x))
width_y = int(math.ceil(im.size[1]*1.0/num_y))

width_x=30
width_y=20

matrix = []

for x in range(im.size[0]):
	matrix.append([])
	for y in range(im.size[1]):
		matrix[x].append(pix[x,y])
matrix = np.array(matrix)

# one part of the image is defined by
# bottom left, width_x,width_y,
# and a matrix with the pixuls
def get_parts(matrix,x,y,xsize,ysize):
	parts = []

	for i in range(0,xsize,x):
		for j in range(0,ysize,y):
			part = matrix[i:(i+x if i+x<xsize else xsize),j:(j+y if j+y<ysize else ysize)]
			parts.append(ImagePart(part,(i,j)))
			

	return parts


parts = get_parts(matrix,width_x,width_y,*im.size)

#checkurboard
#for i,part in enumerate(parts):
#	pixels = part.get_all_pixels()
#	for px in pixels:
#		pix[px] = (0,0,0) if i%2==0 else (255,255,255)

#creepy-tiling
for i,part in enumerate(parts):

	pixels = part.get_all_pixels()
	ll = part.ll
	for px in pixels:
		c = parts[46].get_color(*px, origin=ll)
		print c
		pix[px]=c



im.show()
