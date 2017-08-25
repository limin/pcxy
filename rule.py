#!/usr/bin/python

import logging
import pdb
from croniter import croniter
from datetime import datetime
from dateutil.tz import tzlocal
from yaml import load,dump

logger = logging.getLogger('proxy')
with open('rule.yaml') as stream:
    rules=load(stream)


def isTagAllowed(tag):    
    now = datetime.now(tzlocal())
    def get_full_datetime(d,t):
        l=t.split(':')
        return datetime(d.year, d.month,d.day,int(l[0]), int(l[1]),tzinfo=tzlocal())
    
    try:
        for rule in rules['denies']: 
            #pdb.set_trace()
            cron=croniter(rule['cron_date'],now)
            d=cron.get_prev(datetime)
            start_time = get_full_datetime(d,rule['start_time']);
            end_time = get_full_datetime(d,rule['end_time']);
            if now.time()>=start_time.time() and now.time()<=end_time.time():
                if tag in rule['tags']:
                    return False

        for rule in rules['allows']:
            cron=croniter(rule['cron_date'],now)
            d=cron.get_prev(datetime)
            start_time = get_full_datetime(d,rule['start_time']);
            end_time = get_full_datetime(d,rule['end_time']);
            if now.time()>=start_time.time() and now.time()<=end_time.time():
                if tag in rule['tags']:
                    return True
    except Exception as e:
        logger.error('Checking rule of tag {0} exception: {1}'.format(tag,e))

    return False # not defined anywhere, return False
