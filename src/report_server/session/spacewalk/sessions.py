
from report_server.sreport.models import WebContact, WebCustomer

Class SpacewalkBackend(object):
    
    def read_cookies(cookies):

        PXT_SESSION = ""
        for key, value  in cookies.items():
            _LOG.info(key + ":" + value)
            if key == "pxt-session-cookie":
                PXT_SESSION = value
                _LOG.info('found pxt-session')