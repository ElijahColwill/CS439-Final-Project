import preprocessing
import pandas as pd
import sys
import argparse


def main(cfile: str, vfile: str, date: str):
    data = preprocessing.process(cfile, vfile, date)
    print(data.head())
    print(data.shape)


# If module is not being imported (ran as main program).
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='CS 43900 Final Project')
    parser.add_argument('-c', action='store', required=True, dest='cfile')
    parser.add_argument('-v', action='store', required=True, dest='vfile')
    parser.add_argument('-d', action='store', required=True, dest='date')
    if len(sys.argv) == 7:
        namespace = parser.parse_args(sys.argv[1:])
        main(namespace.cfile, namespace.vfile, namespace.date)
    else:
        print('Usage: python main.py -c <community_file_path> -v <vaccine_file_path> -d <community_report_date>')
