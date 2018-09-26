import os
import sys
import json


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


def create_body(hosts_list):
    if len(__config) == 0:
        get_configuration()

    # JSON FOR GSB #
    # If GSB out dir does not exist, make it
    if not os.path.isdir(__config['GSB_dir']):
        try:
            print('Creating dir ' + __config['out_dir_path'] + __config['GSB_dir'])
            os.mkdir(__config['out_dir_path'] + __config['GSB_dir'])
        except OSError as oserr:
            print('ERROR. Cannot create dir: ' + __config['out_dir_path'] + __config['GSB_dir'])
            print(oserr)

    dict_list = []
    for host in hosts_list:
        dict_list.append({'url': host})

    list_host_list = []
    for i in range(0, len(dict_list) // 500):
        list_host_list.append(dict_list.pop() for j in range(0, 500))
    if len(dict_list) > 0:
        list_host_list.append(dict_list)

    block = 0
    for (dirpath, dirnames, filenames) in os.walk(__config['out_dir_path'] + __config['GSB_dir']):
        block = len(filenames)
        break

    for list_to_write in list_host_list:
        print('Writing file ' + __config['out_dir_path'] + __config['GSB_dir'] + __config['json_GSB_filename'] + str(
            block) + '.json')
        with open(__config['out_dir_path'] + __config['GSB_dir'] + __config['json_GSB_filename'] + str(block) + '.json',
                  'w') as GSB_file:
            to_write = {'client': {'clientId': __config['GSB_clientId'],
                                   'clientVersion': __config['GSB_clientVersion']},
                        'threatInfo': {'threatTypes': __config['GSB_threatTypes'],
                                       'platformTypes': __config['GSB_platformTypes'],
                                       'threatEntryTypes': __config['GSB_threatEntryTypes'],
                                       'threatEntries': list(list_to_write)}}
            block += 1
            json.dump(obj=to_write, fp=GSB_file, sort_keys=False, indent=4, separators=(',', ':'))