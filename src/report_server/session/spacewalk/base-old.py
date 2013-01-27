from datetime import datetime
from datetime import timedelta
from django.contrib.sessions.backends.base import SessionBase
from report_server.sreport.models import Pxtsessions as Session


class CreateError(Exception):
    """
    Used internally as a consistent exception type to catch from save (see the
    docstring for SessionBase.save() for details).
    """
    pass

class SessionBase(SessionBase):
    

    # Methods that child classes must implement.

    def exists(self, session_id):
        """
        Returns True if the given session_key already exists.
        """
        raise NotImplementedError

    def create(self):
        """
        Creates a new session instance. Guaranteed to create a new object with
        a unique key and will have saved the result once (with empty data)
        before the method returns.
        """
        raise NotImplementedError

    def save(self, must_create=False):
        """
        Saves the session data. If 'must_create' is True, a new session object
        is created (otherwise a CreateError exception is raised). Otherwise,
        save() can update an existing object with the same key.
        """
        raise NotImplementedError

    def delete(self, session_key=None):
        """
        Deletes the session data under this key. If the key is None, the
        current session key value is used.
        """
        raise NotImplementedError

    def load(self):
        """
        Loads the session data and returns a dictionary.
        """
        raise NotImplementedError
