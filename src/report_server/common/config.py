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

from splice.common.config import CONFIG
import ConfigParser
import logging


_LOG = logging.getLogger(__name__)


def get_rhic_serve_config_info():
    return {
        "host": CONFIG.get("rhic_serve", "host"),
        "port": CONFIG.get("rhic_serve", "port"),
        "user": CONFIG.get("rhic_serve", "username"),
        "passwd": CONFIG.get("rhic_serve", "password")
    }


def get_import_info():
    if CONFIG.get("import", "continue_on_error") is None:
        CONFIG.set("import", "continue_on_error", "0")
    return {
        "continue_on_error": CONFIG.get('import', 'continue_on_error'),
        'bulk_load': CONFIG.get('import', 'bulk_load')
    }


def get_nau():
    return {
        'calculation': CONFIG.get('nau', 'calculation')
    }
