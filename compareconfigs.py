#! /usr/bin/python3
#
# @(!--#) @(#) compareconfigs.py, version 012, 12-june-2019
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

def errorpage(errormessage):
    print('Content-type: text/html')
    print('')
    print('</html>')
    print('<head>');
    print('<title>Unexpected error</title>')
    print('</head>');
    print('<body>')

    print('<h1>An unexpected error has occurred</h1>')

    print('<p>')
    print('This web page has encountered an error it cannot (currently) deal with.')
    print('</p>')

    print('<p>')
    print('This is the error message:')
    print('</p>')

    print('<pre>')
    print(html.escape(errormessage))
    print('</pre>')

    print('<p>')
    print('Try again as this may be a temporary error.')
    print('</p>')

    print('<p>')
    print('If the error keeps happening please contact:')
    print('</p>')

    print('<pre>')
    print('andy@cranstonhub.com')
    print('</pre>')

    print('<hr>')

    print('</body>')
    print('</html>')

    return

#################################################################

def unixbasename(filename, extension):
    lenfilename = len(filename)

    lenext = len(extension)

    if lenext < lenfilename:
        if filename[-lenext:] == extension:
            filename = filename[0:lenfilename-lenext]

    return filename

#################################################################

def printenv(envname):
    try:
        envvalue = os.environ[envname]
    except KeyError:
        envvalue = '<undefined>'

    if envvalue == '':
        envvalue = '<null>'

    print('Environment variable {}="{}"'.format(envname, envvalue))

    return

#################################################################

def safefilenamechars(filename):
    filename = filename.lower()

    safefilename = ''

    for c in filename:
        if c in '01234567890abcdefghijklmnopqrstuvwxyz':
            safefilename += c
        elif c in '._-':
            safefilename += c
        else:
            safefilename += '_'

    return safefilename

#################################################################

def uploadfilename(stem):
    try:
        docroot = os.environ['DOCUMENT_ROOT']
    except KeyError:
        return None

    try:
        remoteaddr = os.environ['REMOTE_ADDR']
    except KeyError:
        return None

    remoteaddr = safefilenamechars(remoteaddr)

    pid = os.getpid()

    fname = '{}/uploads/rawconfig_{}_{:05d}_{}'.format(docroot, remoteaddr, pid, stem)

    return fname

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

def compareconfigs(first, second):
    diffcount = 0

    # report keys in first config that are not on the second
    for key in first:
        if key not in second:
            diffcount += 1
            print('<div class="key">Key "{}" deleted</div>'.format(key))
            print('<div class="deleted">Old value = "{}"</div>'.format(first[key]))

    # report keys in second config that are not in the first
    for key in second:
        if key not in first:
            diffcount += 1
            print('<div class="key">Key "{}" added</div>'.format(key))
            print('<div class="added">New value = "{}"</div>'.format(second[key]))

    # report keys in both that have a different value
    for key in first:
        if key in second:
            if first[key] != second[key]:
                diffcount += 1
                print('<div class="key">Key "{}" changed</div>'.format(key))
                print('<div class="changed">Old value = "{}"</div>'.format(first[key]))
                print('<div class="changed">New value = "{}"</div>'.format(second[key]))

    if diffcount == 0:
        print('<div class="nodifference">No differences found</div>')
    else:
        print('<br>')
        print('<div class="endcomparison">End of comparison report</div>')

    return 

#################################################################

def main():
    title = 'Raritan raw configuration online comparison utility'

    scriptname = os.path.basename(sys.argv[0])

    cssname = unixbasename(scriptname, '.py') + '.css'

    form = cgi.FieldStorage()
   
    compare = form.getfirst('compare', '')

    if compare != '':
        configs = {}

        for uploadname in [ 'firstconfig', 'secondconfig' ]:
            filename = uploadfilename(uploadname + '.txt')
            if filename == None:
                errorpage('Cannot construct an upload file name for the {} file'.format(uploadname))
                sys.exit(1)

            fileitem = form[uploadname]
            allbytes = fileitem.file.read()
        
            filehandle = open(filename, 'wb')
            filehandle.write(allbytes)
            filehandle.flush()
            filehandle.close()

            configs[uploadname] = readrawconfig(filename)

    print('Content-type: text/html')
    print('')

    print('</html>')

    print('<head>');

    print('<title>{}</title>'.format(html.escape(title)))

    print('<link rel="stylesheet" type="text/css" href="{}">'.format(cssname))

    print('</head>');

    print('<body>')

    print('<h1>{}</h1>'.format(html.escape(title)))

    ### print('<pre>')
    ### print(scriptname)
    ### print(cssname)
    ### print('</pre>')

    print('<form class="main" enctype="multipart/form-data" method="post" action="{}">'.format(scriptname))

    print('<div class="prompttext">Select the first raw config file</div>')
    print('<input class="file" type="file" name="firstconfig">')

    print('<br>')
    print('<br>')

    print('<div class="prompttext">Select the second raw config file</div>')
    print('<input class="file" type="file" name="secondconfig">')

    print('<br>')
    print('<br>')

    print('<input class="submit" type="submit" name="compare" value="Compare Configurations">')

    print('</form>')

    if compare != '':
        compareconfigs(configs['firstconfig'], configs['secondconfig'])

    print('</body>')

    print('</html>')

    return 0

#################################################################

sys.exit(main())

# end of file
