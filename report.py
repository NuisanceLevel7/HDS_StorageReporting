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


cur.execute('SELECT * FROM Arrays' )
arrayList = list()
for row in cur:
  arrayList.append(row)


f = Files()

#output = list()
#output.append('Name,Ser#,HCS Name,Description,Last Refreshed')  

for row in arrayList:
  
  array_sn = str(row[0])
  array_name = str(row[1])
  array_desc = str(row[2])
  array_refresh = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(row[3])))
  cur.execute('''SELECT name FROM Array2Names WHERE serialNum=?''',(array_sn,))
  output = list()
  output.append('Name,Ser#,HCS Name,Description,Last Refreshed')  
  for row in cur:
    bc_name = str(row[0])
    tmp =  [bc_name,array_sn,array_name,array_desc,array_refresh]
    output.append(",".join(tmp) )
  
  cur.execute('''SELECT * FROM Pools WHERE ArraySerialNum=?''',(array_sn,))
  
  output.append("\n")
  output.append("Pools")

  for row in cur:

    dp_poolID  = str(row[1])
    name  = row[2]
    ArraySerialNum  = row[3]
    freeCapacityInKB  = str(int(row[4]/1024/1024))
    numberOfVVols   = str(row[5])
    usageRate   = str(row[6])
    capacityInKB   = str(int(row[7]/1024/1024))
    capacityOfVVolsInKB   = str(int(row[8]/1024/1024))
    pooldata = [dp_poolID,name,freeCapacityInKB,numberOfVVols,usageRate,
                capacityInKB,capacityOfVVolsInKB]
  
    output.append(",".join(pooldata) )

  output.append("\n\n")
  for row in output:
    print row
