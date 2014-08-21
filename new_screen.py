#!/usr/bin/python
import subprocess

HORZ_RES=1920
VERT_RES=1080
HZ=50
LAPTOP_DISP="LVDS1"
OUTPUT="DVI1"
OUTPUT_LOCATION="--above"

cvt_output = subprocess.check_output(['cvt', str(HORZ_RES), str(VERT_RES), str(HZ)])
modeline = cvt_output.split("\n")[1].split()
resolution = modeline[1]
subprocess.call(['xrandr', '--newmode'] + modeline[1:])
subprocess.call(['xrandr', '--addmode', OUTPUT, resolution ])
subprocess.call(['xrandr', '--output', OUTPUT, '--mode', resolution])
subprocess.call(['xrandr', '--output', OUTPUT, OUTPUT_LOCATION, LAPTOP_DISP])
