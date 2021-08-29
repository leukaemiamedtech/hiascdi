#!/bin/bash

FMSG="HIAS Historical Data Interface component installation terminated!"

printf -- 'This script will install the HIAS Historical Data Interface component on HIAS Core.\n';
printf -- '\033[33m WARNING: This is an inteteractive installation, please follow instructions provided. \033[0m\n';

read -p "Proceed (y/n)? " proceed
if [ "$proceed" = "Y" -o "$proceed" = "y" ]; then
    printf -- 'Installing the HIAS Historical Data Interface component....\n';
    conda install -c conda-forge bson
    conda install flask
    conda install -c conda-forge paho-mqtt
    conda install pandas
    conda install psutil
    conda install pymongo
    conda install requests
    conda install urllib3
    pip install mgoquery
    printf -- '\033[32m SUCCESS: HIAS Historical Data Interface component installed successfully! \033[0m\n';
    exit 0
else
    echo $FMSG;
    exit 1
fi