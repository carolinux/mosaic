import sys
from StringIO import StringIO
import requests
import urllib3
import json
from matplotlib import pyplot as plt
import skimage.io as io
from PIL import Image
import numpy as np
import shutil
import os
from datetime import datetime

import average as avg
import graph_util as gu

def getUrl(deserialized_output, idx):
    return deserialized_output['responseData']['results'][idx]['unescapedUrl']

def readGoogleImage(deserialized_output,idx, http):
    #file = cStringIO.StringIO(http.urlopen('GET', imageUrl).read())
    #import ipdb; ipdb.set_trace()
    imageUrl = getUrl(deserialized_output, idx)
    response = requests.get(imageUrl, timeout=3)
    print imageUrl
    img = Image.open(StringIO(response.content))
    return PILtoMatrix(img)

def PILtoMatrix(pic):
    return np.array(pic.getdata(), dtype=np.uint8).reshape(pic.size[1], pic.size[0], 3)

def get_all_keywords(fn):
    if os.path.exists(fn):
        words =open(fn,"r").read().replace("\n"," ").split(" ")
        words = filter(lambda x : x.strip()!='',words)
        return list(set(words))
    else:
        print "No file {} found. Will try to use input as comma separated input".format(fn)
        return list(set(fn.split(",")))

def main(args):
    http = urllib3.PoolManager()
    pics = 0
    searchTerms = get_all_keywords(args[1])
    print searchTerms
    base = args[2]
    for searchTerm in searchTerms:
        out = os.path.join(base,searchTerm)
        os.makedirs(out)
        for startIndex in xrange(1,100,4):
            try: 
                searchUrl = "http://ajax.googleapis.com/ajax/services/search/images?v=1.0&q=" + searchTerm + "&start=" + str(startIndex)

                f = requests.get(searchUrl, timeout=5)
                deserialized_output = json.loads(f.content)
                try:
                    for i in range(4):
                        img = readGoogleImage(deserialized_output,i, http)
                        newy = int(len(img[0])/(len(img)/250.0))
                        img = resize(img, (250,newy), mode="nearest")
                        feat = avg.getFeatures(img)
                        if avg.isGood(feat):
                            print feat
                            pics+=1
                            io.imsave(os.path.join(out,"pic{}.jpg".format(pics)), img)
                            print "found a good picture(pic{}.jpg) for tiling {}".format(pics,datetime.now())
                            fig = gu.plot_infos(img)

                            plt.savefig(os.path.join(out,"pic{}_infos.jpg".format(pics)))
                        #plt.imshow(img)
                        #plt.show()
                except Exception,e:
                    print "Could not read {}. Cause {}".format(getUrl(deserialized_output, i), str(e))
            except Exception,e:
                print "could not read {}th page from google, {}, {}".format(startIndex, str(e), datetime.now())
                pass


if __name__ == '__main__':
    main(sys.argv)
