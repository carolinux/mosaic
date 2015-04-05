import PIL
from PIL import ImageFont
from PIL import Image
from PIL import ImageDraw
import numpy as np
import skimage

PATH="/usr/share/fonts/truetype/ttf-dejavu/DejaVuSans.ttf"

def drawTextOnImage(text, matrix, font_size=25):
    font = ImageFont.truetype(PATH,font_size)
    #if text=="0":
        #import ipdb;ipdb.set_trace()
    #matrix = clean255(matrix)
    #matrix = matrix.astype(int)
    matrix = skimage.img_as_ubyte(matrix)
    arr = np.asarray(matrix, np.uint8)
    img = PIL.Image.fromarray(arr)
    draw = ImageDraw.Draw(img)
    draw.text((0, 0),text,(0,0,0),font=font)
    new_matrix =  np.array(img)
    return new_matrix

