# Copyright 2012 Red Hat, Inc.
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

REPORT_CONFIG_DIR="/etc/splice/"
REPORT_CONFIG_FILE=os.path.join(REPORT_CONFIG_DIR, "report.conf")
hr_fmt = "%m%d%Y:%H"
mn_fmt = "%m%d%Y:%H%M"
day_fmt = "%Y%m%d"
max_fmt = "%m-%d"
full_format = "%a %b %d %H:%M:%S %Y"
just_date = "%m-%d-%Y"
jqplot_fmt = "%Y-%m-%d %I:%M%p"
month_day_year_fmt = "%m%d%Y"
epoch = "%s"

