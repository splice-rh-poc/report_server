# Copyright © 2012 Red Hat, Inc.
#
# This software is licensed to you under the GNU General Public
# License as published by the Free Software Foundation; either version
# 2 of the License (GPLv2) or (at your option) any later version.
# There is NO WARRANTY for this software, express or implied,
# including the implied warranties of MERCHANTABILITY,
# NON-INFRINGEMENT, or FITNESS FOR A PARTICULAR PURPOSE. You should
# have received a copy of GPLv2 along with this software; if not, see
# http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt.

# Fetch data from various services

from report_server.common import config
import base64
import cStringIO
import logging
import httplib
import json
import pycurl
import urllib


_LOG = logging.getLogger(__name__)


class ApiClient:
    config.init()

    @staticmethod
    def get_all_rhics():
        c = config.get_rhic_serve_config_info()
        status, data = request(
            c['host'], c['port'], '/api/rhic/', c['user'], c['passwd'], False)
        if status == 200:
            return data
        raise Exception(status, data)

    @staticmethod
    def get_rhic(rhic_id):
        c = config.get_rhic_serve_config_info()
        api = '/api/rhic/503e31fdd9c1416fd0000003/'
        # status, data = request(c['host'], c['port'], api, c['user'],
        # c['passwd'], False)
        data = request(
            c['host'], c['port'], api, c['user'], c['passwd'], False)
        return data
        # if status == 200:
        #    return data
        # raise Exception(status, data)

    @staticmethod
    def get_account():
        c = config.get_rhic_serve_config_info()
        api = '/api/account/'
        # status, data = request(c['host'], c['port'], api, c['user'],
        # c['passwd'], False)
        data = request(
            c['host'], c['port'], api, c['user'], c['passwd'], False)
        return data

    @staticmethod
    def get_contract(api):
        c = config.get_rhic_serve_config_info()
        # status, data = request(c['host'], c['port'], api, c['user'],
        # c['passwd'], False)
        data = request(
            c['host'], c['port'], api, c['user'], c['passwd'], False)
        return data

    @staticmethod
    def get_rhic_details(RHIC):
        id = getRHICdata(RHIC)
        c = config.get_rhic_serve_config_info()
        if id:
            api = '/api/rhic/' + id + '/'
            # status, data = request(c['host'], c['port'], api, c['user'],
            # c['passwd'], False)
            data = request(
                c['host'], c['port'], api, c['user'], c['passwd'], False)
            return data

    @staticmethod
    def getRHIC_in_account():
        c = config.get_rhic_serve_config_info()
        api = '/api/account/'
        # status, data = request(c['host'], c['port'], api, c['user'],
        # c['passwd'], False)
        data = request(
            c['host'], c['port'], api, c['user'], c['passwd'], False)
        account_doc = data[0]
        print(account_doc)
        account_id = account_doc[0]['account_id']

        api = '/api/rhic/'
        data = request(
            c['host'], c['port'], api, c['user'], c['passwd'], False)
        # all_rhics = json.loads(data[0])
        all_rhics = data

        my_rhics = []
        for rhic in all_rhics:
            if rhic['account_id'] == account_id:
                my_rhics.append(rhic['uuid'])
        return my_rhics


def getRHICdata(RHIC):
    c = config.get_rhic_serve_config_info()

    api = '/api/rhic/'
    data = request(c['host'], c['port'], api, c['user'], c['passwd'], False)
    all_rhics = data
    # all_rhics = json.loads(data)

    my_rhics = []
    for rhic in all_rhics:
        if rhic['uuid'] == RHIC:
            return rhic['id']


def requestPyCurl(host, port, url, username, password, debug=False):
    buf = cStringIO.StringIO()
    URL = 'https://' + host + url
    USER = username
    PASS = password
    conn = pycurl.Curl()
    conn.setopt(pycurl.USERPWD, "%s:%s" % (USER, PASS))
    conn.setopt(pycurl.URL, URL)
    conn.setopt(pycurl.WRITEFUNCTION, buf.write)
    conn.perform()
    return buf


def request(host, port, url, username, password, debug=False):
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
    url = url + "?" + data
    _LOG.info("Sending HTTP request to: %s:%s%s with headers:%s" % (
        host, port, url, headers))
    connection.request(method, url, body=None, headers=headers)

    response = connection.getresponse()
    response_body = response.read()
    if response.status != 200:
        _LOG.info("Response status '%s', '%s', '%s'" % (
            response.status, response.reason, response_body))
    if response.status == 200:
        response_body_raw = response_body
        response_body = json.loads(response_body_raw)
        if debug:
            print "Response: %s %s" % (response.status, response.reason)
            print "JSON: %s" % (json.dumps(response_body))
    return  response_body
