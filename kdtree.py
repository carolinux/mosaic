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

    def boundsContain(self, low,high):
        for i in range(self.dimensions):
            if high[i]<self.bounds[i][0]:
                return False
            if low[i]>self.bounds[i][1]:
                return False
        return True


    def range_query(self, low, high):
        if self.isLeaf():
            if not self.hasContent():
                return None,None
            keys = []
            content = []
            for k,c in zip(self.keys, self.content):
                inRange = True
                for i in range(self.dimensions):
                    if k[i]<low[i] or k[i]>high[i]:
                        inRange = False
                        break
                if inRange:
                    keys.append(k)
                    content.append(c)
            if len(keys)==0:
                return None, None
            return keys, content
        else:
            resl=None,None
            resr=None,None
            if self.left.boundsContain(low,high):
                resl = self.left.range_query(low, high)
            if self.right.boundsContain(low,high):
                resr = self.right.range_query(low, high)
        if resl[0] is not None or resr[0] is not None:
            return np.concatenate(filter(lambda x: x is not None, [resl[0],resr[0]])),\
                    np.concatenate(filter(lambda x: x is not None,[resl[1],resr[1]])) ,
        else:
            return None,None

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

    def insertContent(self, arr):
        #import ipdb; ipdb.set_trace()
        self.keys = arr[:,0:-1]
        self.content = arr[:,-1]

    def insert(self, arr, max_leaf_size):
        if len(arr) == 0:
            return

        if len(arr) <= max_leaf_size: # just insert them there
            self.insertContent(arr)
            return

        if self.left is None and self.right is None:
            # determine optimal split given teh input
            #import ipdb; ipdb.set_trace()
            values = arr[:,self.dimension]
            #TODO: type problems here
            values = map(float,values)
            #TODO: random sample bigger than 1...
            self.median = np.median(np.random.choice(values, int(0.2 * len(values))))
            # find the median of a random sample of the values for the split
            #TODO: What happens if everyone has the same value? Then everybody goes to the right leaf, which is stupid
            lbounds = copy.deepcopy(self.bounds)
            rbounds = copy.deepcopy(self.bounds)
            lbounds[self.dimension][1] = self.median 
            rbounds[self.dimension][0] = self.median 
            self.left = Node(lbounds,self.next_dimension(),self.depth+1,None,None)
            self.right = Node(rbounds,self.next_dimension(),self.depth+1,None,None)

        bool_idx = arr[:,self.dimension].astype(np.float64)<self.median
        self.left.insert(arr[bool_idx], max_leaf_size)
        self.right.insert(arr[~bool_idx], max_leaf_size)

    def pprint(self):
        if self.left is None and self.right is None:
            return str(self.bounds)+" "+str(self.depth)
        return str(self.bounds)+" "+str(self.depth) +"\n"+ self.left.pprint() +"\n" + self.right.pprint()
         
class KDTree:
    
    def __init__(self, bounds, max_leaf_size=10):
        """Bounds should be the limits across
        each dimension ie [[0,255],[0,255],[0,255]]
        defines an RGB colorspace (3D)"""

        self.bounds = bounds # TODO Could also determine bounds from bulk_insert
        self.dim = len(bounds)
        self.max_leaf_size = max_leaf_size
        self.root = Node(bounds, 0, 1)

    def pprint(self):
        print self.root.pprint()

    def range_query(self, low, high):
        return self.root.range_query(low,high)

    #TODO check the types of the key and the arr to insert
    def get_neighbours(self, key):
        if len(key)!=self.dim:
            raise Exception("Key dimension doesn't match")
        return self.root.get_neighbours(key)

    def bulk_insert_dict_value_to_spatial(self, d):
        """We have a dictionary from value to spatial iterable.
        Convert into a numpy array of spatialx, spatialy, ..., value and insert"""
        #import ipdb; ipdb.set_trace()
        arr = np.empty((len(d),self.dim+1), dtype='object')
        for i,(k,v) in enumerate(d.iteritems()):
            for j in range(self.dim):
                arr[i][j] = v[j]
            arr[i][self.dim] = k

        self.bulk_insert(arr)


    def bulk_insert(self, arr):
        self.root.insert(arr, self.max_leaf_size)

