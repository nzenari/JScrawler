import warc
import gzip
import re
import sys
import os
import getopt
import json
import body
import shutil


__config_file_path = './config.json'
__config = {}
crawled_seed_set = set()


def clean():
    '''
    Remove the host's dir if it was not crawled
    '''
    # list dir
    dirs = os.listdir(__config['out_dir_path'] + __config['hosts_dir_path'])
    for dir in dirs:
        if dir not in crawled_seed_set:
            print('Removing ' + dir + ' directory.')
            shutil.rmtree(__config['out_dir_path'] + __config['hosts_dir_path'] + dir)


def get_configuration():
    # Get configuration file
    if os.path.isfile(__config_file_path):
        config_file = open(__config_file_path, 'r')
        __config.update(json.loads(config_file.read()))
        config_file.close()
    else:
        print("Configuration file does not exist.")
        sys.exit(0)


def parser(record, url):
    '''
    Save record into file.
    :param record: single warc record
    :param url: url link of the record
    '''

    # modify url without slashes (file name)
    url = re.sub('^http\\w*://','', url)

    # replacing slash with backslash
    url = url.replace('/', '\\')
    url = url.replace('%', '')

    # check if file name is too long
    if len(url) > 255:
        url = url[:254]

    # create and save the record into the file
    print('Saving file: ' + url)
    with open(url, 'w') as f:
        for line in record.decode('utf8', 'ignore').splitlines():
            f.write(line)
            f.write('\n')


def change_path(url):
    '''
    Move into domain dir, create heritrix subdir and move into it
    :param url: current url
    '''

    reg = '^(?:http:\/\/|www\.|https:\/\/)([^\/]+)'

    # search for each domain
    domain_dir = re.search(reg, url).group(0)
    domain_dir = re.sub('^http\\w*://','', domain_dir)

    # check if domain dir already exists, otherwise create it
    if not os.path.exists(domain_dir):
        os.mkdir(domain_dir)
        os.chdir(domain_dir)

    # change in domain dir
    else:
        os.chdir(domain_dir)

    # create heritrix dir
    if not os.path.exists(__config['heritrix_dir_path']):
        os.mkdir(__config['heritrix_dir_path'])

    # move into heritrix dir
    os.chdir(__config['heritrix_dir_path'])

    print('Moving into ' + os.getcwd())


def extractor(warc_file, out_path):
    '''
    Extract only response record.
    :param warc_file: warc archive
    '''
    dic = {}

    # search for html response
    f = warc.WARCFile(fileobj=warc_file)
    for num, record in enumerate(f):
        if record['WARC-Type'] == 'response':
            dic[record['WARC-Target-URI']] = record.payload.read()

    reg = '^(?:http:\/\/|www\.|https:\/\/)*([^\/]+)'
    for url in dic.keys():
        # save url crawled
        domain = re.search(reg, url).group(0)
        domain = re.sub('^http\\w*://', '', domain)
        crawled_seed_set.add(domain)

        # save current directory
        hosts_dir = os.getcwd()

        #change path
        change_path(url)

        # parser record
        parser(dic.get(url), url)

        # return into previously directory
        os.chdir(hosts_dir)

    # add only crawled seeds to seeds.text
    os.chdir(out_path)

    with open(__config['seeds_filename'], 'w') as f:
        for url in crawled_seed_set:
            f.write(url)
            f.write('\n')

    # create body.json for GSB
    os.chdir('..')
    body.create_body([element for element in crawled_seed_set])


def main(argv):

    get_configuration()

    print('Warc extractor is started')

    if len(argv) == 0:
        print('Error: invalid use.')
        print('python3.6 warcExtractor.py -s <source.warc.gz>')
        sys.exit(2)

    try:
        opt, arg = getopt.getopt(argv, "s", ["idir="])
    except getopt.GetoptError:
        print('Error: invalid use.')
        print('python3.6 warcExtractor.py -s <source.warc.gz>')
        sys.exit(2)

    # get source file from command line
    source = arg[0]

    # open warc.gz file
    unzip_file = gzip.open(source, mode="rb")

    # change dir (out/hosts/)
    os.chdir(__config['out_dir_path'])
    out_path = os.getcwd()
    os.chdir(__config['hosts_dir_path'])

    extractor(unzip_file, out_path)

    clean()


if __name__ == '__main__':
    main(sys.argv[1:])
