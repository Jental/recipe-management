#!/usr/bin/python

import sys
import os
from pymongo import MongoClient
import gridfs
import mimetypes
import requests

client = MongoClient('localhost', 27017)
db = client.eda
grid_fs = gridfs.GridFS(db)

def remove_prefix(text, prefix):
  if text.startswith(prefix):
    return text[len(prefix):]
  return text

def add_image_url(image_url):
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

def add_image_file(filename):
  gridfs_filename = filename[filename.rfind("/")+1:]
  if not grid_fs.exists({"filename" : gridfs_filename}):
    mime_type = mimetypes.guess_type(filename)[0]
    print("Added")
    _id = grid_fs.put(open(filename, 'rb'), contentType=mime_type, filename=gridfs_filename)
    return _id
  else:
    print("Found")
    _id = grid_fs.find_one({"filename": gridfs_filename})._id
    return _id
  
if len(sys.argv) >= 2:
  path = remove_prefix(sys.argv[1], "file://");
  if os.path.isfile(path):
    res = add_image_file(path)
  else:
    res = add_image_url(path)
  print(res)
