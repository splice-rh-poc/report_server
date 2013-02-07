# Copyright  2012 Red Hat, Inc.
#
# This software is licensed to you under the GNU General Public
# License as published by the Free Software Foundation; either version
# 2 of the License (GPLv2) or (at your option) any later version.
# There is NO WARRANTY for this software, express or implied,
# including the implied warranties of MERCHANTABILITY,
# NON-INFRINGEMENT, or FITNESS FOR A PARTICULAR PURPOSE. You should
# have received a copy of GPLv2 along with this software; if not, see
# http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt.

# Django settings for report_server project.


from mongoengine import connect
from mongoengine.connection import register_connection


from splice.common import config
from splice.common.settings import *

from report_server.common.biz_rules import Rules

MONGO_DATABASE_NAME = config.CONFIG.get('report_server', 'db_name')
MONGO_DATABASE_HOST = config.CONFIG.get('report_server', 'db_host')
MONGO_DATABASE_NAME_CHECKIN = config.CONFIG.get('server', 'db_name')
MONGO_DATABASE_HOST_CHECKIN = config.CONFIG.get('server', 'db_host')
MONGO_DATABASE_NAME_RHICSERVE = config.CONFIG.get('rhic_serve', 'db_name')
MONGO_DATABASE_HOST_RHICSERVE = config.CONFIG.get('rhic_serve', 'db_host')

# Connect to the mongo databases.
connect(MONGO_DATABASE_NAME_CHECKIN, alias='checkin_service', tz_aware=True,
        host=MONGO_DATABASE_HOST_CHECKIN)
connect(MONGO_DATABASE_NAME_RHICSERVE, alias='rhic_serve', tz_aware=True,
        host=MONGO_DATABASE_HOST_RHICSERVE)
connect(MONGO_DATABASE_NAME, alias='results', tz_aware=True,
        host=MONGO_DATABASE_HOST)
register_connection('default', MONGO_DATABASE_NAME_RHICSERVE,
                    host=MONGO_DATABASE_HOST_RHICSERVE, tz_aware=True)

# Business Rules initialization
r = Rules()
r.init()
r.list_rules()


ROOT_URLCONF = 'report_server.splice_reports.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'splice_reports.wsgi.application'

TEMPLATE_DIRS = (
    '/usr/lib/report_server/templates',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'tastypie',
    'tastypie_mongoengine',
    'report_server.sreport',
    'report_server.report_import'
)

TEMPLATE_DEBUG = True

# If report-config has spacewalk 
if config.CONFIG.has_option('spacewalk', 'db_name'):
    #print('add the following to sqlnet.ora')
    #print('DIAG_ADR_ENABLED=OFF')
    #print('DIAG_DDE_ENABLED=FALSE')
    #print('DIAG_SIGHANDLER_ENABLED=FALSE')
    

    SESSION_ENGINE = 'report_server.session.spacewalk'
    
    AUTHENTICATION_BACKENDS = (
       'report_server.auth.spacewalk.cookie.backends.SpacewalkBackend',
       #'report_server.auth.spacewalk.credentials.backends.SpacewalkBackend',
       #'mongoengine.django.auth.MongoEngineBackend',
       #'django.contrib.auth.backends.ModelBackend',
    )
    
    MIDDLEWARE_CLASSES = (
        'django.middleware.common.CommonMiddleware',
        'report_server.session.spacewalk.middleware.SpacewalkSessionMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
    )
    
    
#spacewalk is not part of the report-server setup
else:
    AUTHENTICATION_BACKENDS = (
           'mongoengine.django.auth.MongoEngineBackend',
           #'django.contrib.auth.backends.ModelBackend',
        )    
    
    MIDDLEWARE_CLASSES = (
        'django.middleware.common.CommonMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
    )
    


