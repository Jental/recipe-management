#!/usr/bin/python

import os
from pyquery import PyQuery
from pymongo import MongoClient
import json
import gridfs
import mimetypes
import requests

root_dir = '/home/jental/dev/eda_ru/eda.ru/'
log_level = 1

recipe_dirs = [
  'bouillon',
  'breakfast',
  'recipe',
  'desserts',
  'drinks',
  'main_course',
  'paste',
  'risotto',
  'salad',
  'sandwiches',
  'sauce',
  'snack',
  'soups'
]

client = MongoClient('localhost', 27017)
db = client.eda
grid_fs = gridfs.GridFS(db)
collection = db.recipes

def remove_prefix(text, prefix):
  if text.startswith(prefix):
    return text[len(prefix):]
  return text

def remove_suffix(text, suffix):
  if text.endswith(suffix):
    return text[:-len(suffix)]
  return text

def add_image(image_url):
  gridfs_filename = image_url[image_url.rfind("/")+1:]
  if not grid_fs.exists({"filename" : gridfs_filename}):
    mime_type = mimetypes.guess_type(image_url)[0]
    r = requests.get(image_url, stream=True)

    _id = grid_fs.put(r.raw, contentType=mime_type, filename=gridfs_filename)
    if log_level >= 2:
      print("created new gridfs file {0} with id {1}".format(gridfs_filename, _id))
    return _id
  else:
    _id = grid_fs.find_one({"filename": gridfs_filename})._id
    if log_level >= 2:
      print("found gridfs file {0} with id {1}".format(gridfs_filename, _id))
    return _id

def process_recipe(filename, rd, category):
  if log_level >= 2:
    print(filename.encode("utf-8", "surrogateescape"))
  if os.path.isfile(filename):
    with open(filename, 'r') as fh:
      html = fh.read()
      jQuery = PyQuery(html)

      id = remove_prefix(rd, 'recipe')
      title = jQuery('h1.s-recipe-name').text()
      img   = jQuery('img.photo').attr('src')
      # path  = os.path.join(recipes_dir, rd, 'index.html')
      path = filename
      jq_ingredients = jQuery('.b-ingredients-list .ingredient');
      ingredients = [(jQuery(jq_ing).attr('data-id'), jQuery('.name', jq_ing).text(), jQuery('.amount', jq_ing).text()) for jq_ing in jq_ingredients]
      time = jQuery('.b-directions .duration time').text();
      jq_instructions = jQuery('.b-directions .instructions .instruction')
      instructions = [jQuery(jq_instr).text() for jq_instr in jq_instructions];
      notes = [jQuery('.b-directions .note').text()]
      tags = [category]

      found = collection.find_one({"id": id, "category": category})
      if log_level >= 1:
        if collection.count({"id": id}) >= 2:
          print("! multiple equal ids: ", id)
      if found == None:
        if log_level >= 1:
          if collection.count({"id": id}) >= 1:
            print("! multiple equal ids: ", id)
          if log_level == 1:
            print(filename.encode("utf-8", "surrogateescape"))
          print("- id   : ", id)
          print("- title: ", title)
          print("- image: ", img)
          print("- path : ", path)
          print("- ingredients : ")
          for ing in ingredients:
            print("--- : ", ing)
          print("- time: ", time)
          print("- instructions : ")
          for instr in instructions:
            print("--- : ", instr)
          print("- notes : ")
          for note in notes:
            print("--- : ", note)
          print("- tags : ")
          for tag in tags:
            print("--- : ", tag)

        if img is not None:
          img_id = add_image(img)
        else:
          img_id = None
        collection.insert_one({
          'id': id,
          'title': title,
          'image': {
            'id': img_id,
            'src': img
          },
          'description': '',
          'path': path,
          'ingredients': [{'id': i_id, 'name' : i_name, 'amount': i_amount} for (i_id, i_name, i_amount) in ingredients],
          'time': time,
          'instructions': instructions,
          'notes': notes,
          'category': category,
          'tags': tags
        })
      else:
        if log_level >= 3:
          print('! found: ', found)
        elif log_level >= 2:
          print('! found')
        
  else:
    if log_level >= 1:
      print("- Error. File not found")

for recipes_dir in recipe_dirs:
  recipes_dir_fp = os.path.join(root_dir, recipes_dir)
  if log_level >= 1:
    print("category: ", recipes_dir)
# - <category>/recipe<id>/*.html
  for rd in next(os.walk(recipes_dir_fp))[1]:
    for file in os.listdir(os.path.join(recipes_dir_fp, rd)):
      if file.endswith(".html") or file.endswith(".htm"):
        filepath = os.path.join(recipes_dir_fp, rd, file)
        process_recipe(filepath, rd, recipes_dir)
# - <category>/recipe<id>.html
  for rf in os.listdir(recipes_dir_fp):
    if rf.endswith(".html") or rf.endswith(".htm"):
      filepath = os.path.join(recipes_dir_fp, rf)
      rf2 = remove_suffix(remove_suffix(rf, ".html"), ".htm")
      process_recipe(filepath, rf2, recipes_dir)
# - <category>/recipe/<id>/index.html
  recipes_dir_recipe = os.path.join(root_dir, recipes_dir, "recipe")
  if os.path.isdir(recipes_dir_recipe):
    for rd in next(os.walk(recipes_dir_recipe))[1]:
      for file in os.listdir(os.path.join(recipes_dir_recipe, rd)):
        if file.endswith(".html") or file.endswith(".htm"):
          filepath = os.path.join(recipes_dir_fp, "recipe", rd, file)
          process_recipe(filepath, rd, recipes_dir)
# - recipe<id>/*.html
for rd in next(os.walk(root_dir))[1]:
  if rd.startswith("recipe"):
    for file in os.listdir(os.path.join(root_dir, rd)):
      if file.endswith(".html") or file.endswith(".htm"):
        filepath = os.path.join(root_dir, rd, file)
        process_recipe(filepath, rd, "")
