# Adapted from Alessandro Fantini' script

import os
import json
import sys
import shutil
import mmap

__config_file_path = './config.json'
__config = {}


def run_analysis():
    root = __config['out_dir_path'] + __config['javascript_dir_path']
    maxeval = 5
    counter = 0
    counter2 = 0
    keyword = "eval"

    for path, subdirs, files in os.walk(root):
        evals = [0] * maxeval
        for i in range(1,maxeval):
            search = keyword+str(i)
            for filename in files:
                if filename.startswith(search):
                    evals[i] = evals[i]+1
        for filename in files:
            if filename.startswith("tr_._"):
                malware = os.path.join(path, filename)
                if os.stat(malware).st_size != 0:
                    with open(malware, 'rb', 0) as file, \
                            mmap.mmap(file.fileno(), 0, access=mmap.ACCESS_READ) as s: #legge il file
                        index = 0
                        countereval = 0
                        while index < len(s):
                            index = s.find(b"eval(", index)
                            if index == -1:
                                break
                            countereval += 1
                            index += 5
                        if countereval > 0:
                            counter += 1
                        else:
                            counter2 += 1
                        evalcount = 0
                        for i in range(0,maxeval):
                            evalcount += evals[i]
                        print(filename + " has " + str(countereval) + " explicit eval, and produce "+ str(evalcount)+" evals file")

    print("\nNumber of malware with explicit eval:" + str(counter))
    print("\nNumber of malware with no explicit eval:" + str(counter2))


def get_configuration():
    # Get configuration file
    if os.path.isfile(__config_file_path):
        config_file = open(__config_file_path, 'r')
        __config.update(json.loads(config_file.read()))
        config_file.close()
    else:
        print("Configuration file does not exist.")
        sys.exit(0)


def mk_js_dir():
    js_dir_path = __config['out_dir_path'] + __config['javascript_dir_path']
    if not os.path.isdir(js_dir_path):
        try:
            print('Creating dir ' + js_dir_path)
            os.mkdir(js_dir_path)
        except OSError as oserr:
            print('ERROR. Cannot create dir: ' + js_dir_path)
            print(oserr)


def copy_files():
    mk_js_dir()

    count = 0
    js_count = 0

    hosts = os.listdir(__config['out_dir_path'] + __config['hosts_dir_path'])

    for host in hosts:
        js_dir_path = __config['out_dir_path'] + __config['hosts_dir_path'] + host + '/' \
                      + __config['heritrix_dir_path'] + __config['javascript_dir_path']

        if os.path.isdir(js_dir_path):

            js_files = os.listdir(js_dir_path)

            for js_file in js_files:
                src = js_dir_path + '/' + js_file
                dst = __config['out_dir_path'] + __config['javascript_dir_path'] \
                      + 'tr_._' + js_file
                shutil.copy(src, dst)
                js_count += 1
            count += 1


def main():
    get_configuration()
    copy_files()
    run_analysis()


if __name__ == '__main__':
    main()