#!c:/Users/User/AppData/Local/Programs/Python/Python37-32/python.exe

import sys
import subprocess

python2_path = "C:\\Python27\\python.exe"
command = python2_path + " leapmotion.py"
process = subprocess.Popen(command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE,bufsize=2)
with process.stdout:
    print("nothing")
    for line in iter(process.stdout.readline, b''):
        print(line.decode())
