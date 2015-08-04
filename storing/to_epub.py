#!/usr/bin/python

from ebooklib import epub
from pymongo import MongoClient
from bson.objectid import ObjectId
import re

def process_input(step, ingredients):
  links = [
    '<a href="ingredients.xhtml#ingredient_{id}">'.format(id = ingredients[int(inel['ingredient'])]['id']) if 'ingredient' in inel else '<a href="steps.xhtml#step_{id}">'.format(id = inel['output']) if 'output' in inel else '<a href="steps.xhtml#">'
    for inel in step['input']
  ] if 'input' in step else []
  return links

def process_step(step, ingredients):
  if not 'richtext' in step:
    return step['text']

  links = process_input(step, ingredients)

  rtext = step['richtext']
  p = re.compile("(<link:input num=[0-9]+>.*?</link>)")
  p2 = re.compile("<link:input num=([0-9]+)>(.*?)</link>")
  parts = [
    part if m == None else (links[int(m.group(1))] + m.group(2) + "</a>")
    for (m, part) in [(p2.match(part), part) for part in p.split(rtext)]
  ]
  return ''.join(parts)

# docid = '557e8f02335e015c8a6f1e2c'
docid = '55a389a9335e011ba201ab45'
client = MongoClient('localhost', 27017)
db = client.eda
collection = db.recipes
document = collection.find_one({"_id": ObjectId(docid)})
if document != None:
  book = epub.EpubBook()
  book.set_identifier(docid)
  book.set_title(document['title'])
  book.set_language('en')

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
        text = process_step(step, document['ingredients']))
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

  style = 'BODY {color: white;}'
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
