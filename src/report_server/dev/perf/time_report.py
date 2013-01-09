#!/usr/bin/python

from datetime import timedelta
import datetime 
import json
import os
import requests
import timeit

START_DATETIME = '20120701T00:00Z'
END_DATETIME = '20120930T00:00Z'


report_query = """
      import requests;
      import json;
      query_data=json.dumps({"user": "shadowman@redhat.com",
                 "byMonth": "12,2012",
                 "contract_number": "All",
                 "rhic": "null",
                 "env": "All"});
      requests.post('http://localhost:8000/api/v1/report/',
                    data=query_data,
                    auth=('shadowman@redhat.com',
                    'shadowman@redhat.com'));
       """


def api_check():
    query_data=json.dumps({"user": "shadowman@redhat.com",
                     "byMonth": "12,2012",
                     "contract_number": "All",
                     "rhic": "null",
                     "env": "All"})
    
    response = requests.post('http://localhost:8000/api/v1/report/',
        data=query_data, auth=('shadowman@redhat.com', 'shadowman@redhat.com'))
    if(response.status_code == 200):
        return True
    else:
        return False


def execute_test(stmt, rows_in_report_data):
    time =  timeit.timeit(stmt=stmt, number=1)
    print(time)
    return time

def report_data_drop():
    os.system('mongo results --eval "db.dropDatabase()"')

def report_data_import(number):
    os.system('mongoimport -d results --collection report_data report_export_' + str(number))

def test(num):
    report_data_drop()
    report_data_import(num)
    return execute_test(report_query, num)

def main():
    if api_check:
        results = []
        print('ok')
        for i in ["1", "100", "1000"]:
            results.append([i, test(i)])
        for i in results:
            print(i)    

def create_json_db_file(number_of_rows):
    """
    create a json file to be used a db import for test
    it will be default use the report_1000 file as the base, so 
    number_of_rows should be in multiples of 1000
    """
    
    #if number_of_rows%1000 == 0:
    #    print('ok')
    #else:
    #    print('number of rows must be a multple of 1000')
    #    exit()
    
    file_to_write = os.path.join(os.getcwd(), 'report_export_' + str(number_of_rows))
    if os.path.exists(file_to_write):
        print('file exists, removing')
        os.system('rm -Rf ' + file_to_write)
    else:
        file_to_write = open(file_to_write, 'w')
    
    counter = 0    
    for line in open(os.path.join(os.getcwd(), 'report_export_1000'), 'r'):
        counter += 1
        json_line = json.loads(line)
        print(json_line)
        json_line['instance_identifier'] = json_line['instance_identifier'] + 'wes'
        string_line = json.dumps(json_line)
        
        if counter <= number_of_rows:
            file_to_write.write(string_line)
        
        else:
            file_to_write.close()
            exit()
        
def create_product_usage(pu_number):
    #rhic_file = open(os.path.join(os.getcwd(), 'rhic.json'), r)
    #splice_file = open(os.path.join(os.getcwd(), 'splice_server.json'), r)
    facts = """
            "facts" : { "lscpu_dot_cpu(s)" : "1",
            "memory_dot_memtotal" : "604836",
            "lscpu_dot_cpu_socket(s)" : "1" }
            """
            
    rhics = []
    splice = []
    for line in open(os.path.join(os.getcwd(), 'rhic.json'), r):
        json_line = json.loads(line)
        rhics.append(json_line)
    for line in open(os.path.join(os.getcwd(), 'splice_server.json'), r):
        json_line = json.loads(line)
        rhics.append(json_line)    
    
    for number in pu_number():
        pu = {}
        pu['splice_server']=splice[0].hostname
        pu['allowed_prodcut_info']=rhic[0].engineering_ids
        pu['unallowed_product_info']=[]
        pu['data']=


        
class ReportDataGenerator(object):
    """
    Report data generator class.

    1. Generates RHICS
    2. Generates Splice Servers
    3. Generates product usage for RHICS
    """

    def __init__(self):
        self.interval = timedelta(hours=1)
        self.splice_servers = []
        self.rhics = []

    def generate(self):
        """
        Generate all the data.
        """
        self.generate_splice_servers()
        self.generate_rhics()
        num_generated = self.generate_usage()
        return num_generated

    def generate_usage(self):
        """
        Generate actual usage.

        The basic pattern is:
        For each hour between start and end time:
            For each rhic:
                For each instance associated with the rhic:
                    Record Product Usage for the instance
        """
        # Generate usage for each RHIC
        num_generated = 0
        usage_datetime = self.start_datetime
        while usage_datetime < self.end_datetime:
            if usage_datetime.hour % 24 == 0:
                logger.info('Generating data for %s' % usage_datetime)
                logger.info('%s records generated so far' % num_generated)
            for rhic in self.rhics:
                # Generate usage for each instance associated with the RHIC.
                for inst_index in range(rhic.num_instances):
                    # TODO: figure out how we want to distribute across splice
                    # servers
                    splice_server = self.splice_servers[0]
                    self.record_rhic_usage(rhic, inst_index, usage_datetime,
                                           splice_server.uuid)
                    num_generated += 1
            usage_datetime += self.interval

        return num_generated

    def record_rhic_usage(self, rhic, inst_index, usage_datetime, 
                          splice_server):
        """
        Record one record of a RHIC usage.
        """
        pu = ProductUsage(
            consumer=rhic.uuid, splice_server=splice_server,
            instance_identifier=rhic.instance_identifiers[inst_index], 
            allowed_product_info=rhic.engineering_ids,
            facts=rhic.instance_facts[inst_index], date=usage_datetime)
        pu.save()

if __name__ == "__main__":
    #create_json_db_file(1)
    main()
    