#!/usr/bin/env python3

import glob
import os
from pathlib import Path
import re

re_loggers = re.compile(r'\s+Lina[c234]\s+')
re_device = re.compile(r'^\w[:|_]\w{1,14}\[*\d*\]*$')
column_width = 37
project_dir = Path('.')
input_dir = os.path.join(project_dir, 'output')
output_dir = os.path.join(project_dir, 'output')

def read_input():
    output = []
    for filepath in glob.glob(os.path.join(input_dir, 'linac_logger_devices.txt')):
        with open(filepath) as f:
            output = f.read().splitlines()
    return output

def write_output(filename, output):
    with open(os.path.join(output_dir, filename), 'w+') as f:
        for line in output:
            f.write(line + '\n')

def main():
    devices_rates = read_input()
    unique_devices = list(set(devices_rates))
    print(len(unique_devices))

    write_output('linac_logger_unique_devices.txt', unique_devices)

if __name__ == "__main__":
    main()
