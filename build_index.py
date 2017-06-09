import argparse
import os


from util import create_index_from_pictures, get_all_pictures_in_directory_optimized


def build_from_directories(directory_list, tag, leaf_size):
    fns = []
    for directory in directory_list:
        fns += get_all_pictures_in_directory_optimized(directory, ignore_regex=".*info.*")
    pickle_file = os.path.join("trees", tag+".pickle")
    create_index_from_pictures(fns, pickle_file, leaf_size_hint=leaf_size)
    
if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("dirs", help="Comma separated list of directories of tiles to use")
    parser.add_argument("tag", help="A name for your color index. tag.pickle will be generated with the index object")
    parser.add_argument("-l", "--leaf-size", type=int, default=10)

    args = parser.parse_args()
    build_from_directories(args.dirs.split(","), args.tag, args.leaf_size)
