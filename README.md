# raritan-scp

A handful of utilities which make use of the scp features of Raritan intelligent PDUs

The utilities here may be of use to you if you are responsbile for
the administration of one or more Raritan intelligent PDUs.

## What you need

If running on UNIX/Linux:

* Python 3

If running on Windows:

* Python 3
* The pscp.exe command

The pscp.exe command can be downloaded from:

[Download PuTTY: latest release](https://www.chiark.greenend.org.uk/~sgtatham/putty/latest.html)

Be sure to select 32 or 64 bit depending on your system.

## Some basics

This link:

[PX2-1000/2000 Series Online Help](https://help.raritan.com/px2-2000/v3.5.0/en/)

is a great online resource for what you can do with Raritan intellgent PDUs.
To find out more about using the scp commands go to the "Using SCP commands" section.

A quick summary follows where "ipdu" is the hostname of a Raritan intelligent PDU.

On UNIX/Linux:

```
scp admin@ipdu:/backup_settings.txt .
scp admin@ipdu:/bulk_config.txt .
scp admin@ipdu:/raw_config.txt .
```

copies the bulk settings, the bulk config and the raw config to the
current directory.

On Windows:

```
pscp -i keyfile.ppk admin@ipdu:/backup_settings.txt backup_settings.txt
pscp -i keyfile.ppk admin@ipdu:/bulk_config.txt bulk_config.txt
pscp -i keyfile.ppk admin@ipdu:/raw_config.txt raw_config.txt
```

will do the same thing.  Note that "keyfile.ppk" is a Putty compatible
private/public key with a suitable private key for the admin user.

Try these commands on one or more of your PDUs first to check everything
will work.  If the commands do not work on their own then get that fixed
before going any further.

## pdubackups.sh UNIX/Linux shell script

This is for UNIX/Linux only.

First create a directory called `pdubackups` in your home directory.  I did the
following:

```
mkdir $HOME/pdubackups
```

Next copy the `pdubackups.sh` shell script to a directrory in your PATH renaming it to
`pdubackups` and making it executable.  Something like:

```
cp pdubackups.sh $HOME/bin/pdubackups
cd $HOME/bin
chmod u+x pdubackups
```

Now edit the `pdubackups` script and change the line which reads:

```
pdulist="px2study"
```

to be a list of the PDUs you want to backup.  For example:

```
pdulist="pdu_a pdu_b datahall rack_1_left rack_2_right"
```

Also edit the line which reads:

```
user=andyc
```

and change the user to the user name you know you can login with using scp without a password.

Now run the pdubackups script:

```
pdubackups
```

Change to the `$HOME/pdubackups` and look at the files:

```
cd $HOME/pdubackups
ls
```

Look for a file called:

```
logfile.N.log
```

where `N` is the day of the week as a number (0=Sunday, 1=Monday, etc).

Display the content of that logfile.

There should also be a bunch of other files for each PDU successfully backed up.

I recommend creating a crontab entry similar to:

```
30 23 * * * bin/pdubackups
```

To run the `pdubackups` script once every day - in the above example at 11:30pm.

Over a week you will have seven backups for each PDU in the `pdulist=` line
in the `pdubackups` script.

## diffrawconfig.py Python 3 program

Once you have two or more raw_config.txt backups from a single PDU you can use the
`diffrawconfig.py` Python 3 program to compare them and report on any differences.
Differences are classed as additions, changes and deletions.

For example if you have two raw_config.txt files called:

```
px2study.5.raw_config.txt
px2study.6.raw_config.txt
```

then then can be compared with:

```
python diffrawconfig.py px2study.5.raw_config.txt px2study.6.raw_config.txt
```

Here is some typical output:

```
Key "users[1].roles[1]" added
  New value = "4"
Key "modbus.tcp.readonly" changed
  Old value = "0"
  New value = "1"
Key "proto_listener[modbus].port" changed
  Old value = "8502"
  New value = "502"
Key "roles[8].privs._s_" deleted
  Old value = "1"
Key "roles[8].privs[0]._c_" deleted
  Old value = "firmwareUpdate"
Key "roles[8].description" deleted
  Old value = "Allow firmware updates"
Key "roles[8].name" deleted
  Old value = "FW Update"
```

## compareconfigs.py Python 3 CGI program

The `compareconfigs.py` CGI program and the matching CSS (Cascading
Style Sheet) `compareconfigs.css` can  be installed on a web server with
CGI support.  The script can then be run from a browser to compare two
raw configurations.

You can run this on the web at:

(http://cranstonhub.com/cgi-bin/compareconfigs.py)

------------------------------------------------------------

End of README.md
