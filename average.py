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
Value = namedtuple('Value','val idx cnt')

def get_popular_values(arr, num=2):

    hist, bins = np.histogram(arr)
    #print hist,bins
    hist = list(hist)
    shist = sorted(hist)
    res = []
    for i in range(1,num+1):
        cnt = shist[-i]
        index = hist.index(shist[-i])
        res.append(Value(bins[index], index,cnt))
    return res

def getFeatures(fn):
    if isinstance(fn,str):
        pic = img_as_ubyte(io.imread(fn)) # uint8
    else:
        pic = fn
    hues = rgb2hsv(pic)[:,:,0]
    brightness = rgb2hsv(pic)[:,:,2] # Value in HSV
    # std, mean, median
    std = np.std(hues)
    diff_avg = abs(np.mean(hues)-np.median(hues))
    hue_vals = get_popular_values(hues, num=2)
    brightness_vals = get_popular_values(brightness, num=3)
    pixel_count = sum(np.histogram(hues)[0])
    first_two_colors_close = (abs(hue_vals[0].idx - hue_vals[1].idx) == 1) or hue_vals[1].cnt <(0.1 * pixel_count)
    good_contrast = True
    if std == 0.0: # no variance in hue means grayscale image
        good_contrast = abs(brightness_vals[0].idx - brightness_vals[1].idx) < 3 
    res = Feature(std, diff_avg,  first_two_colors_close, good_contrast)
    return res

def isGood(feat):
    return feat.std<0.1 and feat.diff1<0.02 and feat.first2 and feat.contrast

if __name__ == '__main__':
    directory = sys.argv[1]
    fns = util.get_all_pictures_in_directory(directory, True, ignore_regex=".*_info.*")
    allc = 0
    counts = defaultdict(lambda: 0)
    allg = 0
    good = [] 
    for fn in fns:
        try:
            data = getFeatures(fn)
        except Exception, e:
            print e
            continue
        print fn,data
        allc+=1
        if data.std<0.1:
            counts["std"]+=1
        if data.first2:
            counts["first2"]+=1
        if data.diff1<0.02:
            counts["diff1"]+=1
        if isGood(data):
            allg+=1
            good.append(fn)
        img = img_as_ubyte(io.imread(fn))
        newy = int(len(img[0])/(len(img)/250.0))
        img = resize(img, (250,newy), mode="nearest")
        io.imsave(fn, img)
        graph_util.plot_infos(img)
        _,ext = os.path.splitext(fn)
        info_fn = os.path.join(os.path.dirname(fn), re.sub(ext,"_info"+ext,os.path.basename(fn)))
        plt.savefig(info_fn)

    for x in ["first2","diff1","std"]:
        print "{} % have {}= good value".format(100.0*counts[x]/allc,x)
    print "All good for {}%".format(100.0*allg/allc)
    print "Good filenames: {}".format(good)

