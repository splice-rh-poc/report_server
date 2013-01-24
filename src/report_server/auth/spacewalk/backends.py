from django.conf import settings
from django.contrib.auth.models import User, check_password
from report_server.sreport.models import WebContact, WebCustomer
from passlib.hash import md5_crypt

class SpacewalkBackend(object):
    """
    Authenticate against a spacwalk db

    Use the login name, and a hash of the password. For example:

    ADMIN_LOGIN = 'admin'
    ADMIN_PASSWORD = 'sha1$4e987$afbcf42e21bd417fb71db8c66b321e9fc33051de'
    """

    def authenticate(self, username=None, password=None):
        try:
            oracle_user = WebContact.objects.filter(login=username)[0]
            print(oracle_user.password)
            oracle_user_id = oracle_user.id
            passwd_to_match = oracle_user.password
            salt = oracle_user.password.split("$")[2]
            passwd_hash = md5_crypt.encrypt(password, salt=salt)
            
            if passwd_to_match == passwd_hash:
                try:
                    user = User.objects.get(username=username)
                except User.DoesNotExist:
                    # Create a new user. Note that we can set password
                    # to anything, because it won't be checked; the password
                    # from settings.py will.
                    user = User(username=username, password=password)
                    user.is_staff = False
                    user.is_superuser = False
                    user.save()
                return user
            return None
        except IndexError:
            _LOG.error('authentication failed, user does not exist in spacewalk')
            return None        

    def get_user(self, username):
        try:
            return User.objects.get(username=username)
        except User.DoesNotExist:
            return None