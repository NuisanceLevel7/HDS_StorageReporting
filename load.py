#!/usr/bin/python
#
#
import sqlite3
import time
import xml.etree.ElementTree as ET
from HDS_ReportingModule import Files
from HDS_ReportingModule import SQLTools

conn = sqlite3.connect('HDS_Report.sqlite')
cur = conn.cursor()

db = SQLTools()
db.MakeTables(cur)

f = Files()
f.dir = 'XML_DATA'
f.mkdir()

def loadArrays():
  xml = 'XML_DATA/arrays.xml'
  tree = ET.parse(xml)
  doc = tree.getroot()
  #
  # Find the arrays
  arrays = doc.findall('.//StorageArray')

  # Iterate over the arrays
  for array in arrays:
    for node in array.getiterator():
      serialNum =  node.attrib['serialNumber']    
      name = node.attrib['name']
      description = node.attrib['description']
      lastRefresh = node.attrib['lastRefreshed']

    cur.execute('''INSERT OR IGNORE INTO Arrays (serialNum, name, description, lastRefresh)
        VALUES ( ?,?,?,? )''', ( serialNum, name, description, lastRefresh ) )

  conn.commit()


def loadPools():
  xml = 'XML_DATA/pool.xml'
  tree = ET.parse(xml)
  doc = tree.getroot()
  pools = doc.findall('.//Pool')
   # Iterate over the pools
  for pool in pools:
    for node in pool.getiterator():
      info = node.attrib['objectID']
      infoList = info.split('.')
      ArraySerialNum = infoList[2]
      poolID  = int(node.attrib['poolID'])
      name = node.attrib['name']
      freeCapacityInKB = int(node.attrib['freeCapacityInKB'])
      numberOfVVols = int(node.attrib['numberOfVVols'])
      usageRate = int(node.attrib['usageRate'])
      capacityInKB = int(node.attrib['capacityInKB'])
      capacityOfVVolsInKB = int(node.attrib['capacityOfVVolsInKB'])
    cur.execute('''INSERT  INTO Pools 
        (poolID, name, ArraySerialNum, freeCapacityInKB, 
          numberOfVVols, usageRate, capacityInKB, capacityOfVVolsInKB )
        VALUES ( ?,?,?,?,?,?,?,? )''', 
        (poolID, name,  ArraySerialNum, freeCapacityInKB, 
          numberOfVVols, usageRate, capacityInKB, capacityOfVVolsInKB ) ) 

  conn.commit()    

def loadLUNs():
  xml = 'XML_DATA/logicalunit.xml'
  tree = ET.parse(xml)
  doc = tree.getroot()
  luns = doc.findall('.//LDEV')
  for lun in luns:
    for node in lun.getiterator():
      label = '-----'
      if 'objectID' in node.attrib.keys():
        info = node.attrib['objectID']
        infoList = info.split('.')
        ArraySerialNum = infoList[2]  
        sizeInKB = int(node.attrib['sizeInKB'])
        consumedSizeInKB = int(node.attrib['consumedSizeInKB'])
        displayName = node.attrib['displayName']
        dpPoolID = int(node.attrib['dpPoolID'])
        if str(node.attrib['path']) == 'false' :
          paths = 0
        else:
          paths = 1

      if 'label' in node.attrib.keys():
        label = node.attrib['label']
    #print ArraySerialNum, label, displayName
    cur.execute(
      '''INSERT OR IGNORE INTO LUNs 
          (ArraySerialNum, sizeInKB, 
          consumedSizeInKB, displayName, dpPoolID,label,paths) 
         VALUES ( ?,?,?,?,?,?,?)''', 
          (ArraySerialNum, sizeInKB, 
          consumedSizeInKB, displayName, dpPoolID,label,paths) )

  conn.commit() 


def loadPaths():
  xml = 'XML_DATA/paths.xml'
  tree = ET.parse(xml)
  doc = tree.getroot()
  paths = doc.findall('.//Path')
  for path in paths:
    for node in path.getiterator():
      WWN = '-----'
      if 'objectID' in node.attrib.keys():
        info = node.attrib['objectID']
        infoList = info.split('.')
        ArraySerialNum = infoList[2]  
        displayDevNum = node.attrib['displayDevNum']
        portName = node.attrib['portName']
      if 'WWN' in node.attrib.keys():
        WWN = node.attrib['WWN']
    #print ArraySerialNum, label, displayName
    cur.execute(
      '''INSERT INTO Paths 
          (ArraySerialNum, displayDevNum, 
          portName, WWN, Host )
         VALUES ( ?,?,?,?,? )''', 
          (ArraySerialNum, displayDevNum, 
          portName, WWN, WWN ) ) 
  conn.commit() 

def Hosts():
  WWN2Host = dict()
  hostinfo = 'XML_DATA/hostinfo.txt'
  f.read_file(hostinfo)
  for line in f.data:
    if 'objectID=HOSTINFO' in line:
      lines = line.split('.')
      hostname = '"' + lines[1] + '"'
    if 'portWWN=' in line:
      lines = line.split('=')
      WWN = '"' + lines[1]  + '"'
      WWN2Host[WWN] = hostname
  hostinfo = 'XML_DATA/hosts.txt'
  f.read_file(hostinfo)
  for line in f.data:
    line = line.strip()
    if line.startswith('name='):
      lines = line.split('=')
      hostname = lines[1]
    if line.startswith('WWN='):
      lines = line.split('=')
      WWN =  lines[1] 
      WWN2Host[WWN] = hostname      
  for (WWN,hostname) in  WWN2Host.items():
    sql = '''UPDATE Paths SET Host= ? WHERE WWN= ?''' 
    cur.execute(sql,(hostname,WWN))
  conn.commit()

  
loadArrays()
loadPools()
loadLUNs()
loadPaths()
Hosts()
conn.commit()
conn.close()
