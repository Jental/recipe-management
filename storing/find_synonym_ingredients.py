#!/usr/bin/python

from pymongo import MongoClient
import re

client = MongoClient('localhost', 27017)
db = client.eda
collection = db.ingredients

count = 0
for ingredient in collection.find():
  if not 'title' in ingredient:
    print('Warning: no title: ', ingredient['id'])
    continue
  
  inameparts = re.split('\W+', ingredient['title'])
  patterns = [{'title' : re.compile(part, re.IGNORECASE)} for part in inameparts if part.strip() != '']
  found = collection.find({'$and' : patterns})

  if found.count() <= 1:
    # only self found
    continue

  count = count + 1

  print("{title} ({id})".format(
    title = ingredient['title'],
    id    = ingredient['id']
  ))
  for fingr in found:
    if fingr['_id'] != ingredient['_id']:
      print("\t{title} ({id})".format(
        title = fingr['title'],
        id    = fingr['id']
      ))

print("\nTotal: ", count)
