import PIL
from PIL import ImageFont
from PIL import Image
from PIL import ImageDraw
import numpy as np
import skimage

PATH="/usr/share/fonts/truetype/ttf-dejavu/DejaVuSans.ttf"

def clean255(matrix):
    for j in range(len(matrix[0])):
        for i in range(len(matrix)):
            for k in range(3):
                if matrix[i][j][k]>1.0:
                    matrix[i][j][k]=1.0
    return matrix

def invert(matrix):
    for j in range(len(matrix[0])):

        for i in range(len(matrix)):
            for k in range(3):
                matrix[i][j][k]=1-matrix[i][j][k]
    return matrix

"""Converting from PIL to the weird "float until 255" thing
is very cumbersome. Probably there is a bug.."""
def drawTextOnImage(text, matrix, font_size=25):
    font = ImageFont.truetype(PATH,font_size)
    #if text=="0":
        #import ipdb;ipdb.set_trace()
    matrix = clean255(matrix)
    #matrix = matrix.astype(int)
    matrix = skimage.img_as_ubyte(matrix)
    arr = np.asarray(matrix, np.uint8)
    img = PIL.Image.fromarray(arr)
    draw = ImageDraw.Draw(img)
    draw.text((0, 0),text,(0,0,0),font=font)
    new_matrix =  np.array(img)
    return invert(new_matrix)
    #import ipdb;ipdb.set_trace()
    for j in range(len(new_matrix[0])/2):
        for i in range(len(new_matrix/2)):
            if (matrix[i][j]==new_matrix[i][j]).all():
                continue
            #if text=="6":
                #import ipdb;ipdb.set_trace()
            matrix[i][j] =new_matrix[i][j]
    return matrix
