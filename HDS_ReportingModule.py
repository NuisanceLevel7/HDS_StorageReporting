#!/usr/bin/python

import re,os,time,datetime,subprocess,sys
import os.path





class DateString:

  def __init__(self):
    self.yesterday = str(datetime.date.fromtimestamp(time.time() - (60*60*24) ).strftime("%Y-%m-%d"))
    self.today = str(datetime.date.fromtimestamp(time.time()).strftime("%Y-%m-%d"))
    self.tomorrow = str(datetime.date.fromtimestamp(time.time() + (60*60*24) ).strftime("%Y-%m-%d"))
    self.now = str(time.strftime('%X %x %Z'))


class SQLTools:

  def MakeTables(self,cur):
    # Make some fresh tables using executescript()
    cur.executescript('''
    DROP TABLE IF EXISTS Arrays;
    DROP TABLE IF EXISTS Pools;
    DROP TABLE IF EXISTS LUNs;
    DROP TABLE IF EXISTS Array2Names;

    CREATE TABLE Arrays (
      serialNum  TEXT NOT NULL PRIMARY KEY UNIQUE,
      name    TEXT UNIQUE,
      description    TEXT UNIQUE,
      lastRefresh  TEXT
    );

    CREATE TABLE Array2Names (
      serialNum  TEXT NOT NULL PRIMARY KEY UNIQUE,
      name    TEXT UNIQUE
    );

    CREATE TABLE Pools (
      id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
      dp_poolID  INTEGER,
      name   TEXT,
      ArraySerialNum  TEXT,
      freeCapacityInKB INTEGER,
      numberOfVVols INTEGER,
      usageRate INTEGER,
      capacityInKB INTEGER,
      capacityOfVVolsInKB INTEGER

    );

    CREATE TABLE LUNs (
      id  INTEGER NOT NULL PRIMARY KEY
          AUTOINCREMENT UNIQUE,
      consumedSizeInKB  INTEGER,
      sizeInKB INTEGER, 
      dpPoolID INTEGER,
      displayName TEXT,
      label TEXT, 
      ArraySerialNum TEXT
    );

    insert into Array2Names (name,serialNum) 
      VALUES ('SAN10',85014905),
            ('SAN11',87040225),
            ('SAN12',87041510),
            ('SAN13',87042211),
            ('SAN16',211117),
            ('SAN17',212973),
            ('SAN14',91214891),
            ('SAN15',93050015),
            ('SAN18',450098),
            ('SAN19',450132)
            ;
    ''')


class Files:

  def __init__(self):
    self.dir = ''
    self.readfile = []
    self.file_exists = 0

  def mkdir(self):
    if not os.path.isdir(self.dir):
      subprocess.call(["mkdir", self.dir])

  def write_file(self,filename,list):
    f = open(filename,'w')
    for line in list:
      f.write(line)
    f.close()

  def write_file_append(self,filename,list):
    f = open(filename,'a')
    for line in list:
      f.write(line)
    f.close()

  def write_log(self,logfile,logentry):
    f = open(logfile,'a')
    reportDate =  str(time.strftime("%x - %X"))
    f.write(reportDate + " :" + logentry)
    f.close()

  def read_file(self,filename):
    self.readfile = []
    self.file_exists = 1
    # Testing if file exists.
    if os.path.isfile(filename):
      try:
        f = open(filename,'r')
      except IOError:
        print "Failed opening ", filename
        sys.exit(2)
      for line in f:
        line = line.strip()
        self.readfile.append(line)
      f.close()
    else:
      # Set the file_exists flag in case caller cares.
      self.file_exists = 0

  def stat_file(self,fname):
    blocksize = 4096
    hash_sha = hashlib.sha256()
    f = open(fname, "rb")
    buf = f.read(blocksize)
    while 1:
      hash_sha.update(buf)
      buf = f.read(blocksize)
      if not buf:
        break    
    checksum =  hash_sha.hexdigest()
    filestat = os.stat(fname)
    filesize = filestat[6]
    return checksum,filesize

