#!/bin/sh

# Run this script to execute all the unit tests for the ReportServer
#  or pass in a single argument of the TestCase class name to run just that class
#  Example:
#  $ ./run_tests.sh ImportAPITest


# Allows Splice configuration files to be override
export SPLICE_CONFIG="`pwd`/src/report_server/sreport/tests/test_data/splice_unittests.conf"

TO_TEST="sreport"
if [ $# -ge 1 ]
then
TO_TEST=${TO_TEST}.$1
fi

python src/report_server/manage.py test ${TO_TEST} 

