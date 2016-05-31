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

def loadArrays():
  xml = 'arrays.xml'
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
  xml = 'pool.xml'
  tree = ET.parse(xml)
  doc = tree.getroot()
  print "Getting Pools"    
  pools = doc.findall('.//Pool')
   # Iterate over the pools
  for pool in pools:
    for node in pool.getiterator():
      info = node.attrib['objectID']
      infoList = info.split('.')
      ArraySerialNum = infoList[2]
      dp_poolID  = int(node.attrib['poolID'])
      name = node.attrib['name']
      print name,ArraySerialNum
      freeCapacityInKB = int(node.attrib['freeCapacityInKB'])
      numberOfVVols = int(node.attrib['numberOfVVols'])
      usageRate = int(node.attrib['usageRate'])
      capacityInKB = int(node.attrib['capacityInKB'])
      capacityOfVVolsInKB = int(node.attrib['capacityOfVVolsInKB'])
    cur.execute('''INSERT  INTO Pools 
        (dp_poolID, name, ArraySerialNum, freeCapacityInKB, 
          numberOfVVols, usageRate, capacityInKB, capacityOfVVolsInKB )
        VALUES ( ?,?,?,?,?,?,?,? )''', 
        (dp_poolID, name,  ArraySerialNum, freeCapacityInKB, 
          numberOfVVols, usageRate, capacityInKB, capacityOfVVolsInKB ) ) 

  conn.commit()    

def loadLUNs():
  xml = 'logicalunit.xml'
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
      if 'label' in node.attrib.keys():
        label = node.attrib['label']
    #print ArraySerialNum, label, displayName
    cur.execute(
      '''INSERT OR IGNORE INTO LUNs 
          (ArraySerialNum, sizeInKB, 
          consumedSizeInKB, displayName, dpPoolID,label )
         VALUES ( ?,?,?,?,?,? )''', 
          (ArraySerialNum, sizeInKB, 
          consumedSizeInKB, displayName, dpPoolID,label ) ) 
  conn.commit() 

loadArrays()
loadPools()
loadLUNs()
