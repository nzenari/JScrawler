from bs4 import BeautifulSoup
import os
import logging
import json

# logging configuration
logging.basicConfig(level=logging.DEBUG,
                    format='%(message)s',)
# counter for file name
counter = 0

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

def parser(file):
    '''
    Extract javascript from html document.
    :param file: file to parse
    '''

    global counter
    # open file
    f = open(file, 'r')
    source = f.read()

    # parsing js script
    soup = BeautifulSoup(source)
    js_codes = soup.find_all("script")

    # is there are some scripts
    if js_codes:
        # create js dir
        if not os.path.exists(__config['javascript_dir_path']):
            os.mkdir(__config['javascript_dir_path'])

        with open(__config['javascript_dir_path'] + 'script' + str(counter) + '.js', 'w') as js_file:
            # header
            js_file.write('Extracted from ' + file + '\n')
            js_file.write('-' * (len('Extracted from ') + len(file)) + '\n\n')

            # script
            for code in js_codes:
            # if there is some code in the script
                if code.text:
                    js_file.write(code.get_text())
                js_file.write('\n')

        # update counter file name
        counter += 1

def searching_files():
    '''
    List all directories and files to be parsed.
    '''

    # get domain_dirs list (from hosts dir)
    hosts_dir = os.getcwd()
    domain_dirs = os.listdir(hosts_dir)

    logging.debug('Listing directories...')

    # files cleaning
    if '.DS_Store' in domain_dirs:
        domain_dirs.remove('.DS_Store')

    for dir in domain_dirs:
        # list all file in each domain_dirs
        files = os.listdir(__config['heritrix_dir_path'])

        # files cleaning
        if '.DS_Store' in files:
            files.remove('.DS_Store')

        # move into heritrix dir
        os.chdir(dir + '/' + __config['heritrix_dir_path'])
        print(dir)

        # scan all files
        for file in files:
            logging.debug('Parsing ' + file)
            parser(file)

        # return to previously directory
        os.chdir(hosts_dir)



def main():
    get_configuration()

    logging.debug('Javascript extractor is started')

    # move into out/hosts/
    os.chdir(__config['out_dir_path'] + __config['hosts_dir_path'])

    # start js extractor
    searching_files()

if __name__ == '__main__':
    main()
