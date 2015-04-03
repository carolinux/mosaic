import numpy as np
import copy

class Node:

    def __init__(self, bounds, dimension, depth, left=None, right=None, median=None):
        self.bounds = bounds
        self.dimensions = len(bounds)
        self.dimension = dimension # the split dimension of this node
        self.left = left
        self.right = right
        self.depth = depth
        self.median= median
        # two parallel lists to keep the n-dimensional spatial keys
        # and the associated content
        self.keys = None
        self.content = None

    def next_dimension(self):
        return (self.dimension+1) % self.dimensions

    def hasContent(self):
        return self.keys is not None

    def isLeaf(self):
        return self.left is None and self.right is None

    def get_neighbours(self,key):
        if not self.hasContent() and self.isLeaf():
            return None, None
        if self.hasContent():
            return self.keys,self.content
        else:
            if key[self.dimension]<self.median:
                return self.left.get_neighbours(key)
            else:
                return self.right.get_neighbours(key)

    def insert(self, arr, max_depth):
        if len(arr) == 0:
            return
        if self.depth == max_depth: # just insert them there
            #TODO could also insert them here if they are very few!
            self.keys = arr[:,0:-1]
            self.content = arr[:,-1]
            return
        if self.left is None and self.right is None:
            # determine optimal split given teh input
            values = arr[:,self.dimension]
            self.median = np.median(np.random.choice(values)) # find the median of a random sample of the values for the split
            lbounds = copy.deepcopy(bounds)
            rbounds = copy.deepcopy(bounds)
            lbounds[self.dimension][1] = median 
            rbounds[self.dimension][0] = median 
            self.left = Node(lbounds,self.next_dimension(),self.depth+1,None,None)
            self.right = Node(rbounds,self.next_dimension(),self.depth+1,None,None)

        bool_idx = arr[:,self.dimension]<self.median
        self.left.insert(arr[bool_idx], max_depth)
        self.right.insert(arr[~bool_idx], max_depth)

class KDTree:
    
    def __init__(self, bounds, max_depth=10):
        """Bounds should be the limits across
        each dimension ie [[0,255],[0,255],[0,255]]
        defines an RGB colorspace (3D)"""

        self.bounds = bounds
        self.dim = len(bounds)
        self.max_depth = max_depth
        self.root = Node(bounds, 0, 1)

    #TODO check the types of the key and the arr to insert
    def get_neighbours(self, key):
        if key.shape[1]!=self.dim:
            raise Exception("Key dimension doesn't match")
        return self.root.get_neighbours(key)

    def bulk_insert(self, arr):
        if arr.shape[1] != self.dim+1: # must have same dimension plus one extra for content
            raise Exception("Cannot insert points of dimension {} in KD Tree with dimension {}".format(arr.shape[1], self.dim))
        self.root.insert(arr, self.max_depth)


        


