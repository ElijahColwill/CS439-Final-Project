import preprocessing
import pandas as pd
import sys
import argparse


def main(cfile: str, hfile: str):
    data = preprocessing.process(cfile, hfile)
    print(data.head())


# If module is not being imported (ran as main program).
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='CS 43900 Final Project')
    parser.add_argument('-c', action='store', required=True, dest='cfile')
    parser.add_argument('-v', action='store', required=True, dest='hfile')
    if len(sys.argv) == 5:
        namespace = parser.parse_args(sys.argv[1:])
        main(namespace.cfile, namespace.hfile)
    else:
        print('Usage: python main.py -c <community_file_path> -v <vaccine_file_path>')
