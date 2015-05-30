#!/usr/bin/python

import os
from pyquery import PyQuery
from pymongo import MongoClient
import json

ingridients_dir = '/home/jental/dev/eda_ru/eda.ru/wiki/ingredienty/'

client = MongoClient('localhost', 27017)
db = client.eda
collection = db.ingredients

for catname in next(os.walk(ingridients_dir))[1]:
  catdir = os.path.join(ingridients_dir, catname)
  for file in os.listdir(catdir):
    filename = os.path.join(catdir, file)
    try:
      if filename.endswith(('.html', '.htm')):
        print(filename.encode("utf-8", "surrogateescape"))
        with open(filename, 'r') as fh:
          html = fh.read()
          jQuery = PyQuery(html)

          id = os.path.splitext(file)[0]
          title = jQuery('h1.b-instrument-title').text()
          img   = jQuery('img.b-instrument-image').attr('src')
          desc  = jQuery('p.b-instrument-description').html()
          path  = os.path.join("wiki/ingredienty/", catname, file)

          print("- id   : ", id)
          print("- title: ", title)
          print("- image: ", img)
          print("- desc : ", desc)
          print("- path : ", path)

          found = collection.find_one({"id": id})
          if found == None:
            collection.insert_one({'id': id, 'title': title, 'image': img, 'description': desc, 'path': path})
          else:
            print('! found: ', found)
    except:
      pass
