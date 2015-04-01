import skimage.io as io
import sys
import graph_util as gu
from matplotlib import pyplot as plt
import numpy as np
from skimage import data, img_as_float,img_as_ubyte

# TODO : Find good average colors per image
# and show them (average color and color variance, maybe blurring)
colors = []
for fn in sys.argv[1:]:
    pic = img_as_float(io.imread(fn))
    #pic_lab = gu.to_cielab(pic)
    #pic2= gu.to_rgb(pic_lab)
    #l,a,b = gu.get_average_color(pic_lab)
    r,g,b = gu.get_average_color(pic)
    color = gu.create_color_img(r,g,b)
    colors.append([r,g,b])
    fig = gu.plot2(pic,color)
    #plt.show()

c1 = colors[0]
c2 = colors[1]
l1 = gu.rgb_color_to_lab(*c1,dtype=np.float64)
l2 = gu.rgb_color_to_lab(*c2,dtype=np.float64)
from skimage.color import deltaE_ciede2000 as deltalab

print "RGB distance (eucl) {}".format(gu.delta(c1,c2))
print "CIELAB distance (eucl) {}".format(gu.delta(l1,l2))
print "CIELAB distance (built-in, 2000 version of delta) {}".format(deltalab(l1,l2))
