#!/usr/bin/python

import sys
import os
import argparse
from urllib.request import urlopen
from bs4 import BeautifulSoup
import logging
import threading
import logging.config
import sqlite3
import config

logger = logging.getLogger('proxy')

def get(host):    
    parent=host
    tags=None
    while parent is not None and tags is None:    
        tags=query(parent)
        l=parent.split('.',1)
        if len(l)==1:
            parent=None
        else:
            parent=l[-1]
    if tags is None:
        tags=fetch(host)
        insert(host,tags)
    return tags

def query(host):
    conn = sqlite3.connect(config.db_file)
    with conn:
        c = conn.cursor()
        t = (host,)
        c.execute('SELECT tags FROM domains WHERE name=?', t)
        row=c.fetchone()
        if row:
            #empty tags will return ['']. 
            return [ tag for tag in list(map(lambda tag:tag.strip(), row[0].split(','))) if len(tag)>0]
        else:
            return None 

def insert(host,tags):
    execute("insert into domains(name, tags) values (?, ?)", (host, ','.join(tags)))

def update(host,tags):
    execute("UPDATE domains SET tags=? WHERE name=?", (','.join(tags), host))

def fetch(host):
    url='https://domain.opendns.com/{0}'.format(host)
    tags=[]
    logger.info('Fetching tag:'+url)
    try:
        html=urlopen(url).read()
        soup=BeautifulSoup(html)
        span_text=soup.find('span',{'class':'normal'}).getText().strip()
        tags=[tag for tag in list(map(lambda tag:tag.strip(), span_text.split(','))) if len(tag)>0]
    except Exception as e:
        logger.error('Fetching tag {0} exception: {1}'.format(url,e))
    logger.info('Fetched {0}:{1}'.format(host,tags))
    return tags;

def execute(sql,t=None):
    conn = sqlite3.connect(config.db_file)
    with conn:
        cur = conn.cursor()    
        if t:
            cur.execute(sql,t)       
        else:
            cur.execute(sql)       
        conn.commit()
    return

def main():
    parser=argparse.ArgumentParser(description="Fetch domain tag from opendns.")
    parser.add_argument('domain',help="Domain name")
    parser.add_argument("-c", "--create", help="create table",
                    action="store_true")
    parser.add_argument("-s", "--sql", help="sql file")
    args=parser.parse_args()
    if args.create:
        create()
    if args.sql:
        sql = open(args.sql, 'r').read()
        execute(sql)
    tags=fetch(args.domain)
    if not update(args.domain,tags):
        insert(args.domain,tags)
if __name__=="__main__":
        main()
