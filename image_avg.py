import skimage.io as io
import sys
import graph_util as gu
from matplotlib import pyplot as plt

# TODO : Find good average colors per image
# and show them


pic = io.imread(sys.argv[1])

fig = gu.plot2(pic,pic)
plt.show()
