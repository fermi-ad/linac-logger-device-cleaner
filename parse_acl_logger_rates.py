#!/usr/bin/env python3

import os
from pathlib import Path
import re

re_device_rate = re.compile(
    r'(\w[:|_]\w{1,14}\[*\d*\]*)\s+Lina[c234]\s+.*\s+\d+\s(.*)')
project_dir = Path('.')
input_file = os.path.join(project_dir, 'output', 'linac_logger_rates.txt')
output_dir = os.path.join(project_dir, 'output')


def read_input(filename):
    with open(filename) as f:
        return f.read()


def drf(input):
    output = []

    for group in input:
        output.append(group[0] + '@' + group[1])

    return output


def write_output(filename, output):
    with open(os.path.join(output_dir, filename), 'w+') as f:
        for line in output:
            f.write(line + '\n')


def main():
    raw_logger_rates = read_input(input_file)
    device_rates = re_device_rate.findall(raw_logger_rates)
    drfs = drf(device_rates)
    write_output('linac_logger_drf_requests.txt', drfs)


if __name__ == "__main__":
    main()
