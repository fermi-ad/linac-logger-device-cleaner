#!/usr/bin/env python3

"""Transform acl logger rates to drf requests"""

import os
from pathlib import Path
import re

re_device_rate = re.compile(
    r'(\w[:|_]\w{1,14}\[*\d*\]*)\s+Lina[c234]\s+.*\s+\d+\s(.*)')
project_dir = Path('.')
input_file = os.path.join(project_dir, 'output', 'linac_logger_rates.txt')
output_dir = os.path.join(project_dir, 'output')


def read_input(filename):
    """Read the input file and return the contents

    Args:
        filename (str): The name of the file to read

    Returns:
        str: The contents of the file
    """
    with open(filename, encoding='utf8') as file:
        return file.read()


def drf(drf_list):
    """Transform the logger rates to drf requests

    Args:
        drf_list (list(tuple(str, str))): The list of devices and rates

    Returns:
        list: The drf requests
    """
    event_requests = []
    fastest = {}

    for (device, rate) in drf_list:
        # Append `.BIT_VALUE` for status requests
        # This is required to return the entire status word
        if device[1] == '|':
            device += '.BIT_VALUE'

        # Pass through event based rates.
        if rate.startswith('e'):
            event_requests.append(f'{device}@{rate}')
            continue

        # Before caching each device check the existing cache for a similar device
        if device in fastest:
            current_ms = int(rate.split(',')[1])
            existing_ms = int(fastest[device].split(',')[1])

            # If the device already exists, is the rate faster (lower)
            if current_ms < existing_ms:
                # Keep the fastest request
                fastest[device] = rate
        else:
            # If we haven't seen the device, add it to the dict.
            fastest[device] = rate

    periodic_requests = [f'{k}@{v}' for (k, v) in fastest.items()]
    output = event_requests + periodic_requests

    # Create a setting request ("_") for every reading request (":")
    for req in output:
        if req[1] == ':':
            output.append(req.replace(':', '_', 1).partition('@')[0])

    # Pass the output through a set to remove duplicates
    unique_output = list(set(output))
    # Sort the output by device name for easier reading and comparison
    unique_output.sort()

    return unique_output


def write_output(filename, output):
    """Write the output to a file

    Args:
        filename (str): The name of the file to write to
        output (list): The output to write to the file
    """
    with open(os.path.join(output_dir, filename), 'w+', encoding='utf8') as file:
        for line in output:
            file.write(line + '\n')


def main():
    """Read inputs and write final output."""
    raw_logger_rates = read_input(input_file)
    device_rates = re_device_rate.findall(raw_logger_rates)
    drfs = drf(device_rates)
    write_output('linac_logger_drf_requests.txt', drfs)


if __name__ == "__main__":
    main()
