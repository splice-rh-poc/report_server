#!/usr/bin/python


import pymongo
from datetime import datetime
from pymongo import Connection
from pymongo import json_util

conn = Connection()
db = conn["checkin_service"]
collection = db["product"]

mystring = ""
for p in db.product.find():
	mystring = mystring + json_util.dumps(p)

print(mystring)
