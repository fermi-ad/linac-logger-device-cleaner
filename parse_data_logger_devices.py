#!/usr/bin/env python3

import glob
import os
from pathlib import Path
import re

re_loggers = re.compile('\s+Lina[c234]\s+')
re_device = re.compile('^\w[:|_]\w{1,14}[\[\]\d]*$')
column_width = 37
project_dir = Path('.')
input_dir = os.path.join(project_dir, 'data_logger_device_dump')
output_dir = os.path.join(project_dir, 'output')


def read_input():
    output = []

    for filepath in glob.glob(os.path.join(input_dir, '*.bin')):
        with open(filepath) as f:
            output = parse_columns(f)

    return output


def parse_columns(input, column_count=3):
    output = []

    for line in input:
        stripped_line = line.strip()
        if len(stripped_line) != 0:
            for i in range(column_count):
                start = i * column_width
                end = i * column_width + column_width
                stripped_column = line[start:end].strip(' +*')
                column = re_loggers.split(stripped_column)

                if stripped_column != "":
                    output.append(column)

    return output


def get_column(input, column_index=0):
    output = []

    for line in input:
        output.append(line[column_index])

    return output


def validate_devices(input):
    output = []

    for device in input:
        if re_device.match(device):
            output.append(device)

    return output


def write_output(filename, output):
    with open(os.path.join(output_dir, filename), 'w+') as f:
        for line in output:
            f.write(line + '\n')


def main():
    devices_rates = read_input()
    devices = get_column(devices_rates)
    unique_devices = list(set(devices))
    valid_devices = validate_devices(unique_devices)

    write_output('linac_logger_unique_devices.txt', valid_devices)


if __name__ == "__main__":
    main()
