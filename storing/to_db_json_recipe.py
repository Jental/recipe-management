#!/usr/bin/python

import json
import sys
import os
import gridfs
import mimetypes
import requests
from pymongo import MongoClient
import itertools
import re

if len(sys.argv) < 2:
  print("Error: Specify input file")
  exit()

in_file = sys.argv[1]
if not os.path.isfile(in_file):
  print("Error: Input file does not exist")
  exit()

client = MongoClient('localhost', 27017)
db = client.eda
grid_fs = gridfs.GridFS(db)
collection = db.recipes
ingrcollection = db.ingredients

def add_image(image_url):
  gridfs_filename = image_url[image_url.rfind("/")+1:]
  if not grid_fs.exists({"filename" : gridfs_filename}):
    mime_type = mimetypes.guess_type(image_url)[0]
    r = requests.get(image_url, stream=True)

    _id = grid_fs.put(r.raw, contentType=mime_type, filename=gridfs_filename)
    print("created new gridfs file {0} with id {1}".format(gridfs_filename, _id))
    return _id
  else:
    _id = grid_fs.find_one({"filename": gridfs_filename})._id
    print("found gridfs file {0} with id {1}".format(gridfs_filename, _id))
    return _id

def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")

def process_images(jsobj):
  if 'images' in jsobj:
    for img in jsobj['images']:
      if isinstance(img, str):
        imgid = add_image(img)
        yield {
          'src' : img,
          'id' : imgid
        }
      elif 'src' in img:
        imgurl = img['src']
        imgid = add_image(imgurl)
        img['id'] = imgid
        yield img

def process_image(jsobj):
  if 'image' in jsobj and 'src' in jsobj['image']:
    imgurl = jsobj['image']['src']
    imgid = add_image(imgurl)
    yield {
      'src' : imgurl,
      'id' : imgid
    }

def process_instructions(jsobj):
  if 'instructions' in jsobj:
    for (i, instr) in enumerate(jsobj['instructions']):
      if isinstance(instr, str):
        yield {
          'id' : i,
          'text' : instr
        }
      else:
        iid = instr['id'] if 'id' in instr else i
        instr['id'] = iid

        images = process_images(instr)
        images2 = process_image(jsobj)
        instr['images'] = list(itertools.chain(images, images2))
        
        yield instr

def process_ingredients(jsobj):
  if 'ingredients' in jsobj:
    for ingr in jsobj['ingredients']:
      iname = ingr['name']
      if 'id' in ingr:
        yield ingr
      else:
        regx = re.compile(iname, re.IGNORECASE)
        found = ingrcollection.find({'title' : regx})
        if found.count() == 0:
          raise ValueError("Ingredient not found: \"", iname, "\". Please, specify id manually.")

        print("Select ingredient [", iname ,"] num:")
        foundl = list(found)
        for (i, fingr) in enumerate(foundl):
          print(i, ":", fingr['title'])

        choice = int(input().lower())
        print("Selected", foundl[choice]['title'])
        ingr['id'] = foundl[choice]['id']

        yield ingr

def process_notes(jsobj):
  if 'notes' in jsobj:
    for note in jsobj['notes']:
      if isinstance(note, str):
        yield {
          'text' : note
        }
      else:
        yield note

with open(in_file, 'r') as fh:
  jstext = fh.read()
  jsobj = json.loads(jstext)

  images = process_images(jsobj)
  images2 = process_image(jsobj)
  jsobj['images'] = list(itertools.chain(images, images2))

  instructions = process_instructions(jsobj)
  jsobj['instructions'] = list(instructions)

  ingredients = process_ingredients(jsobj)
  jsobj['ingredients'] = list(ingredients)

  notes = process_notes(jsobj)
  jsobj['notes'] = list(notes)

  if 'id' in jsobj:
    rid = jsobj['id']
    rcategory = jsobj['category'] if 'category' in jsobj else None

    dcount = collection.count({"id": rid, "category": rcategory})
    qres = query_yes_no("Found {0} old entries. Delete?".format(dcount))
    if qres:
      collection.delete_many({"id": rid, "category": rcategory}).deleted_count
      print("Deleted", dcount, "old entries")

  if 'title' in jsobj:
    rtitle = jsobj['title']
    dcount = collection.count({"title": rtitle})
    if dcount > 0:
      print("Warning. Found", dcount, "with the same title")

  collection.insert_one(jsobj)
