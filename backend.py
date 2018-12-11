#!/usr/bin/python -u

from sys import stdin, stdout, stderr
import os
import random
import geoip2.database
import json
import datetime

# Some variables
backend_json = '/var/lib/centos-pdns/backend.json'
default_ttl = '60'
auth_zone = 'centos.org'
pdns_servers = ['pdns1', 'pdns2', 'pdns3']
pdns_ipaddresses = { 'pdns1': '108.61.16.227', 'pdns2': '85.236.43.108', 'pdns3': '67.219.148.138' }
geodb = geoip2.database.Reader('/usr/share/GeoIP/GeoLite2-City.mmdb')
soa_ver = datetime.datetime.today().strftime('%Y%m%d%H')
debug = False

def continent_mapping(country_code):
  """ This function will return the continent for the country given in arg - see http://dev.maxmind.com/geoip/legacy/codes/country_continent/ """
  continent_mapping_list={ 'AD': 'EU','AE': 'AS','AF': 'AS','AG': 'NA','AI': 'NA','AL': 'EU','AM': 'AS','AN': 'NA','AO': 'AF','AP': 'AS','AQ': 'AN','AR': 'SA','AS': 'OC','AT': 'EU','AU': 'OC','AW': 'NA','AX': 'EU','AZ': 'AS','BA': 'EU','BB': 'NA','BD': 'AS','BE': 'EU','BF': 'AF','BG': 'EU','BH': 'AS','BI': 'AF','BJ': 'AF','BL': 'NA','BM': 'NA','BN': 'AS','BO': 'SA','BR': 'SA','BS': 'NA','BT': 'AS','BV': 'AN','BW': 'AF','BY': 'EU','BZ': 'NA','CA': 'NA','CC': 'AS','CD': 'AF','CF': 'AF','CG': 'AF','CH': 'EU','CI': 'AF','CK': 'OC','CL': 'SA','CM': 'AF','CN': 'AS','CO': 'SA','CR': 'NA','CU': 'NA','CV': 'AF','CX': 'AS','CY': 'AS','CZ': 'EU','DE': 'EU','DJ': 'AF','DK': 'EU','DM': 'NA','DO': 'NA','DZ': 'AF','EC': 'SA','EE': 'EU','EG': 'AF','EH': 'AF','ER': 'AF','ES': 'EU','ET': 'AF','EU': 'EU','FI': 'EU','FJ': 'OC','FK': 'SA','FM': 'OC','FO': 'EU','FR': 'EU','FX': 'EU','GA': 'AF','GB': 'EU','GD': 'NA','GE': 'AS','GF': 'SA','GG': 'EU','GH': 'AF','GI': 'EU','GL': 'NA','GM': 'AF','GN': 'AF','GP': 'NA','GQ': 'AF','GR': 'EU','GS': 'AN','GT': 'NA','GU': 'OC','GW': 'AF','GY': 'SA','HK': 'AS','HM': 'AN','HN': 'NA','HR': 'EU','HT': 'NA','HU': 'EU','ID': 'AS','IE': 'EU','IL': 'AS','IM': 'EU','IN': 'AS','IO': 'AS','IQ': 'AS','IR': 'AS','IS': 'EU','IT': 'EU','JE': 'EU','JM': 'NA','JO': 'AS','JP': 'AS','KE': 'AF','KG': 'AS','KH': 'AS','KI': 'OC','KM': 'AF','KN': 'NA','KP': 'AS','KR': 'AS','KW': 'AS','KY': 'NA','KZ': 'AS','LA': 'AS','LB': 'AS','LC': 'NA','LI': 'EU','LK': 'AS','LR': 'AF','LS': 'AF','LT': 'EU','LU': 'EU','LV': 'EU','LY': 'AF','MA': 'AF','MC': 'EU','MD': 'EU','ME': 'EU','MF': 'NA','MG': 'AF','MH': 'OC','MK': 'EU','ML': 'AF','MM': 'AS','MN': 'AS','MO': 'AS','MP': 'OC','MQ': 'NA','MR': 'AF','MS': 'NA','MT': 'EU','MU': 'AF','MV': 'AS','MW': 'AF','MX': 'NA','MY': 'AS','MZ': 'AF','NA': 'AF','NC': 'OC','NE': 'AF','NF': 'OC','NG': 'AF','NI': 'NA','NL': 'EU','NO': 'EU','NP': 'AS','NR': 'OC','NU': 'OC','NZ': 'OC','O1': '--','OM': 'AS','PA': 'NA','PE': 'SA','PF': 'OC','PG': 'OC','PH': 'AS','PK': 'AS','PL': 'EU','PM': 'NA','PN': 'OC','PR': 'NA','PS': 'AS','PT': 'EU','PW': 'OC','PY': 'SA','QA': 'AS','RE': 'AF','RO': 'EU','RS': 'EU','RU': 'EU','RW': 'AF','SA': 'AS','SB': 'OC','SC': 'AF','SD': 'AF','SE': 'EU','SG': 'AS','SH': 'AF','SI': 'EU','SJ': 'EU','SK': 'EU','SL': 'AF','SM': 'EU','SN': 'AF','SO': 'AF','SR': 'SA','ST': 'AF','SV': 'NA','SY': 'AS','SZ': 'AF','TC': 'NA','TD': 'AF','TF': 'AN','TG': 'AF','TH': 'AS','TJ': 'AS','TK': 'OC','TL': 'AS','TM': 'AS','TN': 'AF','TO': 'OC','TR': 'EU','TT': 'NA','TV': 'OC','TW': 'AS','TZ': 'AF','UA': 'EU','UG': 'AF','UM': 'OC','US': 'NA','UY': 'SA','UZ': 'AS','VA': 'EU','VC': 'NA','VE': 'SA','VG': 'NA','VI': 'NA','VN': 'AS','VU': 'OC','WF': 'OC','WS': 'OC','YE': 'AS','YT': 'AF','ZA': 'AF','ZM': 'AF','ZW': 'AF' }
  try:
    return continent_mapping_list[country_code]
  except:
    return 'NA'

def backend_init():
  data = stdin.readline()
  stdout.write("OK\tPDNS Custom python Backend\n")
  stdout.flush()

def main():
  """ This is the main hub for this python script """
  backend_init()  
  with open(backend_json) as backend: 
    nodes = json.load(backend)
  while True:
    data = stdin.readline().strip()
    # Debug
    if debug:
      stderr.write("Received \n")
      stderr.write(data)
    query_type, qname, qclass, qtype, id, ip = data.split('\t')
    role = qname.lower().split('.')[0]
    try:
      country_code = geodb.city(ip).country.iso_code.upper()
      if not country_code:
        country_code = "US"
    except:
      country_code = "US"
    cc = continent_mapping(country_code)
    
    # Debug line
    if debug: 
      input = ("\n%s %s %s %s %s\n") % (qname, qclass, country_code, cc, ip)
      stderr.write(input)
    # Searching for ipv4 for role
    if role in nodes:    
      ip_list = nodes[role][cc]['ipv4']
      ip6_list = nodes[role][cc]['ipv6']
      valid_host = True
      pdns_host = False
    elif role in pdns_servers:
      ip_list = []
      ip6_list = []
      valid_host = True
      pdns_host = True
    else:
      ip_list = []
      ip6_list = []
      valid_host = False

    if query_type == 'Q':
      if not valid_host:
        if (qtype == 'SOA' or qtype == 'ANY') and qname == auth_zone:
          dns_answer = "DATA\t%s\t%s\tSOA\t86400\t-1\t pdns1.%s\t hostmaster.%s\t %s 1800 3600 604800 3600\n" % (qname,qclass,auth_zone,auth_zone,soa_ver)
          if debug:
            stderr.write("sending this to pdns\n")
            stderr.write(dns_answer)
          stdout.write(dns_answer)
        stdout.write("END\n")
        stdout.flush()
 
      if valid_host:
        if (qtype == 'SOA' or qtype == 'ANY'):
          dns_answer = "DATA\t%s\t%s\tSOA\t86400\t-1\t pdns1.%s\t hostmaster.%s\t %s 1800 3600 604800 3600\n" % (qname,qclass,auth_zone,auth_zone,soa_ver)
        if (qtype == 'NS' or qtype == 'ANY') and valid_host:
          for ns in pdns_servers:
            dns_answer +="DATA\t%s\t%s\tNS\t86400\t-1\t%s.%s\n" % (qname,qclass,ns,auth_zone)
        if (qtype == 'ANY' or qtype == 'A' or qtype == 'AAAA'):
          if len(ip_list) > 0 and role not in ['buildlogs','cloud']:
            while len(ip_list) < 5:
              ip_list.append(random.choice(nodes[role]['NA']['ipv4']))
            ip_answer = random.choice(ip_list)
            dns_answer += "DATA\t%s\t%s\tA\t%s\t%s\t%s\n" % (qname,qclass,default_ttl,id,ip_answer)
          elif pdns_host:
            dns_answer += "DATA\t%s\t%s\tA\t%s\t%s\t%s\n" % (qname,qclass,default_ttl,id,pdns_ipaddresses[role])
          elif valid_host:
            ip_answer = random.choice(nodes[role]['NA']['ipv4'])
            dns_answer += "DATA\t%s\t%s\tA\t%s\t%s\t%s\n" % (qname,qclass,default_ttl,id,ip_answer)      
          else:
            # Invalid host trap, sending END
            valid_host = False
          if len(ip6_list) > 0:
            ip6_answer = random.choice(ip6_list)
            dns_answer += "DATA\t%s\t%s\tAAAA\t%s\t%s\t%s\n" % (qname,qclass,default_ttl,id,ip6_answer)
        # Debug
        if debug:
          stderr.write("sending this to pdns\n")
          stderr.write(dns_answer)
        stdout.write(dns_answer)
        stdout.write("END\n")
        stdout.flush()

if __name__ == '__main__':
  main()

