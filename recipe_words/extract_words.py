from nltk.tokenize import wordpunct_tokenize
import functools
import operator
import re
import os
import pymorphy2
from itertools import groupby
from subprocess import call

INPUT_DIR = "/home/jental/tmp/txts"
# INPUT_DIR = "/home/jental/tmp/txts2"
OUT_FILE = "/home/jental/tmp/outwords.txt"

morph = pymorphy2.MorphAnalyzer()
words = []

for filename in os.listdir(INPUT_DIR):
  if filename.endswith(".txt"):
    fileh = open(INPUT_DIR + "/" + filename)
    try:
      text = fileh.read()
    except:
      print("Read error: " + filename)
      fileh.close()
      continue
    fileh.close()
    
    words += functools.reduce(operator.add, [morph.parse(w)[:1] for w in wordpunct_tokenize(text) if len(w) >= 3], [])


# !!! Filtration
# normalized = [(p.normal_form, p.tag.POS) for p in words if not p.tag.POS is None]
# normalized = [(p.normal_form, p.tag.POS) for p in words if p.tag.POS == 'NOUN']
normalized = [(p.normal_form, p.tag.POS) for p in words if p.tag.POS == 'VERB' or p.tag.POS == 'INFN']

counted = [p for p in [(key, len(list(group))) for key, group in groupby(sorted(normalized))] if p[1] >= 10]
counted2 = sorted(counted, key = lambda c2 : c2[1], reverse = True)

ofileh = open(OUT_FILE, "w");
for p in counted2:
  ofileh.write("%s" % (p,))
  ofileh.write("\n")
ofileh.close()

# print(counted2)  
