
import matplotlib.pyplot as plt
from skimage import data, img_as_float,img_as_ubyte
import matplotlib.image as mpimg
import numpy as np
import math
import copy
from skimage.color import rgb2lab,lab2rgb, rgb2hsv, hsv2rgb
from skimage.color import deltaE_ciede2000 as deltalab

def delta(c1,c2):
    """euclidean distance of color1 tuple to color2 tuple
    If they are in CIELAB format, then this is a good measure
    for perception difference between colors"""
    # can also look at skimage.color.deltaE_cie76(lab1, lab2)
    return math.sqrt((c1[0]-c2[0])**2 + (c1[1]-c2[1])**2 + (c1[2]-c2[2])**2)

def rgb_colors_are_similar(c1, c2, threshold=10):
    lab1 = rgb_color_to_lab(*c1)
    lab2 = rgb_color_to_lab(*c2)
    d = deltalab(lab1,lab2)
    #print d
    return d<threshold

#TODO: Does it have a clear dominant color (standard dev? mode? hist)
def is_suitable_for_mosaic(pic):
    return True

#TODO: Blur first (maybe ignore outliers somehow?)
def get_average_color(pic):
    # may not be rgb, depending on color space of picture
    r = np.average(pic[:,:,0])
    g = np.average(pic[:,:,1])
    b = np.average(pic[:,:,2])
    return r,g,b

def hsv_color_to_rgb(l,a,b,dtype=np.uint8):
    res = hsv2rgb(np.array([[[l,a,b]]],dtype=dtype))
    return tuple(res.flatten())

def rgb_color_to_hsv(r,g,b,dtype=np.uint8):
    res = rgb2hsv(np.array([[[r,g,b]]],dtype=dtype))
    return tuple(res.flatten())
def lab_color_to_rgb(l,a,b,dtype=np.uint8):
    res = lab2rgb(np.array([[[l,a,b]]],dtype=dtype))
    return tuple(res.flatten())

def rgb_color_to_lab(r,g,b,dtype=np.uint8):
    res = rgb2lab(np.array([[[r,g,b]]],dtype=dtype))
    return tuple(res.flatten())

def to_rgb(img):
    res = lab2rgb(img)
    return res

def to_cielab(img):
    return rgb2lab(img_as_float(img))

def get_colors_as_int64(d):
    f = (d[:,:,0].astype(np.int64)<<16) + (d[:,:,1].astype(np.int64)<<8) + d[:,:,2]
    return f

def create_color_img(r,g,b,w=10,h=10, dtype=np.float64):
    d = np.ones((w,h,3),dtype=dtype)
    d[:,:,0] = r
    d[:,:,1] = g
    d[:,:,2] = b
    return d

def plot2(image1, image2, title1="Base", title2="Comparison"):
    fig = plt.figure()
    # this image
    a=fig.add_subplot(2,1,1)
    imgplot = plt.imshow(image1)
    a.set_title(title1)
    # the other image
    a=fig.add_subplot(2,1,2)
    imgplot = plt.imshow(image2)
    a.set_title(title2)
    return fig

def plot_infos(image):
    fig = plt.figure()
    # this image
    a=fig.add_subplot(3,3,1)
    imgplot = plt.imshow(image)
    a.set_title("picture")
    # the other image
    a=fig.add_subplot(3,3,2)
    hsv = rgb2hsv(copy.deepcopy(image))
    h,s,v = get_average_color(hsv)
    #import ipdb; ipdb.set_trace()
    color = create_color_img(*hsv_color_to_rgb(h,s,v,dtype=np.float64))
    imgplot = plt.imshow(color)
    a.set_title("color")
    a=fig.add_subplot(3,3,7)
    hueonly = copy.deepcopy(hsv) 
    hueonly[:,:,1] = 0.5
    hueonly[:,:,2] = 0.5
    a.set_title("hue only")
    plt.imshow(hsv2rgb(hueonly))
    a=fig.add_subplot(3,3,8)
    satonly = copy.deepcopy(hsv) 
    satonly[:,:,0] = 0.0
    satonly[:,:,2] = 0.5
    a.set_title("sat only")
    plt.imshow(hsv2rgb(satonly))
    a=fig.add_subplot(3,3,9)
    valonly = copy.deepcopy(hsv) 
    valonly[:,:,0] = 0.0
    valonly[:,:,1] = 0.0
    a.set_title("val only")
    plt.imshow(hsv2rgb(valonly))
    hsv = rgb2hsv(image)
    a = fig.add_subplot(3,3,3)
    #import ipdb; ipdb.set_trace()
    plt.hist(hsv[:,:,0].flatten(), bins=20)
    a.set_title("Hue")
    a = fig.add_subplot(3,3,4)
    plt.hist(hsv[:,:,1].flatten(), bins=20)
    a.set_title("Sat")
    a = fig.add_subplot(3,3,6)
    plt.hist(hsv[:,:,2].flatten(), bins=20)
    a.set_title("Val (brighntess)")
    return fig

def plot4(image1, image2, image3, image4, title1, title2, title3, title4):
    fig = plt.figure()
    # this image
    a=fig.add_subplot(2,2,1)
    imgplot = plt.imshow(image1)
    a.set_title(title1)
    # the other image
    a=fig.add_subplot(2,2,2)
    imgplot = plt.imshow(image2)
    a.set_title(title2)
    a=fig.add_subplot(2,2,3)
    imgplot = plt.imshow(image3)
    a.set_title(title3)
    # the other image
    a=fig.add_subplot(2,2,4)
    imgplot = plt.imshow(image4)
    a.set_title(title4)
    return fig
