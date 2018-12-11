# pdns-custom-geoip-backend
This repository hosts the various python code and/or data that helps building a powerdns pipe backend that suits centos infra needs

## Requirements
 * python
 * Maxmind Geolite2 database : [City version](https://dev.maxmind.com/geoip/geoip2/geolite2/)
 * python-geoip2 pkg (to consume those Geolite2 DB)
 * [PowerDNS](http://www.powerdns.com)

## How to use
The goal of that backend is to create dynamic backend in the CentOS infra. Some roles like mirror.centos.org (and vault,msync,cloud,buildlogs) are spread around multiple nodes, so redirecting the user to one of the nodes in the originator continent if possible, falling back to some node from US 

This python script will be used as a [pdns pipe backend](https://doc.powerdns.com/authoritative/backends/pipe.html)

To add this pipe backend, configure pdns.conf like this (assuming that code and also sqlite DB will live in /opt/pdns) : 
```
launch=pipe
pipe-command=<path to backend.py>
pipebackend-abi-version=1

```
## json backend
Structure for the .json backend is simple:
record/role => continent => ipv4/ipv6 lists
Example 
```
{
    "mirror": {
        "AF": {
            "ipv4": [], 
            "ipv6": []
        }, 
        "NA": {
            "ipv4": [
                "192.168.1.1", 
                "192.168.2.2"
            ], 
            "ipv6": [
                "::2", 
                "::3"
            ]
        }, 
      } 
}

```
The .json is in fact generated from a SQL db in which we add/remove/disable some nodes (through monitoring) and each new role added in the DB is converted a potential <role>.centos.org in the .json file and reloaded on pdns backend

