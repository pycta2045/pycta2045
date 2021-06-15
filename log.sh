#!/bin/bash
DATE=$(date +%D)
TIME=$(date +%I:%M\ %p)
TARGET="./HOURS.txt"
FILE_NAME='./temp.txt'
if [ -f $FILE_NAME ];then # File exist
	echo log ended
	var="END\t: $TIME"
	#echo -e "writing...\n$var"
	echo -e $var >> $FILE_NAME
	echo "=================="
	contant=$(cat $FILE_NAME)
	echo -e "$contant"
	rm $FILE_NAME
	echo -e "$contant\n==================">>$TARGET
else # File doesn't exist
	echo log started...
	var="$DATE\nSTART\t: $TIME"
	echo -e $var >> $FILE_NAME
fi	
echo "=================="
