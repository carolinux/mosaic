from skimage.color import rgb2lab,lab2rgb, rgb2hsv
import skimage.io as io
from skimage import img_as_ubyte
from skimage.transform import resize
from collections import namedtuple, defaultdict
import numpy as np
import sys
import re
import os
from matplotlib import pyplot as plt


import util
import graph_util

""" Check what the pictures in a directory look like with respect
to how suitable they are for using as mosaic tiles"""

Feature = namedtuple('Feature', 'std diff1 first2 contrast')
Value = namedtuple('Value','val idx maxidx cnt')

def get_popular_values(arr, num=2):

    hist, bins = np.histogram(arr)
    #print hist,bins
    hist = list(hist)
    shist = sorted(hist)
    res = []
    for i in range(1,num+1):
        cnt = shist[-i]
        index = hist.index(shist[-i])
        res.append(Value(bins[index], index,len(hist)-1,cnt))
    return res

def crop_border(fn):
    from PIL import Image, ImageChops

    im = Image.open(fn)

    bg = Image.new(im.mode, im.size, im.getpixel((0,0)))
    diff = ImageChops.difference(im, bg)
    diff = ImageChops.add(diff, diff, 2.0, -100)
    bbox = diff.getbbox()
    if bbox:
        return im.crop(bbox)
    else:
        return im



def getFeatures(fn):
    if isinstance(fn,str):
        cropped_pillow_im = crop_border(fn)
        # converting between PIL images and skimage ubyte is easy!
        pic = img_as_ubyte(cropped_pillow_im) # uint8
    else:
        pic = fn
    if pic.shape[1] < 50:
        return None, None # too narrow
    hues = rgb2hsv(pic)[:,:,0]
    brightness = rgb2hsv(pic)[:,:,2] # Value in HSV
    # std, mean, median
    std = np.std(hues)
    diff_avg = abs(np.mean(hues)-np.median(hues))
    hue_vals = get_popular_values(hues, num=2)
    brightness_vals = get_popular_values(brightness, num=3)
    pixel_count = sum(np.histogram(hues)[0])
    first_two_colors_close = (abs(hue_vals[0].idx - hue_vals[1].idx) == 1) or (hue_vals[0].idx==0 and\
        hue_vals[1].idx==hue_vals[1].maxidx ) or (hue_vals[0].idx==hue_vals[0].maxidx and hue_vals[1].idx==0)\
        or (hue_vals[1].cnt <(0.1 * pixel_count))
    good_contrast = True
    if std == 0.0: # no variance in hue means grayscale image
        good_contrast = abs(brightness_vals[0].idx - brightness_vals[1].idx) < 3 
    res = Feature(std, diff_avg,  first_two_colors_close, good_contrast)

    if not isGood(res):
        return None, None

    newy = int(len(pic[0]) / (len(pic) / 250.0))
    pic = resize(pic, (250, newy), mode="nearest")
    return res, pic

def isGood(feat):
    return feat.std<0.1 and feat.diff1<0.02 and feat.first2 and feat.contrast

if __name__ == '__main__':
    directory = sys.argv[1]
    target_dir = os.path.join(directory, "good")
    if not os.path.exists(target_dir):
        os.mkdir(target_dir)

    fns = util.get_all_pictures_in_directory_optimized(directory)
    allc = 0
    counts = defaultdict(lambda: 0)
    allg = 0
    good = [] 
    for fn in fns:
        try:
            data, adjusted_pic = getFeatures(fn)
        except Exception, e:
            print e
            continue

        if not data:
            continue

        copy_fn = os.path.join(target_dir, os.path.basename(fn))
        io.imsave(copy_fn, adjusted_pic)

        # plot infos for reference
        graph_util.plot_infos(adjusted_pic)
        _,ext = os.path.splitext(fn)
        info_fn = os.path.join(target_dir, re.sub(ext,"_info"+ext,os.path.basename(fn)))
        plt.savefig(info_fn)
        plt.close('all')

