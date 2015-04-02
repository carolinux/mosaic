from skimage.color import rgb2lab,lab2rgb, rgb2hsv
import skimage.io as io
from skimage import img_as_ubyte
from collections import namedtuple, defaultdict
import numpy as np
import sys

import util

""" Check what the pictures in a directory look like with respect
to how suitable they are for using as mosaic tiles"""

Feature = namedtuple('Feature', 'std diff1 diff2 first2')
def getFeatures(fn):
    if isinstance(fn,str):
        pic = img_as_ubyte(io.imread(fn)) # uint8
    else:
        pic = fn
    hues = rgb2hsv(pic)[:,:,0]
    # std, mean, median
    std = np.std(hues)
    hist, bins = np.histogram(hues)
    hist = list(hist)
    shist = sorted(hist)
    diff_avg = abs(np.mean(hues)-np.median(hues))
    diff_hist = 1.0*(shist[-1] - shist[-2])/sum(hist)
    max_index = hist.index(shist[-1]) 
    second_max_index = hist.index(shist[-2]) 
    third_max_index = hist.index(shist[-3])
    total_count = sum(hist)
    first_two_colors_close = (abs(max_index - second_max_index) == 1) or shist[-2] <(0.1 * total_count)
    #if not first_two_colors_close:
    #    import ipdb; ipdb.set_trace()
    res = Feature(std, diff_avg, diff_hist, first_two_colors_close)
    return res

def isGood(feat):
    return feat.std<0.1 and feat.diff1<0.02 and feat.first2

if __name__ == '__main__':
    directory = sys.argv[1]
    fns = util.get_all_pictures_in_directory(directory, True)
    allc = 0
    counts = defaultdict(lambda: 0)
    allg = 0
    good = [] 
    for fn in fns:
        try:
            data = getFeatures(fn)
        except Exception, e:
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

    for x in ["first2","diff1","std"]:
        print "{} % have {}= good value".format(100.0*counts[x]/allc,x)
    print "All good for {}%".format(100.0*allg/allc)
    print "Good filenames: {}".format(good)

