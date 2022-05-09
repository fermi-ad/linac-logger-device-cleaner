#!/usr/bin/env python3

"""Helper file for filtering the linac_logger_devices file for unique requests"""

import glob
import os
from pathlib import Path
import re

re_loggers = re.compile(r'\s+Lina[c234]\s+')
re_device = re.compile(r'^\w[:|_]\w{1,14}\[*\d*\]*$')
COLUMN_WIDTH = 37
project_dir = Path('.')
input_dir = os.path.join(project_dir, 'output')
output_dir = os.path.join(project_dir, 'output')


def read_input():
    """Read the input file and return the contents

    Returns:
        list: The contents of the file
    """
    output = []
    for filepath in glob.glob(os.path.join(input_dir, 'linac_logger_devices.txt')):
        with open(filepath, encoding='utf8') as file:
            output = file.read().splitlines()
    return output


def write_output(filename, output):
    """Write the output to a file

    Args:
        filename (str): The name of the file to write to
        output (list): The output to write
    """
    with open(os.path.join(output_dir, filename), 'w+', encoding='utf8') as file:
        for line in output:
            file.write(line + '\n')


def main():
    """Orchestrate reading, processing, and writing"""
    devices_rates = read_input()
    unique_devices = list(set(devices_rates))
    print(len(unique_devices))

    write_output('linac_logger_unique_devices.txt', unique_devices)


if __name__ == "__main__":
    main()
