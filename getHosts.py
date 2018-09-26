from bs4 import BeautifulSoup
import urllib.request
import host
import json
from datetime import *
import os
import sys
import multiprocessing
import threading
import re
import hostInfo


__config_file_path = './config.json'
__config = {}

hosts = []
tot_new = []


class ThreadGetAndParse(threading.Thread):
    def __init__(self, thread_num, start_p, pages, cores, classification, url):
        threading.Thread.__init__(self)
        self.thread_num = thread_num
        self.start_p = start_p
        self.pages = pages
        self.cores = cores
        self.classification = classification
        self.url = url

    def run(self):

        for page in range(int(self.start_p), int(self.pages)+1, int(self.cores)):

            print("{0}) Requesting page {1}".format(self.thread_num, page))
            # get page
            html = get_html(self.url.format(self.classification, page))

            if html is not None:
                # Parse items
                hosts_temp, new, count, end_flag = parse_table(get_table(html))

                if len(hosts_temp) > 0:
                    for host_temp in hosts_temp:
                        hosts.append(host_temp)
                        hostInfo.create_file(host_temp['hostname'], host_temp)

                tot_new.append((page, new))

                if end_flag:
                    # no new host
                    print("There are not new hosts. Thread #{0} is stopping.".format(self.thread_num))
                    break

            else:
                print(self.url.format(self.classification, page) + " is none.")


def get_html(url):
    '''
    :param url: hpHosts url
    :return: HTML parsed by BeautifulSoup
    '''

    print('Getting html from {0}'.format(url))
    try:
        # Get hosts from url
        req = urllib.request.Request(url=url)
        f = urllib.request.urlopen(req)
        html = f.read().decode('utf-8')

        # Create BeautifulSoup object
        soup = BeautifulSoup(html, 'html.parser')
        return soup

    except Exception as e:
        print('ERROR. Error in getting html page from ' + url)
        print(e)
        return None


def get_table(html):
    '''
    :param html: BeautifulSoup output
    :return: A list of tables extracted by BeautifulSoup
    '''

    return html.find_all('table')[4]


def get_number_of_pages(table):
    '''
    Return the number of pages written in the td of the first tr
    :param table: HTML table
    :return: int which rappresents the number of pages
    '''

    print("Getting number of pages.")
    s = re.findall('Page\s1/[0-9]+', str(table.find_all('tr')[0].find_all('td')[0]))[0]
    return int(s[s.find('/')+1:])


def parse_table(table):
    '''
    :param table: A table of interest
    :return: A list of host objects
    '''

    print('Parsing HTML table')

    last_check = get_last_check()
    from_date = datetime.strptime(__config['download_from_date'], '%d/%m/%Y %H:%M:%S')
    to_date = datetime.strptime(__config['download_to_date'], '%d/%m/%Y %H:%M:%S')
    table_hosts = []
    new = 0
    count = 0
    flag_old = False
    rows = table.find_all('tr')

    # for each row
    for i in range(2, len(rows)):
        # table details
        tds = rows[i].find_all('td')

        # check class
        if len(tds) == 5:
            count += 1

            hostname = tds[1].string.strip()
            ip_address = tds[2].string.strip()
            classification = tds[3].string.strip()
            pub_date = tds[4].string.strip()
            add_date = datetime.strftime(datetime.utcnow(), '%d/%m/%Y %H:%M:%S')

            pub_date_obj = datetime.strptime(pub_date, '%d/%m/%Y %H:%M:%S')
            if to_date < pub_date_obj:
                flag_old = False
            elif from_date <= pub_date_obj <= to_date and (last_check is None or pub_date_obj > last_check):
                print("Creating a new host: {0}".format(hostname))
                table_hosts.append(host.HOST(hostname, ip_address, classification, pub_date, add_date).get_params_as_dict())
                new += 1
            else:
                # set to True if pub_date < last_check
                flag_old = True
        else:
            continue

    return table_hosts, new, count, flag_old


def write_file(last_check):
    '''
    Write seeds file
    :param last_check: Date of last check
    '''

    try:
        # If out dir does not exist, make it
        if not os.path.isdir(__config['out_dir_path']):
            try:
                print('Creating dir ' + __config['out_dir_path'])
                os.mkdir(__config['out_dir_path'])
            except OSError as oserr:
                print('ERROR. Cannot create dir: ' + __config['out_dir_path'])
                print(oserr)

        # TXT FOR CRAWLER #
        # Open file for crawler
        txt_for_crawler = open(__config['out_dir_path'] + __config['seeds_filename'], 'w')

        list_host = []
        # Write to txt file the hostname
        print('Writing file ' + __config['out_dir_path'] + __config['seeds_filename'])
        for host_obj in hosts:
            host_params = host_obj
            list_host.append(host_params)
            txt_for_crawler.write(host_params['hostname'] + '\n')

        txt_for_crawler.close()

        # write last check in configuration file
        print('Writing file ' + __config_file_path)
        __config['last_check'] = last_check
        with open(__config_file_path, 'w') as write_file:
            json.dump(obj=__config, fp=write_file, sort_keys=False, indent=4, separators=(',', ':'))

    except Exception as e:
        print('ERROR. Error in writing files.')
        print(e)


def get_last_check():
    '''
    :return: The last check date provided from JSON file, None if file does not exist.
    '''

    try:
        last_check = __config['last_check']
        print("Returning last check: {0}.".format(last_check))
        return datetime.strptime(last_check, '%d/%m/%Y %H:%M:%S')
    except:
        print("Returning last check: None.")
        return None


def get_timedelta_as_string(start, end):
    '''
    Return the work time delta.
    :param start: datetime object
    :param end: datetime object
    :return: string
    '''

    sec = (end - start).seconds
    res = ''

    # days
    days = sec // 86400
    if days == 1:
        res += '1 day '
        sec -= 86400 * days
    elif days > 1:
        res += str(days) + ' days '
        sec -= 86400 * days

    # hours
    hours = sec // 3600
    if hours == 1:
        res += '1 hour '
        sec -= 3600 * hours
    elif hours > 1:
        res += str(hours) + ' hours '
        sec -= 3600 * hours

    # minutes
    minutes = sec // 60
    if minutes == 1:
        res += '1 minute '
        sec -= 60 * minutes
    elif minutes > 1:
        res += str(minutes) + ' minutes '
        sec -= 60 * minutes

    # seconds
    if sec == 1:
        res += '1 second '
    elif sec > 1:
        res += str(sec) + ' seconds '

    return res[:-1]


def main():
    print('Host collector is started')
    start_time_obj = datetime.utcnow()
    print('Start: ' + datetime.strftime(start_time_obj, '%d/%m/%Y %H:%M:%S'))

    # Get configuration file
    if os.path.isfile(__config_file_path):
        config_file = open(__config_file_path, 'r')
        __config.update(json.loads(config_file.read()))
        config_file.close()
    else:
        print('ERROR. Configuration file does not exist.')
        sys.exit(0)

    # For each year of interest
    for classification in __config['class_to_download']:

        print("Request for class {0}".format(classification))

        # get number of pages written in the each page
        url_for_pages = __config['host_file_url'].format(classification, 1)
        html_for_pages = get_html(url_for_pages)
        # if there exists at least one page
        if html_for_pages is not None:
            # get number of pages
            pages = get_number_of_pages(get_table(html_for_pages))

            # get cores number
            cores = multiprocessing.cpu_count()

            # Create threads
            threads = []
            count_thread = 1
            for core in range(0, cores):
                print("Creating thread {}".format(count_thread))
                count_thread += 1
                threads.append(ThreadGetAndParse(core + 1, core + 1, pages, cores, classification, __config['host_file_url']))

            # Start threads
            count_thread = 1
            for thread in threads:
                print("Staring thread {}".format(count_thread))
                count_thread += 1
                thread.start()

            # Join threads
            count_thread = 1
            for thread in threads:
                print("Joining thread {}".format(count_thread))
                count_thread += 1
                thread.join()

        else:
            print(url_for_pages + " is none.")

        # write files
        if len(hosts) > 0:
            write_file(datetime.strftime(start_time_obj, '%d/%m/%Y %H:%M:%S'))
        else:
            print("JSON already updated. {0}".format(str(len(hosts))))

    n = 0
    for i in range(0, len(tot_new)):
        n += tot_new[i][1]

    end_time_obj = datetime.utcnow()
    print('End: ' + datetime.strftime(end_time_obj, '%d/%m/%Y %H:%M:%S'))

    print('Host collector is ended in {0}.\n{1} hosts was new.'.format(get_timedelta_as_string(start_time_obj, end_time_obj), n))


if __name__ == '__main__':
    main()
