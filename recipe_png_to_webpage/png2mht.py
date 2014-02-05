import os
import chilkat
import urllib.request
import urllib.parse

mht = chilkat.CkMht()
success = mht.UnlockComponent("Anything for 30-day trial")

proxy_support = urllib.request.ProxyHandler({"https" : "127.0.0.1:8118"})
opener = urllib.request.build_opener(proxy_support)

for filename in os.listdir("/home/jental/Cook/"):
  if filename.endswith(".png"):
    query = filename[:-18]
    newFileName = "/home/jental/dev/Cook/" + query + ".mht"
    if not os.path.isfile(newFileName):
      params = urllib.parse.urlencode({"q" : "!ducky " + query})
      try:
        handler = opener.open("https://duckduckgo.com/html/?%s" % params)
      except:
        print("Failed to execute a request: " + "https://duckduckgo.com/html/?%s" % params)
        continue
      foundUrl = handler.geturl()
      handler.close()
      print(foundUrl)
      # print(foundUrl)
      # mhtRes = mht.GetAndSaveMHT(foundUrl, u"/home/jental/dev/Cook/" + query + u".mht")
      mhtRes = mht.getMHT(foundUrl)
      # if mhtRes != True:
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
