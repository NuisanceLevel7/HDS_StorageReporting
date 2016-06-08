#!/usr/bin/python

import re,os,time,datetime,subprocess,sys
import os.path
from shutil import copyfile






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
    DROP TABLE IF EXISTS Paths;

    CREATE TABLE Arrays (
      serialNum  TEXT NOT NULL PRIMARY KEY UNIQUE,
      name    TEXT UNIQUE,
      description    TEXT UNIQUE,
      lastRefresh  TEXT
    );

    CREATE TABLE Array2Names (
      ArraySerialNum  TEXT NOT NULL PRIMARY KEY UNIQUE,
      name    TEXT UNIQUE
    );

    CREATE TABLE Pools (
      id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
      poolID  INTEGER,
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
      ArraySerialNum TEXT,
      Paths integer
    );

    CREATE TABLE Paths (
      id  INTEGER NOT NULL PRIMARY KEY
          AUTOINCREMENT UNIQUE,
      displayDevNum  TEXT,
      WWN TEXT, 
      portName TEXT,
      ArraySerialNum TEXT,
      Host TEXT
    );

    insert into Array2Names (name,ArraySerialNum) 
      VALUES ('SAN10',85014905),
            ('SAN11',87040225),
            ('SAN12',87041510),
            ('SAN13',87042211),
            ('SAN16',211117),
            ('SAN17',212973),
            ('SAN15',91214891),
            ('SAN14',93050015),
            ('SAN18',450098),
            ('SAN19',450132)
            ;
    ''')


# Add to the module...
# GetArrayList - 1) creates an instance dict() variable named arrayList
#                arrayList[serial] = Friendly_Name or ArrayName
#
#                2) Also create the formatted CSV line the each array in ArrayData[SN] = CSV
#
#                3) Also create instance variables to hold the CSV formatted headers for arrays, pools and LUNs



class ReportGen:

  def __init__(self):
    
    self.Array2Name = dict()
    self.ArrayList = dict()
    self.ArrayData = dict()
    self.ArrayColumnHeader = 'Name,Ser#,HCS Name,Description,Last Refreshed'
    self.PoolColumnHeader = 'Pool ID,Name,Capacity GB,Free GB, UsageRate,V-Vols, Subscribed GB, Subscription%'
    self.LunColumnHeader = 'LUN ID,Consumed (GB),Capacity GB,Label,Host,Pool ID,Array SN'
    self.PoolList = list()
    self.LunList = list()
    f = Files()
    f.dir = 'Report'
    f.mkdir()    
    f.copy_file('logo_datalink.png', 'Report/logo_datalink.png')


  def GetArrayList(self,cur):

    self.ArrayList = dict()
    self.ArrayData = dict()    
    cur.execute('SELECT * FROM Arrays' )
    
    arrays = list()
    for row in cur:
      arrays.append(row)

    for row in arrays:
  
      array_sn = str(row[0])
      array_name = str(row[1])
      alt_name = str(row[1])
      
      array_desc = str(row[2])
      array_refresh = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(row[3])))
      cur.execute('''SELECT name FROM Array2Names WHERE ArraySerialNum=?''',(array_sn,))
      output = list()
      output.append('Name,Ser#,HCS Name,Description,Last Refreshed\n')  
      for row in cur:
        alt_name = str(row[0])
      self.ArrayList[array_sn] =  [alt_name,array_sn,array_name,array_desc,array_refresh]
      csv = ",".join(self.ArrayList[array_sn])
      self.ArrayData[array_sn] = csv
      self.Array2Name[array_sn] = alt_name

  def GetPoolList(self,cur,array):
    
    self.PoolList = list()
    cur.execute('''SELECT * FROM Pools WHERE ArraySerialNum=?''',(array,))
    for row in cur:
      
      poolID  = str(row[1])
      name  = row[2]
      ArraySerialNum  = row[3]
      freeCapacityInTB  = str(int(row[4]/1024/1024))
      numberOfVVols   = str(row[5])
      usageRate   = str(row[6])
      capacityInTB   = str(int(row[7]/1024/1024))
      capacityOfVVolsInTB   = str(int(row[8]/1024/1024))
      subscription = (float(capacityOfVVolsInTB)/float(capacityInTB))*100
      subscription = format(subscription, '0.1f')
      pooldata = [poolID,name,capacityInTB,freeCapacityInTB,usageRate,numberOfVVols,
                capacityOfVVolsInTB,str(subscription)]
      self.PoolList.append(pooldata)

  def GetLunList(self,cur,array):
    luns = dict()
    self.LunList = list()
    cur.execute('''SELECT displayDevNum,Host FROM Paths WHERE ArraySerialNum=?''',(array,))
    for row in cur:
      luns[str(row[0])] = str(row[1])
    cur.execute('''SELECT * FROM LUNs WHERE ArraySerialNum=? and paths=1''',(array,))
    for row in cur:
      consumedSizeInKB = str(format((int(row[1])/1024/1024),'0.1f'))
      sizeInKB = str(format((int(row[2])/1024/1024),'0.1f'))
      dpPoolID = str(row[3])
      displayName = str(row[4])
      label = str(row[5])
      hostname = '----' 
      if displayName in luns:
        hostname = luns[displayName]
      lundata = [displayName,consumedSizeInKB,sizeInKB,label,hostname,dpPoolID,array]
      self.LunList.append(lundata)






class Files:

  def __init__(self):
    self.dir = ''
    self.data = []
    self.file_exists = 0

  def mkdir(self):
    if not os.path.isdir(self.dir):
      subprocess.call(["mkdir", self.dir])

  def write_file(self,filename,list):
    f = open(filename,'w')
    for line in list:
      f.write(line + '\n')
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
        self.data.append(line)
      f.close()
    else:
      # Set the file_exists flag in case caller cares.
      self.file_exists = 0

  def copy_file(self,src, dest):
    try:
      copyfile(src, dest)
    except IOError:
      print "Failed file copy ", src,dest
      sys.exit(2)

    
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

class HTML5:

  def __init__(self):
    self.tr = '<tr>'
    self.td = '<td>'
    self.th = '<th>'
    self.end_table = '\n</table>\n'
    self.end_html = '  </body>\n</html>\n'
    self.http_header = 'Content Type: text/html\n\n'

    


  def style_sheet(self):
    stylesheet = '''
<style>
#header {
    background-color:black;
    color:white;
    text-align:center;
    padding:5px;
}
#nav {
    line-height:30px;
    height:400px;
    width:10%;
    float:left;
    padding:5px;
    overflow:auto;
    background-color:#eeeeee;    
}
#section {
    width:85%;
    float:left;
    padding:10px;
}
#footer {
    background-color:black;
    color:white;
    clear:both;
    text-align:center;
    padding:5px;
}
#nav_content
{
  overflow:auto;
  background:#fff;
}
#section_content
{
  height:600px;
  overflow:auto;
  background:#fff;
  padding:10px;
}
p.small 
{
    line-height: 30px;
}
p.big 
{
    line-height: 60px;
}
</style>'''
    f = open('Report/Report.css','w')
    f.write(stylesheet)
    f.close()
   
    
 
  
  def th_list(self,row,bgcolor='#BAB9B8'):
    
    html = '      <tr bgcolor=' + bgcolor + '>'
    for cell in row:
      html += '<th>' + str(cell) + '</th>'
    html += '</tr>\n'
    return html

  def tr_list(self,row,bgcolor=''):
    html = '      <tr bgcolor=' + bgcolor + '>'
    for cell in row:
      html += '<td>' + str(cell) + '</td>'
    html += '</tr>\n'
    return html   
 
 
  def start_html(self,title='Web Report Page',align='center'): 
    html =   '<!DOCTYPE html>\n'
    html +=  '  <head><title>' + title + '</title>\n'
    html +=  '  <meta charset="UTF-8">\n'
    html +=  '  <link href="Report.css" rel="stylesheet" />\n'
    html +=  '  </head>\n'
    html +=  '  <body align="' + align + '">\n'
    return  html
    
       

  def start_table(self,align='center',border='1',caption='',width='100%'):
    html =  '\n\n'
    #html += '<p><br>\n'
    html += '<table align="' + align +  '" border="' + str(border)
    html += '" width="' + width + '">\n'
    if caption != '':
      html += '<caption>' + caption + '</caption>\n'
    return  html
 

  def insert_table(self,rows,headings,align='center',border='1',caption=''):
    html =  '\n\n'
    html += '<p><br>\n'
    html += '<table align="' + align +  '" border="' + str(border) + '">\n'
    html += '<caption>' + caption + '</caption>\n'
    for row in rows:
      html += self.tr_list(row)
    html += self.end_table
    return  html


  def header(self,content):
    code = '<div id="header"><br>\n'
    code += content + '\n</div>\n'
    return code

  def nav(self,content):
    code = '<div id="nav">\n'
    code += content + '\n</div>\n'
    return code

  def section(self,content):
    code = '<div id="section">\n'
    code += content + '\n</div>\n'
    return code

  def footer(self,content):
    code = '<div id="footer">\n'
    code += content + '\n</div>\n'
    return code







