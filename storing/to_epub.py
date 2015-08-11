#!/usr/bin/python

from ebooklib import epub
from pymongo import MongoClient
from bson.objectid import ObjectId
import re
import gridfs
import mimetypes
import requests
import sys

# docid = '557e8f02335e015c8a6f1e2c'
# docid = '55a389a9335e011ba201ab45'
# docid = '559e1b72335e015f6552fbc2'
# docid = '55c85404335e014d115529d6'
if (len(sys.argv) > 1) and not sys.argv[len(sys.argv) - 1].startswith("--"):
  docid = sys.argv[len(sys.argv) - 1]
else:
  docid = '55a389a9335e011ba201ab45'

def process_input(step, ingredients):
  links = [
    '<a href="ingredients.xhtml#ingredient_{id}">'.format(id = ingredients[int(inel['ingredient'])]['id']) if 'ingredient' in inel else '<a href="steps.xhtml#step_{id}">'.format(id = inel['output']) if 'output' in inel else '<a href="steps.xhtml#">'
    for inel in step['input']
  ] if 'input' in step else []
  return links

def process_step(step, ingredients):
  if not 'richtext' in step:
    if 'text' in step:
      return step['text']
    else:
      return ''

  links = process_input(step, ingredients)

  rtext = step['richtext']
  p = re.compile("(<link:input num=[0-9]+>.*?</link>)")
  p2 = re.compile("<link:input num=([0-9]+)>(.*?)</link>")
  parts = [
    part if m == None else (links[int(m.group(1))] + m.group(2) + "</a>")
    for (m, part) in [(p2.match(part), part) for part in p.split(rtext)]
  ]
  return ''.join(parts)

def process_step_image(imageData, book):
  iid = None
  if isinstance(imageData, str):
    if '--process-links' in sys.argv:
      print("image: downloading:", imageData)
      
      icontentType = mimetypes.guess_type(imageData)[0]
      ifilename = imageData[imageData.rfind("/")+1:]
      iid = ifilename
      icontent = requests.get(imageData, stream=True).raw.read()
  else:
    print("image: from db: id: ", imageData['id'])
    
    imageId = imageData['id']
    imageObj = grid_fs.get(imageId)

    ifilename = imageObj.filename
    icontentType =  imageObj.contentType
    iid = str(imageObj._id)
    icontent = imageObj.read()

  if iid != None:
    ei = epub.EpubImage()
    ei.id = iid
    ei.file_name = ifilename
    ei.media_type = 'image/jpeg' if (icontentType == None) else icontentType
    ei.content = icontent

    print("image: filename:", ifilename)
    print("image: content-type:", icontentType)

    return (ei, '<img src="{src}" />'.format(src = ifilename))
  else:
    print("image: unprocessed:", imageData)

    return (None, '')

def process_step_images(step, book):
  parts = []
  
  if 'images' in step:
    for imageData in step['images']:
      (obj, part) = process_step_image(imageData, book)
      if obj != None:
        parts.append(part)
        book.add_item(obj)

  if 'image' in step:
    (obj, part) = process_step_image(step['image'], book)
    if obj != None:
      parts.append(part)
      book.add_item(obj)

  return parts

client = MongoClient('localhost', 27017)
db = client.eda
collection = db.recipes
grid_fs = gridfs.GridFS(db)
document = collection.find_one({"_id": ObjectId(docid)})
if document != None:
  book = epub.EpubBook()
  book.set_identifier(docid)
  book.set_title(document['title'])
  book.set_language('en')

  print("title:", document['title'])

  cIntro = epub.EpubHtml(title='Intro', file_name='intro.xhtml', lang='en')
  with open('templates/epub/intro.tpl', 'r') as template_file:
    cIntro_template = template_file.read()
    cIntro.content = cIntro_template.format(
      title = document['title'],
      src   = document['src'] if 'src' in document else '',
      cat   = document['category'],
      tags  = ', '.join(document['tags']))
  book.add_item(cIntro)

  cIngredients = epub.EpubHtml(title='Ingredients', file_name='ingredients.xhtml', lang='en')
  with open('templates/epub/ingredients.tpl', 'r') as template_file, open('templates/epub/ingredient.tpl', 'r') as template_file_1:
    cIngredients_template = template_file.read()
    cIngredient_template = template_file_1.read()
    cIngredient_parts = [
      cIngredient_template.format(
        id     = ingr['id'],
        name   = ingr['name'],
        amount = ingr['amount'])
      for ingr in document['ingredients']
    ]
    cIngredients.content = cIngredients_template.format(
      ingredients  = '\n'.join(cIngredient_parts))
  book.add_item(cIngredients)

  cSteps = epub.EpubHtml(title='Instructions', file_name='steps.xhtml', lang='en')
  with open('templates/epub/steps.tpl', 'r') as template_file, open('templates/epub/step.tpl', 'r') as template_file_1:
    cSteps_template = template_file.read()
    cStep_template = template_file_1.read()
    
    cStep_parts = [
      cStep_template.format(
        id   = step['id'],
        text = process_step(step, document['ingredients']),
        images = '\n'.join(process_step_images(step, book)))
      for step in document['instructions']
    ]
    cSteps.content = cSteps_template.format(
      steps  = '\n'.join(cStep_parts))
  book.add_item(cSteps)

  book.toc = (epub.Link('intro.xhtml', 'Intro', 'intro'),
              epub.Link('ingredients.xhtml', 'Ingredients', 'ingredients'),
              epub.Link('steps.xhtml', 'Instructions', 'steps'))

  book.add_item(epub.EpubNcx())
  book.add_item(epub.EpubNav())

  style = """
body {
  color: white;
}
.step {
  page-break-before: always;
}
"""
  nav_css = epub.EpubItem(
    uid="style_nav",
    file_name="style/nav.css",
    media_type="text/css",
    content=style)
  book.add_item(nav_css)

  book.spine = ['nav', cIntro, cIngredients, cSteps]

  epub.write_epub('test.epub', book, {})
else:
  print("Recipe with _id={0} not found".format(docid))
