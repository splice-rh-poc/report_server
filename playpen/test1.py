
import base64
import httplib
import json
import logging
import time
import urllib


_LOG = logging.getLogger(__name__)

def test(host, port, url, username, password, debug=False):
    status, data = _request(host, port, url, username, password, debug)
    print "Data: %s" % (data)
    print "Status: %s" % (status)

def _request(host, port, url, username, password, debug=False):
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
    return response.status, response_body


if __name__ == "__main__":
    test(host="ec2-184-72-159-16.compute-1.amazonaws.com", port=443, url="/api/account/",
        username="shadowman@redhat.com", password="shadowman@redhat.com", debug=True)

