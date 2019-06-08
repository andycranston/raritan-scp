#!/bin/bash
#
# pdubackups
#
# a shell script to backup a number of PDUs
# naming the backup file with the PDU name in it
#

pdulist="px2study"
user="andyc"
filelist="backup_settings.txt bulk_config.txt raw_config.txt"

#
# Main
#

PATH=/bin:/usr/bin
export PATH

progname=`basename $0`

backupdir=$HOME/pdubackups

dayofweek=`date '+%w'`

logfile=$backupdir/logfile.$dayofweek.log
cp /dev/null $logfile

echo "Starting run of script \"$progname\"" >> $logfile

for pdu in $pdulist
do
  echo "Getting backup files from PDU \"$pdu\"" >> $logfile

  for file in $filelist
  do
    echo "Getting file \"$file\" from PDU \"$pdu\"" >> $logfile
    scp $user@$pdu:/$file $backupdir/$pdu.$dayofweek.$file >>$logfile 2>&1
    if [ $? -ne 0 ]
    then
      echo "ERROR: an error occurred copying file \"$file\" from PDU \"$pdu\"" >>$logfile
    fi
  done
done

echo "Run of script \"$progname\" complete" >> $logfile

exit 0
