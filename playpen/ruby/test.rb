#!/usr/bin/ruby
require 'rubygems'
require 'mongo'

include Mongo

@client = MongoClient.new('localhost', 27017)
@db     = @client['results']
@coll   = @db['marketing_report_data']

space = "\n"*2
space

print "Print one object" << space
one = @coll.find_one
print one.to_s << space

print "Total number of objects in DB: " << @coll.count.to_s


