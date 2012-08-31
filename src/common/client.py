#Fetch data from various services
import os
import httplib
import urllib
import json
import logging
import time
import base64
from common import config
import pycurl, cStringIO, json
from subprocess import call

_LOG = logging.getLogger(__name__)


class ApiClient:
    config.init()
    
    @staticmethod
    def get_all_rhics():
        c = config.get_rhic_serve_config_info()
        status, data = request(c['host'], c['port'], '/api/rhic/', c['user'], c['passwd'], False)
        if status == 200:
            return data
        raise Exception(status, data)
    @staticmethod
    def get_rhic(rhic_id):
        c = config.get_rhic_serve_config_info()
        api = '/api/rhic/503e31fdd9c1416fd0000003/'
        #status, data = requestCurl(c['host'], c['port'], api, c['user'], c['passwd'], False)
        data = requestCurl(c['host'], c['port'], api, c['user'], c['passwd'], False)
        return data
        #if status == 200:
        #    return data
        #raise Exception(status, data)
        
    @staticmethod
    def get_account():
        c = config.get_rhic_serve_config_info()
        api = '/api/account/'
        #status, data = requestCurl(c['host'], c['port'], api, c['user'], c['passwd'], False)
        data = requestCurl(c['host'], c['port'], api, c['user'], c['passwd'], False)
        return data
    
    @staticmethod
    def get_contract(api):
        c = config.get_rhic_serve_config_info()
        #status, data = requestCurl(c['host'], c['port'], api, c['user'], c['passwd'], False)
        data = requestCurl(c['host'], c['port'], api, c['user'], c['passwd'], False)
        return data
    
    
    @staticmethod
    def get_rhic_details(RHIC):
        id = getRHICdata(RHIC)
        c = config.get_rhic_serve_config_info()
        api = '/api/rhic/' + id + '/'
        #status, data = requestCurl(c['host'], c['port'], api, c['user'], c['passwd'], False)
        data = requestCurl(c['host'], c['port'], api, c['user'], c['passwd'], False)
        return data
    
    @staticmethod
    def getRHIC_in_account():
        c = config.get_rhic_serve_config_info()
        api = '/api/account/'
        #status, data = requestCurl(c['host'], c['port'], api, c['user'], c['passwd'], False)
        data = requestCurl(c['host'], c['port'], api, c['user'], c['passwd'], False)
        account_doc = data[0]
        print(account_doc)
        account_id = account_doc[0]['account_id'] 
        
        api = '/api/rhic/'
        data = requestCurl(c['host'], c['port'], api, c['user'], c['passwd'], False)
        #all_rhics = json.loads(data[0])
        all_rhics = data
        
        my_rhics = []
        for rhic in all_rhics:
            if rhic['account_id'] == account_id:
                my_rhics.append(rhic['uuid'])
        return my_rhics
    
    
def getRHICdata(RHIC):
    c = config.get_rhic_serve_config_info()
           
    api = '/api/rhic/'
    data = requestCurl(c['host'], c['port'], api, c['user'], c['passwd'], False)
    all_rhics = data
    #all_rhics = json.loads(data)
    
    my_rhics = []
    for rhic in all_rhics:
        if rhic['uuid'] == RHIC:
            return rhic['id']
    
    
            
    
def request(host, port, url, debug=False):
    connection = httplib.HTTPSConnection(host, port)
    if debug:
        connection.set_debuglevel(100)
    method = 'GET'
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
       
    }
    _LOG.info("Sending HTTP request to: %s:%s%s with headers:%s" % (host, port, url, headers))
    url = 'https://ec2-184-72-159-16.compute-1.amazonaws.com/api/rhic/503e31fdd9c1416fd0000003/'
    connection.request(method, url, body=None, headers=headers)

    response = connection.getresponse()
    response_body = response.read()
    if response.status == 200:
        response_body_raw = response_body
        response_body = json.loads(response_body_raw)
        if debug:
            print "Response: %s %s" % (response.status, response.reason)
            print "JSON: %s" % (json.dumps(response_body))
            output = open("example_rhic_serve_data_%s.json" % (time.time()), "w")
            output.write(response_body_raw)
            output.close()
    return response.status, response_body

def request_secure(host, port, url, username, password, debug=False):
    connection = httplib.HTTPConnection(host, port)
    if debug:
        connection.set_debuglevel(100)
    method = 'GET'
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    raw = ':'.join((username, password))
    encoded = base64.encodestring(raw)[:-1]
    headers['Authorization'] = 'Basic ' + encoded

    _LOG.info("Sending HTTP request to: %s:%s%s with headers:%s" % (host, port, url, headers))
    connection.request(method, url, body=None, headers=headers)

    response = connection.getresponse()
    response_body = response.read()
    if response.status != 200:
        _LOG.info("Response status '%s', '%s', '%s'" % (response.status, response.reason, response_body))
    if response.status == 200:
        response_body_raw = response_body
        response_body = json.loads(response_body_raw)
        if debug:
            print "Response: %s %s" % (response.status, response.reason)
            print "JSON: %s" % (json.dumps(response_body))
            output = open("example_candlepin_data_%s.json" % (time.time()), "w")
            output.write(response_body_raw)
            output.close()
    return response.status, response_body

def requestPyCurl(host, port, url, username, password, debug=False):
    buf = cStringIO.StringIO()
    URL = 'https://'+ host + url
    USER = username
    PASS = password
    conn = pycurl.Curl()
    conn.setopt(pycurl.USERPWD, "%s:%s" % (USER, PASS))
    conn.setopt(pycurl.URL, URL)
    conn.setopt(pycurl.WRITEFUNCTION, buf.write)
    conn.perform()
    return buf

'''
def requestCurl(host, port, url, username, password, debug=False):
    options = 'curl -u ' + username + ':' + password + ' https://' + host + url + ' -k'
    print(options)
    out = os.popen(options)
    return out.readlines()
'''

def requestCurl(host, port, url, username, password, debug=False):
    connection = httplib.HTTPSConnection(host, port)
    if debug:
        connection.set_debuglevel(100)
    method = 'GET'
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    raw = ':'.join((username, password))
    encoded = base64.encodestring(raw)[:-1]
    headers['Authorization'] = 'Basic ' + encoded

    query_params = {
    }
    data = urllib.urlencode(query_params, True)
    url = url +"?" + data
    _LOG.info("Sending HTTP request to: %s:%s%s with headers:%s" % (host, port, url, headers))
    connection.request(method, url, body=None, headers=headers)

    response = connection.getresponse()
    response_body = response.read()
    if response.status != 200:
        _LOG.info("Response status '%s', '%s', '%s'" % (response.status, response.reason, response_body))
    if response.status == 200:
        response_body_raw = response_body
        response_body = json.loads(response_body_raw)
        if debug:
            print "Response: %s %s" % (response.status, response.reason)
            print "JSON: %s" % (json.dumps(response_body))
    return  response_body

    
    
     
