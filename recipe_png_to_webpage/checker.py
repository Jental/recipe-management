#!/usr/bin/python

import os
import urllib
from pyquery import PyQuery
import unicodedata
import re

in_dir = '/home/jental/Cook/Converted/'

def extract_nameparts(filename):
  name = os.path.splitext(filename)[0]
  parts = re.split("-|\||\\\\|/|\:", name)
  return [part.strip() for part in parts]

def fix_mht_u_characters(text):
  return urllib.parse.unquote(text.replace("\r", "").replace("=\n", "").replace("=", "%"))
def fix_mht_u_characters2(text):
  return ' '.join([fix_mht_u_characters(part) for part in text.split(' ')])

def check_title(filepath):
  if (os.path.isfile(filepath)):
    with open(filepath, 'r') as fh:
      html = fh.read()
      jQuery = PyQuery(html)

      jq_titles = jQuery('title')
      if len(jq_titles) > 0:
        title = fix_mht_u_characters2(jq_titles[0].text.strip())
        titleparts = extract_nameparts(title)
      else:
        title = ""
        titleparts = []
      nameparts = extract_nameparts(os.path.basename(filepath))[1:]
      intersection = list(set(titleparts) & set(nameparts))
      # print(title)
      # print(titleparts)
      # print(nameparts)
      # print(intersection)
      # exists = title in nameparts
      exists = len(intersection) * 2 > len(nameparts)
      if (exists):
        return True
      else:
        # print("-: check_title: part not found", title, nameparts)
        # print("-: check_title: part not found", "\n".join([line.strip() for line in jQuery('title').text().strip().split("\r\n")]), nameparts)
        # print(html)
        return False
  else:
    print("-: check_title: file not found")
    return False

# path = "/home/jental/Cook/Converted/crucide- Сельский хлеб.mht"
# path = "/home/jental/Cook/Converted/Mangiare e Bere - Свиная вырезка с ананасами, лимонной травой, красными апельсинами и розовыми патагонскими креветками.mht"
# path = "/home/jental/Cook/Converted/Из Италии с любовью - Быстрые маринованные баклажаны-Melanzane marinate.mht"
# path = "/home/jental/Cook/Converted/kitchen_nax- Захер от Шумахера в моём исполнении, или пока пекутся круассаны).mht"
# check = check_title(path)
# print(check)

correct = 0
incorrect = 0
for file in os.listdir(in_dir):
  path = os.path.join(in_dir, file)
  is_correct = check_title(path)
  if is_correct:
    correct = correct + 1
  else:
    incorrect = incorrect + 1
    print("Incorrect file: ", file)
print("Total correct  : ", correct)
print("Total incorrect: ", incorrect)
