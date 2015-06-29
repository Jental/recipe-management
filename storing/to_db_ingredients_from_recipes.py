#!/usr/bin/python

import os
from pyquery import PyQuery
from pymongo import MongoClient
import json

ingridients_dir = '/home/jental/dev/eda_ru/eda.ru/wiki/ingredienty/'

client = MongoClient('localhost', 27017)
db = client.eda
icollection = db.ingredients
rcollection = db.recipes

for recipe in rcollection.find():
  if 'ingredients' in recipe:
    for ingr in recipe['ingredients']:
      if 'id' in ingr and 'name' in ingr:
        cnt = icollection.count({'id' : ingr['id']})
        if cnt == 0:
          ni = {
            'id': ingr['id'],
            'title' : ingr['name']
          }
          icollection.insert_one(ni)
