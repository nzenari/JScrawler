import requests
import time
import hostInfo
import sys
import os
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


def do_requests():

    if len(__config) == 0:
        get_configuration()

    # apro il file degli url
    hosts = open(__config['out_dir_path'] + __config['seeds_filename'], 'r')

    # leggo tutti gli url
    hosts_lines = hosts.readlines()

    count = 1

    for threat_url in hosts_lines:

        print(str(count) + '/' + str(len(hosts_lines)) + ' Threat_url: ' + threat_url[:-1])
        count += 1

        # url per la chiamata di virusTotal
        vt = __config['vt_requests_url']
        # parametri per l'interrogazione di virusTotal
        params = {'apikey': __config['vt_api_key'], 'url': threat_url}

        # interrogazione di virusTotal
        response = requests.post(vt, params=params)


        # list of error
        hosts_error = []

        try:
            json_response = response.json()
            get_report(json_response['scan_id'])
        except Exception as e:
            hosts_error.append(threat_url)
            print('ERROR. ' + e)

        # if at least one error occurred, write error file
        if len(hosts_error) > 0:
            with open(__config['out_dir_path'] + __config['vt_error_file']) as write_file:
                for url in hosts_error:
                    write_file.write(url + '\n')

        time.sleep(30)


def get_report(scan_id):
    url = __config['vt_report_url']

    params = {'apikey': __config['vt_api_key'], 'resource': scan_id}
    headers = {"Accept-Encoding": "gzip, deflate",
               "User-Agent": "gzip,  My Python requests library example client or username"}

    response = requests.get(url, params=params, headers=headers)

    report = response.json()

    # print(report)

    host_dict = {'vt_scan_date': report['scan_date'], 'positives': report['positives'], 'total': report['total']}

    hostInfo.add_tag_vt(report['url'], host_dict)


if __name__ == '__main__':
    do_requests()