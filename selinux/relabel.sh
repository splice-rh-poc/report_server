#!/bin/sh

/sbin/restorecon -R /srv/report-server
/sbin/restorecon -R /etc/httpd/conf.d/report-server.conf
/sbin/restorecon -R /etc/splice
/sbin/restorecon -R /etc/init.d/report-server
/sbin/restorecon -R /var/log/report-server