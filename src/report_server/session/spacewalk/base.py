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
    """
    Base class for all Session classes.
    """
    TEST_COOKIE_NAME = 'testcookie'
    TEST_COOKIE_VALUE = 'worked'

    def __init__(self, session_id=None):
        self._session_id = session_id
        self.accessed = False
        self.modified = False

    def update(self, dict_):
        self._session.update(dict_)
        self.modified = True


    def clear(self):
        # To avoid unnecessary persistent storage accesses, we set up the
        # internals directly (loading data wastes time, since we are going to
        # set it to an empty dict anyway).
        self._session_cache = {}
        self.accessed = True
        self.modified = True

    def _get_new_session_key(self, web_user):
        "Returns session key that isn't being used."
        d = datetime.now + timedelta(day=1)        
        s = Session(web_user=web_user, expires=d.strftime('%s'))
        s.save()
        return s.id

    def _get_or_create_session_key(self, web_user):
        if self._session_id is None:
            self._session_id = self._get_new_session_key(web_user)
        return self._session_id

    def _get_session_key(self):
        return self._session_id

    session_key = property(_get_session_id)

    def _get_session(self, no_load=False):
        """
        Lazily loads session from storage (unless "no_load" is True, when only
        an empty dict is stored) and stores it in the current instance.
        """
        self.accessed = True
        try:
            return self._session_cache
        except AttributeError:
            if self.session_id is None or no_load:
                self._session_cache = {}
            else:
                self._session_cache = self.load()
        return self._session_cache

    _session = property(_get_session)

    def get_expiry_age(self):
        """Get the number of seconds until the session expires."""
        expiry = self.get('_session_expiry')
        if not expiry:   # Checks both None and 0 cases
            return settings.SESSION_COOKIE_AGE
        if not isinstance(expiry, datetime):
            return expiry
        delta = expiry - timezone.now()
        return delta.days * 86400 + delta.seconds

    def get_expiry_date(self):
        """Get session the expiry date (as a datetime object)."""
        expiry = self.get('_session_expiry')
        if isinstance(expiry, datetime):
            return expiry
        if not expiry:   # Checks both None and 0 cases
            expiry = settings.SESSION_COOKIE_AGE
        return timezone.now() + timedelta(seconds=expiry)

    def set_expiry(self, value):
        """
        Sets a custom expiration for the session. ``value`` can be an integer,
        a Python ``datetime`` or ``timedelta`` object or ``None``.

        If ``value`` is an integer, the session will expire after that many
        seconds of inactivity. If set to ``0`` then the session will expire on
        browser close.

        If ``value`` is a ``datetime`` or ``timedelta`` object, the session
        will expire at that specific future time.

        If ``value`` is ``None``, the session uses the global session expiry
        policy.
        """
        if value is None:
            # Remove any custom expiration for this session.
            try:
                del self['_session_expiry']
            except KeyError:
                pass
            return
        if isinstance(value, timedelta):
            value = timezone.now() + value
        self['_session_expiry'] = value

    def get_expire_at_browser_close(self):
        """
        Returns ``True`` if the session is set to expire when the browser
        closes, and ``False`` if there's an expiry date. Use
        ``get_expiry_date()`` or ``get_expiry_age()`` to find the actual expiry
        date/age, if there is one.
        """
        if self.get('_session_expiry') is None:
            return settings.SESSION_EXPIRE_AT_BROWSER_CLOSE
        return self.get('_session_expiry') == 0

    def flush(self):
        """
        Removes the current session data from the database and regenerates the
        key.
        """
        self.clear()
        self.delete()
        self.create()

    def cycle_key(self):
        """
        Creates a new session key, whilst retaining the current session data.
        """
        data = self._session_cache
        key = self.session_id
        self.create()
        self._session_cache = data
        self.delete(id)

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
