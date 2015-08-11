#!/usr/bin/python

import sys
import re
from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client.eda
collection = db.default_values
ingrcollection = db.ingredients

iname = sys.argv[1]
print("Ingredient:", iname)
parts = re.split('\W+', iname)

patterns = [{'title' : re.compile(part, re.IGNORECASE)} for part in parts if part.strip() != '']
found = ingrcollection.find({'$and' : patterns})

if found.count() == 0:
  found = ingrcollection.find({'$or' : patterns})

if found.count() == 0:
  raise ValueError("Ingredient not found: \"", iname, "\". Please, specify id manually.")

print("Select ingredient [", iname ,"] num:")
foundl = list(found)
for (i, fingr) in enumerate(foundl):
  print(i, ":", fingr['title'])

choice = int(input().lower())
print("Selected", foundl[choice]['title'])

collection.insert({
  'type' : 'ingredient',
  'key'  : iname,
  'value': foundl[choice]['id']
})
