import os
import chilkat
from subprocess import call

mht = chilkat.CkMht()
success = mht.UnlockComponent("Anything for 30-day trial")

INPUT_DIR = "/home/jental/Cook/Converted"

for filename in os.listdir(INPUT_DIR):
  if filename.endswith(".mht"):
    f2 = open(INPUT_DIR + "/" + filename)
    text2 = f2.read()
    f2.close()
    mhtRes = mht.UnpackMHTString(text2, "/home/jental/tmp/", "/home/jental/tmp/out.html", "/home/jental/tmp/out")
    if (not mhtRes):
      print("Failed to open: ", filename)
    else:
      outFile = open("/home/jental/tmp/txts/" + filename + ".txt", "w");
      call(["elinks", "-dump", "/home/jental/tmp/out.html", "-dump-charset", "utf-8"], stdout=outFile)
      outFile.close()
