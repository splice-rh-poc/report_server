#!/usr/bin/python

from datetime import timedelta
from pymongo import Connection

import datetime 
import json
import os
import requests
import time
import timeit

c = Connection()

#SETUP
report_query = """
      import requests;
      import json;
      query_data=json.dumps({"user": "shadowman@redhat.com",
                 "startDate": "10/01/2012",
                 "endDate": "01/10/2013",
                 "contract_number": "All",
                 "rhic": "null",
                 "env": "All"});
      requests.post('http://localhost:8000/api/v1/report/',
                    data=query_data,
                    auth=('shadowman@redhat.com',
                    'shadowman@redhat.com'));
       """

product_usage_post_test = """
                  { "_id" : { "$oid" : "50eedde4a585a61915000003" },
                  "_types" : [ "ProductUsage" ],
                  "splice_server" : "splice_server_uuid-1",
                  "allowed_product_info" : [ "69" ],
                  "unallowed_product_info" : [],
                  "facts" :
                     { "lscpu_dot_cpu(s)" : "1",
                     "memory_dot_memtotal" : "604836",
                     "lscpu_dot_cpu_socket(s)" : "1" },
                  "_cls" : "ProductUsage",
                  "instance_identifier" : "12:31:3D:08:40:00",
                  "date" : { "$date" : 1351296000000 },
                  "consumer" : "8d401b5e-2fa5-4cb6-be64-5f57386fda86" }
                  """

def product_usage_post(num):
    filename = 'pu.'  + str(num)  
    path = os.getcwd() + '/pu/'
    fullpath = os.path.join(path, filename)    
 
    stmt = """
    
    import requests;
    import json;
    
    raw_file = open('""" + fullpath + """' , 'rb')
    data = raw_file.read()
    
    requests.post('http://localhost:8000/api/v1/productusage/', data=data)

    """
    return stmt

def api_report_check():
    """
    Quick check to verify the api is working as expected
    """
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

def api_import_check():
    """
    Quick check to verify the api is working as expected
    """    
    product_usage_drop()
    product_usage_setup()
    response = requests.post('http://localhost:8000/api/v1/productusage/',
                             data=product_usage_post_test)
    if(response.status_code == 202):
            return True
    else:
        return False    

#DB's
def report_data_drop():
    #print('sleep 5 seconds')
    #time.sleep(5) 
    c.drop_database('results')
    
def report_data_import(num):
    os.system('mongoimport -d results --collection report_data report_export_' + str(num))

def product_usage_drop():
    c.drop_database('checkin_service')

def product_usage_setup():
    os.system('mongoimport -d checkin_service --collection splice_server ' + (os.path.join(os.getcwd(), 'splice_server.json')))
    
#TESTS
def execute_test(stmt, rows_in_report_data):
    #print(stmt)
    time =  timeit.timeit(stmt=stmt, number=1)
    print(time)
    return time

def test_report(num):
    return execute_test(report_query, num)

def test_import(num):
    product_usage_drop()
    report_data_drop()
    product_usage_setup()
    return execute_test(product_usage_post(num), num)

def main_report(num):
    
    print('ok')
    print('*' * 10 + ' TESTING REPORT ' + num) 
    result = (["report", num, test_report(num)])

    return result

def main_import(num):
    #if api_import_check():
     
    print('*' * 10 + ' TESTING IMPORT ' + num) 
    result = (["import", num, test_import(num)])
    os.system('mongoexport -d results -c report_data --out report_export_' + num + ' --jsonArray')
    os.system('ls report_export_' + num)
        
    return result
    

if __name__ == "__main__":
    results = []
    #for num in ["100", "1000", "2000", "20000", "40000", "100000" ]:
    for num in ["100", "1000" ]:
        i = main_import(num)
        r = main_report(num)
        results.append( [i, r])
    print('='* 30)
    print('final-results:')
    for r in results:
        print(r)
    