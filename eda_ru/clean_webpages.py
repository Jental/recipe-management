import os
from pyquery import PyQuery

in_dir = '/home/jental/dev/eda_ru/eda.ru/'
# in_dir = '/home/jental/dev/eda_ru/tmp/'

for cdir, dirs, files in os.walk(in_dir):
  for file in files:
    full_filename_b = os.path.join(cdir, file).encode("utf-8", "surrogateescape")
    try:
      full_filename = full_filename_b.decode("utf-8")
      print(full_filename)
      if full_filename.endswith(('.html', '.htm')):
        with open(full_filename, 'r') as fh:
          html = fh.read()

          jQuery = PyQuery(html)
          jQuery.remove('.ad-link')
        with open(full_filename, 'w') as fh:
          fh.write(jQuery("html").html())
    except:
      pass
