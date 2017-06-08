import os
import sys

from util import create_index_from_pictures, get_all_pictures_in_directory_optimized


def build_from_directories(directory_list, tag):
    fns = []
    for directory in directory_list:
        fns += get_all_pictures_in_directory_optimized(directory, ignore_regex=".*info.*")
    pickle_file = os.path.join("trees", tag+".pickle")
    create_index_from_pictures(fns, pickle_file)
    
if __name__=="__main__":
    comma_separated_dirs = sys.argv[1]
    tag = sys.argv[2]
    build_from_directories(comma_separated_dirs.split(","), tag)
