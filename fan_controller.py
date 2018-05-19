import subprocess
import os
import sys
from datetime import datetime
import time
from logger import make_logger

LOGGER = make_logger(sys.stderr, "fan_control")

def main():

    delta = int(sys.argv[1])

    # process = subprocess.Popen("DISPLAY=:0 XAUTHORITY=/var/run/lightdm/root/:0 nvidia-settings -a 'GPUFanControlState=1'", stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell=True)
    # process.communicate()



    # while True:
    process = subprocess.Popen("nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader", stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell=True)
    output = process.communicate()[0]

    for i, line in enumerate(output.splitlines(),0):
        gputemp = int(line.decode())
        LOGGER.info("[STATUS]: GPU #{} Temperature = {}".format(i, gputemp))

        if gputemp <= 40:
            newfanspeed = 35

        if gputemp > 40 and gputemp < 75:
            newfanspeed = gputemp + delta
            newfanspeed = min(newfanspeed, 100)

        if gputemp >= 75:
            newfanspeed = 100


        process = subprocess.Popen("DISPLAY=:0 XAUTHORITY=/var/run/lightdm/root/:0 nvidia-settings -a \"[fan-{}]/GPUTargetFanSpeed={}\"".format(i, newfanspeed), stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell=True)
        output, error = process.communicate()
        if output:
            LOGGER.info("[ACTION]: {}".format(output.decode().strip()))
        if error:
            LOGGER.critical("[ERROR]: {}".format(error.decode().strip()))

main()
