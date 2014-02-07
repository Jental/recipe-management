import os
import chilkat
import urllib.request
import urllib.parse

INPUT_DIR = "/home/jental/Cook/"
OUTPUT_DIR = "/home/jental/tmp/Cook/"
REQUEST_URL = "https://duckduckgo.com/html/?%s"

if (not os.path.isfile(OUTPUT_DIR)) and (not os.path.isdir(OUTPUT_DIR)):
  os.mkdir(OUTPUT_DIR)

mht = chilkat.CkMht()
success = mht.UnlockComponent("Anything for 30-day trial")
if not success:
  exit()

proxy_support = urllib.request.ProxyHandler({"https" : "127.0.0.1:8118"}) # Privoxy
opener = urllib.request.build_opener(proxy_support)

for filename in os.listdir(INPUT_DIR):
  if filename.endswith(".png"):
    query = filename[:-18]
    newFileName = OUTPUT_DIR + "/" + query + ".mht"
    if not os.path.isfile(newFileName):
      params = urllib.parse.urlencode({"q" : "!ducky " + query})
      try:
        handler = opener.open(REQUEST_URL % params)
      except:
        print("Failed to execute a request: " + REQUEST_URL % params)
        continue
      foundUrl = handler.geturl()
      handler.close()
      print(foundUrl)
      # print(foundUrl)
      mhtRes = mht.getMHT(foundUrl)
      if mhtRes == None:
        try:
          print("Failed to download: ", foundUrl, mht.lastErrorText)
        except:
          print("Failed to download: ", foundUrl)
          pass
      else:
        file = open(newFileName, "w")
        file.write(mhtRes)
        file.close()
    else:
      print("File " + newFileName + " already exists")
