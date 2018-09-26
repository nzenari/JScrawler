import requests
import json
import os
import sys
import hostInfo

__config_file_path = './config.json'
__config = {}

# Get configuration file
if os.path.isfile(__config_file_path):
    config_file = open(__config_file_path, 'r')
    __config.update(json.loads(config_file.read()))
    config_file.close()
else:
    print("Configuration file does not exist.")
    sys.exit(0)


gsb = __config['GSB_url']
params = {'key': __config['GSB_key']}
header = {'Content-type': 'application/json'}

body_list = os.listdir(__config['out_dir_path'] + __config['GSB_dir'])

simplify_label_dict = {}

for file in body_list:

    body = open(__config['out_dir_path'] + __config['GSB_dir'] + file, 'r')

    body_dict = json.loads(body.read())

    data = body_dict

    request = requests.post(gsb, params=params, json=data)
    json_request = request.json()
    print(json_request)

    for match in json_request['matches']:
        try:
            url = match['threat']['url']
            if url not in simplify_label_dict:
                print('URL not in simplify_label_dict')
                simplify_label_dict[url] = {'threats': {match['threatType']: {'platformType': [match['platformType']]}}}
            else:

                if match['threatType'] not in simplify_label_dict[url]['threats'].keys():
                    simplify_label_dict[url]['threats'][match['threatType']] = {'platformType': [match['platformType']]}

                if match['platformType'] not in simplify_label_dict[url]['threats'][match['threatType']][
                    'platformType']:
                    simplify_label_dict[url]['threats'][match['threatType']]['platformType'].append(
                        match['platformType'])
        except:
            print('HTTP status: ' + str(request))

print(simplify_label_dict)

for host in simplify_label_dict.keys():
    hostInfo.add_tag_gsb(host, simplify_label_dict[host])
