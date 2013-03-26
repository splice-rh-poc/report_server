#!/usr/bin/python


import pymongo
from datetime import datetime
from pymongo import Connection

conn = Connection()
db = conn["checkin_service"]
collection = db["product"]

mystring = ""
for p in db.product.find():
	mystring = mystring + pymongo.json_util.dumps(p)

print(mystring)