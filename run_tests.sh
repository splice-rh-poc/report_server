#!/bin/sh

# Run this script to execute all the unit tests for the ReportServer
#  or pass in a single argument of the TestCase class name to run just that class
#  Example:
#  $ ./run_tests.sh ImportAPITest



# Allows Splice configuration files to be override
export SPLICE_CONFIG="`pwd`/src/report_server/sreport/tests/test_data/splice_unittests.conf"
export DJANGO_SETTINGS_MODULE="dev.unit_test_settings"



TO_TEST="sreport"
if [ $# -ge 1 ]
then
TO_TEST=${TO_TEST}.$1
fi

pushd src/report_server/
python manage.py test ${TO_TEST} 

