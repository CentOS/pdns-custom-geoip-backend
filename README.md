# pdns-custom-geoip-backend
This repository hosts the various python code and/or data that helps building a powerdns pipe backend that suits centos infra needs

## Requirements
 * python
 * sqlite
 * [PowerDNS](http://www.powerdns.com)

## How to use
The goal of that backend is to create dynamic backend in the CentOS infra. Some roles like mirror.centos.org (and vault,msync,cloud,buildlogs) are spread around multiple nodes, so redirecting the user to one of the nodes in the originator continent if possible, falling back to some node from US 

This python script will be used as a [pdns pipe backend](https://doc.powerdns.com/authoritative/backends/pipe.html)

To add this pipe backend, configure pdns.conf like this (assuming that code and also sqlite DB will live in /opt/pdns) : 
```
launch=pipe
pipe-command=/opt/pdns/backend_sqlite.py
pipebackend-abi-version=1

```

## Sqlite DB format
```
CREATE TABLE nodes ( id integer primary key, fqdn, country, continent, active, maintenance, ipv4_addr, ipv6_addr, mirror, vault, debuginfo, cloud, buildlogs, msync);
```
Enabling/disabling a role is easy as setting the value to 'true'/'false' and adding a new "record" would just need to alter the table with a new column name
