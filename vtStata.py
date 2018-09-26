import os
import json
import sys


__config_file_path = './config.json'
__config = {}


def get_configuration():
    # Get configuration file
    if os.path.isfile(__config_file_path):
        config_file = open(__config_file_path, 'r')
        __config.update(json.loads(config_file.read()))
        config_file.close()
    else:
        print("Configuration file does not exist.")
        sys.exit(0)


def main():

    get_configuration()

    count = 0

    hosts = os.listdir(__config['out_dir_path'] + __config['hosts_dir_path'])

    for host in hosts:
        info_json = {}
        info_file_path = __config['out_dir_path'] + __config['hosts_dir_path'] + host + '/' +  __config['host_json_filename']
        if os.path.isfile(info_file_path):
            info_file = open(info_file_path, 'r')
            info_json.update(json.loads(info_file.read()))
            info_file.close()
        else:
            print('ERROR. Info file does not exist. (' + info_file_path + ')')

        try:
            positives = info_json['VT']['positives']
            if positives == 0:
                count += 1
                print(info_file_path)
        except:
            print("C -- " + info_file_path)
            continue

    print('\nVirus Total tagged {0} hosts of {1} as not maliciuos\n'.format(count, len(hosts)))


if __name__ == '__main__':
    main()