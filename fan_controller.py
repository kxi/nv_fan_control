import subprocess
import os
import sys
import gspread
from datetime import datetime
import time


def main():

    delta = int(sys.argv[1])

    process = subprocess.Popen("nvidia-settings -a 'GPUFanControlState=1'", stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell=True)
    process.communicate()



    while True:
        process = subprocess.Popen("nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader", stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell=True)
        output = process.communicate()[0]

        for i, line in enumerate(output.splitlines(),0):
            gputemp = int(line.decode())
            print("[STATUS]: GPU #{} Temperature = {}".format(i, gputemp))

            if gputemp <= 40:
                newfanspeed = 0 + delta
            if gputemp > 40 and gputemp < 75:
                newfanspeed = gputemp + delta
            if gputemp >= 75:
                newfanspeed = 100

            process = subprocess.Popen("nvidia-settings -a \"[fan-{}]/GPUTargetFanSpeed={}\"".format(i, newfanspeed), stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell=True)
            output, error = process.communicate()
            if output:
                print("[ACTION]: {}".format(output.decode().strip()))
            if error:
                print("[ERROR]: {}".format(error.decode().strip()))

            time.sleep(1)

        time.sleep(4)
main()
