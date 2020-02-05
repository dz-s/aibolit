import argparse
import multiprocessing
import os
import subprocess
import time
from multiprocessing import Pool
from pathlib import Path
import csv

parser = argparse.ArgumentParser(description='Compute Readability score')
parser.add_argument('--filename',
                    help='path for file with a list of Java files')

args = parser.parse_args()

if args.filename is None:
    print("Usage: python readbility.py --filename <FILENAME>")
    exit(1)

dir_path = os.path.dirname(os.path.realpath(__file__))
results = {}

path = '05'
os.makedirs(path, exist_ok=True)
csv_file = open('05/05_readability.csv', 'w', newline='\n')
writer = csv.writer(
    csv_file, delimiter=';',
    quotechar='"', quoting=csv.QUOTE_MINIMAL)


def log_result(result):
    # This is called whenever foo_pool(i) returns a result.
    # result_list is modified only by the main process, not the pool workers.
    writer.writerow(result)
    csv_file.flush()


def call_proc(cmd, java_file):
    """ This runs in a separate thread. """
    print('Running ', ' '.join(cmd))
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    score = None
    if not err:
        score = float(out.decode().split('readability:')[-1].strip())
    else:
        print('Error when running: {}'.format(out))
    return java_file, score


if __name__ == '__main__':
    t1 = time.time()
    pool = Pool(multiprocessing.cpu_count())
    jar_path = str(Path(dir_path, r'readability.jar')).strip()
    handled_files = []

    with open(args.filename, 'r') as f:
        for i in f.readlines():
            java_file = str(Path(dir_path, i)).strip()
            pool.apply_async(
                call_proc,
                args=(['java', '-jar', 'rsm.jar', java_file], java_file,),
                callback=log_result)

    pool.close()
    pool.join()

    print(results)
    t2 = time.time()
    print('It took this many seconds ' + str(t2 - t1))
