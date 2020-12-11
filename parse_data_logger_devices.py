#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 10 15:02:04 2020
​
@author: snag
"""
import os
import glob
import re
import pathlib

lines = []
reg = '\s+Lina[c234]\s+'
column_width = 37
path = str(pathlib.Path(__file__).parent.absolute()) + '/data_logger_device_dump'

for filepath in glob.glob(os.path.join(path, '*.bin')):
    with open(filepath) as f:
        for line in f:
            stripped_line = line.strip()
            if len(stripped_line) != 0:
                for i in range(3):
                    stripped_column = line[i*column_width:i *
                                           column_width + column_width].strip()
                    column = re.split(reg, stripped_column)
                    if stripped_column != "":
                        lines.append(column)
print(lines)
