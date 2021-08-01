#!/bin/bash

#Run on launch
python display.py

echo "*/5 * * * * cd /code ; /usr/local/bin/python display.py >> /var/log/cron.log 2>&1
# "> schedule.txt

crontab schedule.txt
cron -f