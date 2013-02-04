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


import os

#from splice.common import config
from report_server.settings import *

ROOT_URLCONF = 'dev.urls'

curr_dir = os.path.dirname(__file__)
source_dir = os.path.join(curr_dir, '..')
os.chdir(source_dir)

DUMP_DIR = os.path.join(curr_dir, 'db_dump')

TEMPLATE_DIRS = (
    os.path.join(source_dir, 'templates')
)

TEMPLATE_DEBUG = True
#DUMP_DIR='/home/whayutin/workspace/report_server/src/report_server/dev/db_dump/'
DUMP_DIR='/home/hudson/slave/workspace/report-server/src/report_server/dev/db_dump/'



### BEGIN ### ORIGINAL METERING SETTINGS

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    #'report_server.session.spacewalk.middleware.SpacewalkSessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

### END ### ORIGINAL METERING SETTINGS


### BEGIN ### SPACEWALK REPORT-SERVER SETTINGS
"""

SESSION_ENGINE = 'report_server.session.spacewalk.db'
#SESSION_ENGINE = 'django.contrib.sessions.backends.db

AUTHENTICATION_BACKENDS = (
   'report_server.auth.spacewalk.cookie.backends.SpacewalkBackend',
   'report_server.auth.spacewalk.credentials.backends.SpacewalkBackend',
   #'django.contrib.auth.backends.ModelBackend',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    #'django.contrib.sessions.middleware.SessionMiddleware',
    'report_server.session.spacewalk.middleware.SpacewalkSessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

DATABASES = {
   'default': {
              'ENGINE': 'django.db.backends.oracle', 
              'NAME': 'xe',                      
              'USER': 'spacewalk',               
              'PASSWORD': 'spacewalk',           
              'HOST': 'ec2-23-23-35-227.compute-1.amazonaws.com',
              'PORT': '1521',     
          }   
}
"""
### END ###SPACEWALK REPORT-SERVER SETTINGS


