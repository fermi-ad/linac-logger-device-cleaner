import pandas as pd
import urllib
import time
import datetime
from dateutil import parser as dtpars
from urllib.request import urlopen
import argparse
from pathlib import Path
from io import StringIO

### Make a CLI argument parser
parser = argparse.ArgumentParser(description="usage: %prog [options] <haystack.txt> --needlefile \n")
### Add options
parser.add_argument ('haystackfile', default='linac_logger_drf_requests.txt',
                     help="[Path and] filename for DRF requests. (default: linac_logger_drf_requests.txt)")
parser.add_argument ('-v', dest='debug', action="store_true", default=False,
                     help="Turn on verbose debugging. (default: False)")
parser.add_argument ('--maxcount',  dest='maxcount', default=-1,
                     help="Number of devices in list to process. (default: -1 = all)")
parser.add_argument ('--outdir',  dest='outdir', default='',
                     help="Directory to write final output file. (default: pwd)")
parser.add_argument ('--needlefile',  dest='needle_filename', default='',
                     help="[Path and] file name of needles to be found in DRF requests (default: '')")
parser.add_argument ('--logfile',  dest='log_filename', default='',
                     help="[Path and] file name of logs to be found in DRF requests (default: '')")

### Get the options and argument values from the parser....
options = parser.parse_args()
DRF_file  = options.haystackfile
debug     = options.debug
maxcount  = int(options.maxcount)
outdir    = options.outdir
needle_filename = options.needle_filename
log_filename = options.log_filename

# Get the current directory of execution
abspath = Path().absolute()
current_dir = str(abspath)

if outdir == '': outdir = current_dir

print (f'\n__Analysis of DRF file {DRF_file}__')
# Mine the haystack file for the list of devices
haystack_devices = []
# Get the list of parameter names 
with open(DRF_file, 'r') as DRF_lines:
    for linecount, drf_line in enumerate(DRF_lines):
        if maxcount > 0 and linecount > maxcount: break
        drf_line = drf_line.strip()
        devicename = drf_line.split('@')[0] # The part before the @
        haystack_devices.append(devicename)

if debug: print ('List of DRF device names: ',haystack_devices)
print (f'There are {len(haystack_devices)} entries in device reference file.')
Zcount_haystack = sum(1 for devicename in haystack_devices if devicename.startswith('Z'))
print (f'({Zcount_haystack} starting with Z)')

# Process all the needles, even if it means finding each in the haystack
needle_df = {}
needles_found = []
needles_notfound = []
needles_notsettings = []
if needle_filename != '':
    needle_cols = ['device_name','description','location','station','comment','ignore']
    needle_df = pd.read_csv(needle_filename, skiprows=0, names=needle_cols)
    if debug: print (needle_df)
    needles_found = []
    for needle_i, needle_row in needle_df.loc[needle_df['ignore'] == '1'].iterrows():
        needle_name = needle_row[0]
        if len(needle_name)<1: continue
        if needle_name in haystack_devices:
            needles_found.append(needle_name)
            smush = ''
            for row_i, col in enumerate(needle_row):
                smush += ' '+str(col).casefold()
            if debug: print (smush)
            if smush.count('set') >= 0: 
                needles_notsettings.append(needle_name)
        else: needles_notfound.append(needle_name)
    print (f'\n__Analysis of proposed list to ignore from {needle_filename}:__')
    print (f'{len(needles_found)} devices marked "ignore" found.')
    Zcount_needles = sum(1 for devicename in needle_df.device_name if isinstance(devicename,str) and devicename.startswith('Z'))
    print (f'({Zcount_needles} starting with Z)')
    print (f'\--> {len(needles_notsettings)} devices marked "ignore" and which have "set" in their row somewhere')
    Zcount_NonSetneedles = sum(1 for devicename in needles_notsettings if isinstance(devicename,str) and devicename.startswith('Z'))
    print (f'({Zcount_NonSetneedles} starting with Z)')

# Process the log file, if specified.
ACNET_NOT_FOUND = 'Status reply [16 -13]'
device_error_tallies = {}
device_error_tally_Z = 0

if log_filename != '':
    ACNET_error_file = open('ACNET_no_such_property.txt', 'w')
    with open(log_filename, 'r') as logfile:
        for logline_i, log_line in enumerate(logfile):
            if maxcount > 0 and logline_i > maxcount: break
            logline = log_line.strip()
            if logline.count(ACNET_NOT_FOUND) > 0:
                # Extract the last word, hopefully a device name
                logdevice = logline.split(' ')[-1]
                if logdevice not in device_error_tallies.keys():
                    ACNET_error_file.write(logdevice+'\n')
                    device_error_tallies[logdevice] = 1
                    if logdevice.startswith('Z'): device_error_tally_Z += 1
                else: device_error_tallies[logdevice] += 1
    # Summarize some analysis of the devices garnering these error codes
    ACNET_error_file.close()
    print (f'\n__Analysis of nanny log file__ :')
    # Sort by tallies, highest to lowest
    device_error_tallies = dict(sorted(device_error_tallies.items(), key=lambda item: item[1], reverse=True))

    # OK, I should have done this in a Pandas dataframe.  I'm sorry.
    # Make a list of devices having each error count
    errorcounts_dict = {}
    for logdevice, errorcount in device_error_tallies.items():
        if not errorcount in errorcounts_dict.keys(): errorcounts_dict[errorcount] = []
        errorcounts_dict[errorcount].append(logdevice)
    # Output a digest of the error counts and how many devices have each error count
    for errorcount, devicelist in  errorcounts_dict.items():
        ErrorDevices_haystack = sum(1 for errordevicename in devicelist if errordevicename in haystack_devices)
        print (f'{len(devicelist)} devices in the logger file EACH had {errorcount} instances of "{ACNET_NOT_FOUND}".')
        print (f'({device_error_tally_Z} devices with {ACNET_NOT_FOUND} begin with Z)')
        print (f'   and {ErrorDevices_haystack} of these device names were found in {DRF_file}')
        if needle_filename != '':
            ErrorDevices_needlestack = sum(1 for errordevicename in devicelist if errordevicename in needles_found)
            print (f'    and {ErrorDevices_needlestack} devices with this error code were found in {needle_filename}')

proposed_to_drop = []
# Generate a suggested, edited DRF file, and a summary table
AllGood                                   = []
ZDevices___________                       = []
NonSettingsToIgnore                       = []
NoSuchProperty16_13                       = []
ZDevices___________ANDNonSettingsToIgnore = []
ZDevices___________ANDNoSuchProperty16_13 = []
NonSettingsToIgnoreANDNoSuchProperty16_13 = []
ZDevices___________ANDNonSettingsToIgnoreANDNoSuchProperty16_13 = []
devicestodrop = []
uncounted = 0
with open(DRF_file, 'r') as DRF_lines, open(DRF_file+'NEW', 'w') as newfile:
    for linecount, drf_line in enumerate(DRF_lines):
        if maxcount > 0 and linecount > maxcount: break
        drf_line = drf_line.strip()
        devicename = drf_line.split('@')[0] # The part before the @
        if devicename.startswith('Z') or devicename in needles_notsettings or devicename in device_error_tallies.keys():
            devicestodrop.append(devicename)
        if   (not devicename.startswith('Z')) and (not devicename in needles_notsettings) and (not devicename in device_error_tallies.keys()):
            AllGood.append(devicename)
            newfile.write(drf_line+'\n')
        # Single-list badness
        elif (    devicename.startswith('Z')) and (not devicename in needles_notsettings) and (not devicename in device_error_tallies.keys()):
            ZDevices___________.append(devicename)
        elif (not devicename.startswith('Z')) and (    devicename in needles_notsettings) and (not devicename in device_error_tallies.keys()):
            NonSettingsToIgnore.append(devicename)
        elif (not devicename.startswith('Z')) and (not devicename in needles_notsettings) and (    devicename in device_error_tallies.keys()):
            NoSuchProperty16_13.append(devicename)
        # Double-list badness
        elif (    devicename.startswith('Z')) and (    devicename in needles_notsettings) and (not devicename in device_error_tallies.keys()):
            ZDevices___________ANDNonSettingsToIgnore.append(devicename)
        elif (    devicename.startswith('Z')) and (not devicename in needles_notsettings) and (    devicename in device_error_tallies.keys()):
            ZDevices___________ANDNoSuchProperty16_13.append(devicename)
        elif (not devicename.startswith('Z')) and (    devicename in needles_notsettings) and (    devicename in device_error_tallies.keys()):
            NonSettingsToIgnoreANDNoSuchProperty16_13.append(devicename)
        # Triple bad
        elif (    devicename.startswith('Z')) and (    devicename in needles_notsettings) and (    devicename in device_error_tallies.keys()):
            ZDevices___________ANDNonSettingsToIgnoreANDNoSuchProperty16_13.append(devicename)
        else: uncounted += 1
    # Close the loop over DRF file lines.
    newfile.close()

print ('__Summary__')
print ('\n DeviceCount  | ZDevices___________ | NonSettingsToIgnore | NoSuchProperty16_13 |')
print (' {: >5}        |                     |                     |                     | <-- All Good'.format(len(AllGood                                  )))
print (' {: >5}        |        Y            |                     |                     |'.format(len(ZDevices___________                      )))
print (' {: >5}        |                     |         Y           |                     |'.format(len(NonSettingsToIgnore                      )))
print (' {: >5}        |                     |                     |          Y          |'.format(len(NoSuchProperty16_13                      )))
print (' {: >5}        |        Y            |         Y           |                     |'.format(len(ZDevices___________ANDNonSettingsToIgnore)))
print (' {: >5}        |        Y            |                     |          Y          |'.format(len(ZDevices___________ANDNoSuchProperty16_13)))
print (' {: >5}        |                     |         Y           |          Y          |'.format(len(NonSettingsToIgnoreANDNoSuchProperty16_13)))
print (' {: >5}        |        Y            |         Y           |          Y          |'.format(len(ZDevices___________ANDNonSettingsToIgnoreANDNoSuchProperty16_13)))
print (f'Devices unaccounted for above: {uncounted}.')

print (f'\nSUMMARY: Dropping {len(devicestodrop)} (union of all disqualifying lists) should eliminate from the present {len(haystack_devices)}')
print (f' {len(ZDevices___________)+len(ZDevices___________ANDNonSettingsToIgnore)+len(ZDevices___________ANDNonSettingsToIgnoreANDNoSuchProperty16_13)} total Z devices,')
print (f' {len(needles_notsettings)} devices we think we should ignore anyway, and')
print (f' {len(device_error_tallies.keys())} devices which reliably give {ACNET_NOT_FOUND} in the nanny log.')
print (f'The resulting {DRF_file} would be {len(AllGood)} devices')
