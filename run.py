import time
import os

while(True):
    try:
        os.system("python main.py")
    except:
        print "some error"
    time.sleep(30)
