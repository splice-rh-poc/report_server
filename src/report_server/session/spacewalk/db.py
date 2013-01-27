from django.conf import settings
from django.contrib.auth.models import User, check_password
from report_server.sreport.models import WebContact, WebCustomer
from report_server.sreport.models import Pxtsessions as Session
from passlib.hash import md5_crypt
from datetime import datetime

from django.contrib.sessions.backends.base import SessionBase, CreateError
from django.core.exceptions import SuspiciousOperation
from django.db import IntegrityError, transaction, router
from django.utils.encoding import force_unicode
from django.utils import timezone


class SessionStore(SessionBase):
    """
    Implements database session store.
    """
    def __init__(self, session_id=None):
        super(SessionStore, self).__init__(session_id)

    def load(self):
        try:
            s = Session.objects.get(
                session_id = self.session_id,
                expires__gt=datetime.now().strftime('%s')
            )
            return s.web_user
        except (Session.DoesNotExist, SuspiciousOperation):
            self.create()
            return {}

    def exists(self, session_id):
        return Session.objects.filter(session_id=session_id).exists()

    def create(self, web_user):
        while True:
            self._session_id = self._get_new_session_key(web_user)
            try:
                # Save immediately to ensure we have a unique entry in the
                # database.
                self.save(must_create=True)
            except CreateError:
                # Key wasn't unique. Try again.
                continue
            self.modified = True
            self._session_cache = {}
            return

    def save(self, must_create=False):
        """
        Saves the current session data to the database. If 'must_create' is
        True, a database error will be raised if the saving operation doesn't
        create a *new* entry (as opposed to possibly updating an existing
        entry).
        """
        obj = Session(
            session_key=self._get_or_create_session_key(),
            session_data=self.encode(self._get_session(no_load=must_create)),
            expire_date=self.get_expiry_date()
        )
        using = router.db_for_write(Session, instance=obj)
        sid = transaction.savepoint(using=using)
        try:
            obj.save(force_insert=must_create, using=using)
        except IntegrityError:
            if must_create:
                transaction.savepoint_rollback(sid, using=using)
                raise CreateError
            raise

    def delete(self, session_key=None):
        if session_key is None:
            if self.session_key is None:
                return
            session_key = self.session_key
        try:
            Session.objects.get(session_key=session_key).delete()
        except Session.DoesNotExist:
            pass


# At bottom to avoid circular import
from django.contrib.sessions.models import Session
