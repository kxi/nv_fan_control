import subprocess
import os
import sys
from datetime import datetime
import time
from logger import make_logger
import platform

LOGGER = make_logger(sys.stderr, "fan_control")


def main():

    if '18.04' in platform.version():
        NV_prefix = "sudo -s DISPLAY=:0 XAUTHORITY=/run/user/1000/gdm/Xauthority"
    if '20.04' in platform.version():
        NV_prefix = "sudo -s DISPLAY=:0 XAUTHORITY=/run/user/125/gdm/Xauthority"

    delta = int(sys.argv[1])

    process = subprocess.Popen(f"{NV_prefix} nvidia-settings -a 'GPUFanControlState=1'", stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell=True)
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
        LOGGER.info(f"[STATUS]: GPU #{i} Temperature = {gpu_temp}. Recent Fan Speed = {recent_fan_speed}")
        print(f"[STATUS]: GPU #{i} Temperature = {gpu_temp}. Recent Fan Speed = {recent_fan_speed}")

        if gpu_temp <= 40:
            new_fan_speed = 35

        if gpu_temp > 40 and gpu_temp < 75:
            new_fan_speed = gpu_temp + delta
            new_fan_speed = min(new_fan_speed, 100)

        if gpu_temp >= 75:
            new_fan_speed = 100

        if abs(recent_fan_speed - new_fan_speed) <= 3:
            LOGGER.info(f"[NO_ACT]: GPU #{i} Target Fan Speed = {new_fan_speed}, Recent Fan Speed = {recent_fan_speed}")
            print(f"[NO_ACT]: GPU #{i} Target Fan Speed = {new_fan_speed}, Recent Fan Speed = {recent_fan_speed}")

        else:
            process = subprocess.Popen(f"{NV_prefix} nvidia-settings -a \"[fan-{i}]/GPUTargetFanSpeed={new_fan_speed}\"", stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell=True)
            output, error = process.communicate()
            if output:
                LOGGER.info(f"[ACTION]: GPU #{i} {output.decode().strip()}")
                print(f"[ACTION]: GPU #{i} {output.decode().strip()}")
            if error:
                LOGGER.critical(f"[ERROR]: GPU #{i} {error.decode().strip()}")
                print(f"[ERROR]: GPU #{i} {error.decode().strip()}")

main()
