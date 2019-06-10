#! /usr/bin/python3
#
# @(!--#) @(#) compareconfigs.py, version 006, 07-june-2019
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
import html
import cgi
import cgitb; cgitb.enable()  # for troubleshooting

#################################################################

DEFAULT_FIRST_FILENAME  = 'raw_config.txt.001'
DEFAULT_SECOND_FILENAME = 'raw_config.txt.002'
DEFAULT_FORMAT = 'text'

#################################################################

def readrawconfig(configfilename):
    global progname

    try:
        configfile = open(configfilename, 'r', encoding='utf-8')
    except IOError:
        print('{}: unable to open config file "{}" for reading'.format(configfilename), file=sys.stderr)
        return None

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

    return config
        
#################################################################

def convertrawconfigbytes(bytestream):
    config = {}

    for line in bytestream.split('\n'):
        line = line.strip()
        if len(line) == 0:
            continue
        if line[0] == '#':
            continue

        equalsposition = line.find('=')
    
        if equalsposition == -1:
            continue
    
        key = line[0:equalsposition]
        value = line[equalsposition+1:]
    
        print('+++ {} +++ {} +++'.format(key, value))
    
        if key in config:
            pass
        else:
            config[key] = value

    return config

#################################################################

def compareconfigs(first, second, format):
    diffs = {}

    index = 0

    # report keys in second config that are not in the first
    for key in second:
        if key not in first:
            if format == 'text':
                diffs[index] = 'Key "{}" added\n  New value = "{}"'.format(key, second[key])
            index += 1

    # report keys in both that have a different value
    for key in first:
        if key in second:
            if first[key] != second[key]:
                if format == 'text':
                    diffs[index] = 'Key "{}" changed\n  Old value = "{}"\n  New value = "{}"'.format(key, first[key], second[key])
                index += 1

    # report keys in first config that are not on the second
    for key in first:
        if key not in second:
            if format == 'text':
                diffs[index] = 'Key "{}" deleted\n  Old value = "{}"'.format(key, first[key])
            index += 1

    return diffs

#################################################################

def commandline():
    global progame

    parser = argparse.ArgumentParser()
        
    parser.add_argument('first',  help='name of first raw_config.txt file')
    parser.add_argument('second', help='name of second raw_config.txt file')

    args = parser.parse_args()

    firstfilename  = args.first
    secondfilename = args.second

    firstconfig = readrawconfig(firstfilename)

    if firstconfig == None:
        sys.exit(2)

    secondconfig = readrawconfig(secondfilename)

    if secondconfig == None:
        sys.exit(2)

    diffs = compareconfigs(firstconfig, secondconfig, 'text')

    numdiffs = len(diffs)

    if numdiffs == 0:
        retcode = 0
    else:
        for i in range(0, numdiffs):
            print(diffs[i])
        retcode = 1

    return retcode

#################################################################

def formbytes2file(cgiform, fieldname, outfilename):
    fileitem = cgiform[fieldname]
    allbytes = fileitem.file.read()

    filehandle = open(outfilename, 'wb')
    filehandle.write(allbytes)
    filehandle.flush()
    filehandle.close()

    return

#################################################################

def htmlform():
    title = 'Raritan raw configuration online comparison utility'

    scriptname = os.path.basename(sys.argv[0])

    print('Content-type: text/html')
    print('')

    print('</html>')

    print('<head>');

    print('<title>{}</title>'.format(html.escape(title)))

    print('</head>');

    print('<body>')

    print('<h1>{}</h1>'.format(html.escape(title)))

    form = cgi.FieldStorage()

   
    compare = form.getfirst('compare', '')

    print('<form enctype="multipart/form-data" method="post" action="{}">'.format(scriptname))

    print('<input type="file" name="firstconfig" size="80" value="Select first raw configuration file">')

    print('<br>')
    print('<br>')

    print('<input type="file" name="secondconfig" size="80" value="Select second raw configuration file">')

    print('<br>')
    print('<br>')

    print('<input type="submit" name="compare" value="Compare Configurations">')

    print('</form>')

    if compare != '':
        print('<pre>')

        print('Something happening here')

        formbytes2file(form, 'firstconfig', '/tmp/firstconfig.txt')
        formbytes2file(form, 'secondconfig', '/tmp/secondconfig.txt')

        firstconfig = readrawconfig('/tmp/firstconfig.txt')
        secondconfig = readrawconfig('/tmp/secondconfig.txt')

        diffs = compareconfigs(firstconfig, secondconfig, 'text')

        numdiffs = len(diffs)

        if numdiffs == 0:
            retcode = 0
        else:
            for i in range(0, numdiffs):
                print(diffs[i])
            retcode = 1

        print('</pre>')

    print('</body>')

    print('</html>')

    return 0

#################################################################

def main():
    try:
        gatewayinterface = os.environ['GATEWAY_INTERFACE']
    except KeyError:
        gatewayinterface = ''

    if gatewayinterface == '':
        retcode = commandline()
    else:
        retcode = htmlform()

    return retcode

#################################################################

progname = os.path.basename(sys.argv[0])

sys.exit(main())

# end of file
