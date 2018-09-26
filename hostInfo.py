import json
import sys
import os
import re
from datetime import *


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


def create_file(host, dictionary):
    if len(__config) == 0:
        get_configuration()

    # create host's dir and file
    host_dir = __config['out_dir_path'] + __config['hosts_dir_path'] + get_dir(host) + '/'
    if not os.path.isdir(host_dir):
        print('Creating directory {0}'.format(host_dir))
        os.makedirs(host_dir)

    # for safety reasons, add VT and GSB empty fields
    dictionary['VT'] = {}
    dictionary['GSB'] = {}

    with open(host_dir + __config['host_json_filename'], 'w') as write_file:
        json.dump(obj=dictionary, fp=write_file, sort_keys=False, indent=4, separators=(',', ':'))


def add_tag_vt(host, dictionary):

    if len(__config) == 0:
        get_configuration()

    # Check if host's dir exists
    host_dir = __config['out_dir_path'] + __config['hosts_dir_path'] + get_dir(host) + '/'
    if os.path.isdir(host_dir):
        # get json
        if os.path.isfile(host_dir + __config['host_json_filename']):
            # If it exists, open and load JSON
            json_file = open(host_dir + __config['host_json_filename'], 'r')
            json_dict = json.loads(json_file.read())
            json_file.close()

            json_dict['VT'] = dictionary

            print('VT tags added. Writing file {0}'.format(host_dir + __config['host_json_filename']))
            # Write JSON file
            with open(host_dir + __config['host_json_filename'], 'w') as write_file:
                json.dump(obj=json_dict, fp=write_file, sort_keys=False, indent=4, separators=(',', ':'))
        else:
            d = {"ip": "", "pub_date": "", "classification": "", "hostname": get_dir(host),
                 "add_date": datetime.strftime(datetime.utcnow(), '%d/%m/%Y %H:%M:%S')}
            create_file(get_dir(host), d)
            add_tag_vt(host, dictionary)


def add_tag_gsb(host, dictionary):

    if len(__config) == 0:
        get_configuration()

    # Check if host's dir exists
    host_dir = __config['out_dir_path'] + __config['hosts_dir_path'] + get_dir(host) + '/'
    if os.path.isdir(host_dir):
        # get json
        if os.path.isfile(host_dir + __config['host_json_filename']):
            # If it exists, open and load JSON
            json_file = open(host_dir + __config['host_json_filename'], 'r')
            json_dict = json.loads(json_file.read())
            json_file.close()

            json_dict['GSB'] = dictionary

            print('GSB tags added. Writing file {0}'.format(host_dir + __config['host_json_filename']))
            # Write JSON file
            with open(host_dir + __config['host_json_filename'], 'w') as write_file:
                json.dump(obj=json_dict, fp=write_file, sort_keys=False, indent=4, separators=(',', ':'))


def get_dir(host):
    reg = '^(?:http:\/\/|www\.|https:\/\/)*([^\/]+)'
    dir = re.search(reg, host).group(0)
    dir = re.sub('^http\\w*://', '', dir)

    return dir
