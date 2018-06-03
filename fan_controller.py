import subprocess
import os
import sys
from datetime import datetime
import time
from logger import make_logger

LOGGER = make_logger(sys.stderr, "fan_control")

def main():

    delta = int(sys.argv[1])

    process = subprocess.Popen("DISPLAY=:0 XAUTHORITY=/var/run/lightdm/root/:0 nvidia-settings -a 'GPUFanControlState=1'", stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell=True)
    process.communicate()

    # while True:
    process = subprocess.Popen("nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader", stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell=True)
    output = process.communicate()[0]
    temperature_list = output.splitlines()

    process = subprocess.Popen("nvidia-smi --query-gpu=fan.speed --format=csv,noheader", stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell=True)
    output = process.communicate()[0]
    fan_speed_list = output.splitlines()


    for i, line in enumerate(temperature_list,0):
        gpu_temp = int(line.decode())
        recent_fan_speed = int(fan_speed_list[i].decode().strip().strip("%"))
        LOGGER.info("[STATUS]: GPU #{} Temperature = {}. Recent Fan Speed = {}".format(i, gpu_temp, recent_fan_speed))

        if gpu_temp <= 40:
            new_fan_speed = 35

        if gpu_temp > 40 and gpu_temp < 75:
            new_fan_speed = gpu_temp + delta
            new_fan_speed = min(new_fan_speed, 100)

        if gpu_temp >= 75:
            new_fan_speed = 100

        if abs(recent_fan_speed - new_fan_speed) <= 3:
            LOGGER.info("[NO_ACT]: GPU #{} Target Fan Speed = {}, Recent Fan Speed = {}".format(i, new_fan_speed, recent_fan_speed))
        else:
            process = subprocess.Popen("DISPLAY=:0 XAUTHORITY=/var/run/lightdm/root/:0 nvidia-settings -a \"[fan-{}]/GPUTargetFanSpeed={}\"".format(i, new_fan_speed), stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell=True)
            output, error = process.communicate()
            if output:
                LOGGER.info("[ACTION]: GPU #{} {}".format(i, output.decode().strip()))
            if error:
                LOGGER.critical("[ERROR]: GPU #{} {}".format(i, error.decode().strip()))

main()
