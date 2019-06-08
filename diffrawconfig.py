#! /usr/bin/python3
#
# @(!--#) @(#) compareconfigs.py, version 001, 08-june-2019
#
# compare two raw_config.txt files extracted from a Raritan PDU
#

#################################################################

#
# imports
#

import sys
import os
import argparse

#################################################################

def readrawconfig(configfilename):
    global progname

    try:
        configfile = open(configfilename, 'r', encoding='utf-8')
    except IOError:
        print('{}: unable to open raw config file "{}" for reading'.format(configfilename), file=sys.stderr)
        sys.exit(0)

    config = {}

    linenumber = 0

    for line in configfile:
        linenumber += 1
        line = line.strip()
        if len(line) == 0:
            continue
        if line[0] == '#':
            continue

        equalsposition = line.find('=')

        if equalsposition == -1:
            print('{}: warning: line {} in config file "{}" does not contain an equals sign - ignoring'.format(progname, linenumber, configfilename), file=sys.stderr)
            continue

        key = line[0:equalsposition]
        value = line[equalsposition+1:]

        ### print('+++ {} +++ {} +++'.format(key, value))

        if key in config:
            print('{}: warning: the key "{}" in line {} in config file "{}" is a duplicate - ignoring'.format(progname, equalsposition, linenumber, configfilename), file=sys.stderr)
        else:
            config[key] = value

    configfile.close()

    if len(config) == 0:
        print('{}: warning: config file "{}" does not contain any keys - continuing'.format(progname, configfilename), file=sys.stderr)

    return config

#################################################################

def compareconfigs(first, second):
    diffs = {}

    index = 0

    # report keys in second config that are not in the first
    for key in second:
        if key not in first:
            diffs[index] = 'Key "{}" added\n  New value = "{}"'.format(key, second[key])
            index += 1

    # report keys in both that have a different value
    for key in first:
        if key in second:
            if first[key] != second[key]:
                diffs[index] = 'Key "{}" changed\n  Old value = "{}"\n  New value = "{}"'.format(key, first[key], second[key])
                index += 1

    # report keys in first config that are not on the second
    for key in first:
        if key not in second:
            diffs[index] = 'Key "{}" deleted\n  Old value = "{}"'.format(key, first[key])
            index += 1

    return diffs

#################################################################

def main():
    global progame

    parser = argparse.ArgumentParser()
        
    parser.add_argument('first',  help='name of first raw_config.txt file')
    parser.add_argument('second', help='name of second raw_config.txt file')

    args = parser.parse_args()

    firstfilename  = args.first
    secondfilename = args.second

    firstconfig = readrawconfig(firstfilename)

    secondconfig = readrawconfig(secondfilename)

    diffs = compareconfigs(firstconfig, secondconfig)

    numdiffs = len(diffs)

    if numdiffs == 0:
        retcode = 0
    else:
        for i in range(0, numdiffs):
            print(diffs[i])
        retcode = 1

    return retcode

#################################################################

progname = os.path.basename(sys.argv[0])

sys.exit(main())

# end of file
