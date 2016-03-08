from __future__ import print_function
import sys
import pdb
import argparse
import logging
import os
import subprocess
import urllib2

TOKENIZER_PREFIXES = 'https://raw.githubusercontent.com/moses-smt/' +\
                     'mosesdecoder/master/scripts/share/nonbreaking_' +\
                     'prefixes/nonbreaking_prefix.'
TOKENIZER_URL = 'https://raw.githubusercontent.com/moses-smt/mosesdecoder/' +\
                'master/scripts/tokenizer/tokenizer.perl'

# Get the arguments
parser = argparse.ArgumentParser()
parser.add_argument(
    "--source",  default=None, help="Source data to tokenize")
parser.add_argument(
    "--target",  default=None, help="Target file to save tokenized data")
args = parser.parse_args()

def download_and_write_file(url, file_name):
    if not os.path.exists(file_name):
        path = os.path.dirname(file_name)
        if not os.path.exists(path):
            os.makedirs(path)
        u = urllib2.urlopen(url)
        f = open(file_name, 'wb')
        meta = u.info()
        file_size = int(meta.getheaders("Content-Length")[0])
        file_size_dl = 0
        block_sz = 8192
        while True:
            buffer = u.read(block_sz)
            if not buffer:
                break
            file_size_dl += len(buffer)
            f.write(buffer)
            status = r"%10d  [%3.2f%%]" % \
                (file_size_dl, file_size_dl * 100. / file_size)
            status = status + chr(8)*(len(status)+1)
            print(status)
        f.close()
    else:
        print("...file exists [{}]".format(file_name))

if __name__ == "__main__":
    if not args.source or not args.target:
        print("Usage: python tokenize_data.py --source <path_to_source> --target <path_to_target>")
        sys.exit(1)

    try:
        source_file = args.source
        target_file = args.target

        language = source_file.split('.')[-1]
        directory = os.path.dirname(source_file)
        
        tokenizer_file = os.path.join(directory, 'tokenizer.perl')
        prefixes_file = os.path.join(directory, '../share/nonbreaking_prefixes/nonbreaking_prefix.' + language)
        download_and_write_file(TOKENIZER_URL, tokenizer_file)
        download_and_write_file(TOKENIZER_PREFIXES + language, prefixes_file)

        var = ["perl", tokenizer_file, "-l", source_file.split('.')[-1], '-threads', '8']
        open(target_file, 'w').close()
        with open(source_file, 'r') as inp:
            with open(target_file, 'w') as out:
                subprocess.check_call(
                    var, stdin=inp, stdout=out, shell=False)
    except Exception as e:
        print(e)
        print('Error read/writing fiels')
