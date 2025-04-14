#!/bin/bash

: "${CRON_SCHEDULE:=0 3 * * *}"


echo "[INFO] Starting dnsmasq"
echo "[INFO] Using CRON_SCHEDULE: $CRON_SCHEDULE"
echo "$CRON_SCHEDULE python3 /update-list.py > /proc/1/fd/1 2>&1" > /etc/cron.d/update-list

python3 /update-list.py


chmod 0644 /etc/cron.d/update-list
crontab /etc/cron.d/update-list
touch /var/log/update-list.log

printenv > /etc/environment

cron -f
