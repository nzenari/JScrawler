class HOST:
    def __init__(self, hostname, ip, classification, pub_date, add_date):
        '''
        HOST object constructor

        :param hostname: The hostname
        :param ip: The IP address
        :param classification: The classification provided by hpHosts
        :param pub_date: When the host is publicated by hpHosts
        :param add_date: When the host is added in json file
        '''

        self.hostname = hostname
        self.ip = ip
        self.classification = classification
        self.pub_date = pub_date
        self.add_date = add_date


    def get_params_as_dict(self):
        '''

        :return: Return a dictionary with IP's parameters
        '''
        return {'hostname': self.hostname, 'ip': self.ip, 'classification': self.classification, 'pub_date': self.pub_date, 'add_date': self.add_date}