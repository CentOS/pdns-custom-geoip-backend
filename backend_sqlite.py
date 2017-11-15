#!/usr/bin/python -u

from sys import stdin, stdout
import os
import GeoIP
import random
import sqlite3
import shutil

# Some variables
db_file_src= '/opt/pdns/nodes.db'
db_file = '/dev/shm/nodes.db'
default_ttl = '60'
pdns_servers = ['pdns1.centos.org','pdns2.centos.org','pdns3.centos.org']

def continent_mapping(country_code):
  """ This function will return the continent for the country given in arg - see http://dev.maxmind.com/geoip/legacy/codes/country_continent/ """
  continent_mapping_list={ 'AD': 'EU','AE': 'AS','AF': 'AS','AG': 'NA','AI': 'NA','AL': 'EU','AM': 'AS','AN': 'NA','AO': 'AF','AP': 'AS','AQ': 'AN','AR': 'SA','AS': 'OC','AT': 'EU','AU': 'OC','AW': 'NA','AX': 'EU','AZ': 'AS','BA': 'EU','BB': 'NA','BD': 'AS','BE': 'EU','BF': 'AF','BG': 'EU','BH': 'AS','BI': 'AF','BJ': 'AF','BL': 'NA','BM': 'NA','BN': 'AS','BO': 'SA','BR': 'SA','BS': 'NA','BT': 'AS','BV': 'AN','BW': 'AF','BY': 'EU','BZ': 'NA','CA': 'NA','CC': 'AS','CD': 'AF','CF': 'AF','CG': 'AF','CH': 'EU','CI': 'AF','CK': 'OC','CL': 'SA','CM': 'AF','CN': 'AS','CO': 'SA','CR': 'NA','CU': 'NA','CV': 'AF','CX': 'AS','CY': 'AS','CZ': 'EU','DE': 'EU','DJ': 'AF','DK': 'EU','DM': 'NA','DO': 'NA','DZ': 'AF','EC': 'SA','EE': 'EU','EG': 'AF','EH': 'AF','ER': 'AF','ES': 'EU','ET': 'AF','EU': 'EU','FI': 'EU','FJ': 'OC','FK': 'SA','FM': 'OC','FO': 'EU','FR': 'EU','FX': 'EU','GA': 'AF','GB': 'EU','GD': 'NA','GE': 'AS','GF': 'SA','GG': 'EU','GH': 'AF','GI': 'EU','GL': 'NA','GM': 'AF','GN': 'AF','GP': 'NA','GQ': 'AF','GR': 'EU','GS': 'AN','GT': 'NA','GU': 'OC','GW': 'AF','GY': 'SA','HK': 'AS','HM': 'AN','HN': 'NA','HR': 'EU','HT': 'NA','HU': 'EU','ID': 'AS','IE': 'EU','IL': 'AS','IM': 'EU','IN': 'AS','IO': 'AS','IQ': 'AS','IR': 'AS','IS': 'EU','IT': 'EU','JE': 'EU','JM': 'NA','JO': 'AS','JP': 'AS','KE': 'AF','KG': 'AS','KH': 'AS','KI': 'OC','KM': 'AF','KN': 'NA','KP': 'AS','KR': 'AS','KW': 'AS','KY': 'NA','KZ': 'AS','LA': 'AS','LB': 'AS','LC': 'NA','LI': 'EU','LK': 'AS','LR': 'AF','LS': 'AF','LT': 'EU','LU': 'EU','LV': 'EU','LY': 'AF','MA': 'AF','MC': 'EU','MD': 'EU','ME': 'EU','MF': 'NA','MG': 'AF','MH': 'OC','MK': 'EU','ML': 'AF','MM': 'AS','MN': 'AS','MO': 'AS','MP': 'OC','MQ': 'NA','MR': 'AF','MS': 'NA','MT': 'EU','MU': 'AF','MV': 'AS','MW': 'AF','MX': 'NA','MY': 'AS','MZ': 'AF','NA': 'AF','NC': 'OC','NE': 'AF','NF': 'OC','NG': 'AF','NI': 'NA','NL': 'EU','NO': 'EU','NP': 'AS','NR': 'OC','NU': 'OC','NZ': 'OC','O1': '--','OM': 'AS','PA': 'NA','PE': 'SA','PF': 'OC','PG': 'OC','PH': 'AS','PK': 'AS','PL': 'EU','PM': 'NA','PN': 'OC','PR': 'NA','PS': 'AS','PT': 'EU','PW': 'OC','PY': 'SA','QA': 'AS','RE': 'AF','RO': 'EU','RS': 'EU','RU': 'EU','RW': 'AF','SA': 'AS','SB': 'OC','SC': 'AF','SD': 'AF','SE': 'EU','SG': 'AS','SH': 'AF','SI': 'EU','SJ': 'EU','SK': 'EU','SL': 'AF','SM': 'EU','SN': 'AF','SO': 'AF','SR': 'SA','ST': 'AF','SV': 'NA','SY': 'AS','SZ': 'AF','TC': 'NA','TD': 'AF','TF': 'AN','TG': 'AF','TH': 'AS','TJ': 'AS','TK': 'OC','TL': 'AS','TM': 'AS','TN': 'AF','TO': 'OC','TR': 'EU','TT': 'NA','TV': 'OC','TW': 'AS','TZ': 'AF','UA': 'EU','UG': 'AF','UM': 'OC','US': 'NA','UY': 'SA','UZ': 'AS','VA': 'EU','VC': 'NA','VE': 'SA','VG': 'NA','VI': 'NA','VN': 'AS','VU': 'OC','WF': 'OC','WS': 'OC','YE': 'AS','YT': 'AF','ZA': 'AF','ZM': 'AF','ZW': 'AF' }
  return continent_mapping_list[country_code]

def backend_init():
  data = stdin.readline()
  stdout.write("OK\tCentOS Custom DNS Backend\n")
  stdout.flush()
  shutil.copy (db_file_src, db_file)

def main():
  """ This is the main hub for this python script """
  backend_init()   
  conn = sqlite3.connect(db_file)
  c = conn.cursor()
  geoip4=GeoIP.open("/usr/share/GeoIP/GeoIP.dat",GeoIP.GEOIP_MEMORY_CACHE)
  while True:
    data = stdin.readline().strip()
    query_type, qname, qclass, qtype, id, ip = data.split('\t')
    role = qname.lower().split('.')[0]
    ip_list = []
    ip6_list = []
    try:
      country_code = geoip4.country_code_by_addr(ip)
      if not country_code:
        country_code = "US"
    except:
      country_code = "US"
    cc = continent_mapping(country_code)
    c.execute("select ipv4_addr from nodes where active='true' and maintenance='false' and %s='true' and continent='%s'" % (role,cc))
    ip_list = c.fetchall()

    c.execute("select ipv6_addr from nodes where ipv6_addr != '' and active='true' and maintenance='false' and %s='true' and continent='%s'" % (role,cc))
    ip6_list = c.fetchall()

    # If both lists are empty, fallback to US
    if len(ip_list) == 0:
      c.execute("select ipv4_addr from nodes where active='true' and maintenance='false'and %s='true' and country='US'" % (role,cc))
      ip_list = c.fetchall()
      c.execute("select ipv6_addr from nodes where ipv6_addr != '' and active='true' and maintenance='false' and %s='true' and country='US'" % (role,cc))
      ip6_list = c.fetchall()



    if query_type == 'Q':
      dns_answer ="DATA\t"+qname+"\t"+qclass+"\tSOA\t86401\t-1\t ns1.centos.org\t hostmaster.centos.org\t 2008080300 1800 3600 604800 3600\n"
      if (qtype == 'NS'):
        for ns in pdns_servers:
          dns_answer +="DATA\t"+qname+"\t"+qclass+"\tNS\t86400\t-1\t"+ns+"\n"
      if (qtype == 'ANY' or qtype == 'A' or qtype == 'AAAA'):
        if len(ip_list) > 0:
          ip_answer = random.choice(ip_list)[0]
          dns_answer += "DATA\t"+qname+"\t"+qclass+"\tA\t"+default_ttl+"\t"+id+"\t"+ip_answer+"\n"
        if len(ip6_list) > 0:
          ip6_answer = random.choice(ip6_list)[0]
          dns_answer += "DATA\t"+qname+"\t"+qclass+"\tAAAA\t"+default_ttl+"\t"+id+"\t"+ip6_answer+"\n"
    stdout.write(dns_answer)
    stdout.write("END\n")
    stdout.flush()

if __name__ == '__main__':
  main()
