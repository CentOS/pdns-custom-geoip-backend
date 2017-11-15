# pdns-custom-geoip-backend
This repository hosts the various python code and/or data that helps building a powerdns pipe backend that suits centos infra needs

## Requirements
 * python
 * sqlite
 * PDNS

## How to use
The goal of that backend is to create dynamic backend in the CentOS infra. Some roles like mirror.centos.org (and vault,msync,cloud,buildlogs) are spread around multiple nodes, so redirecting the user to one of the node in the originator countinent if possible, falling back to some node from US 

To add this pipe backend, configure pdns.conf like this (assuming that code and also sqlite DB will live in /opt/pdns) : 
```
pipe-command=/opt/pdns/backend_sqlite.py
pipebackend-abi-version=1

```

## Sqlite DB format
```
CREATE TABLE nodes ( id integer primary key, fqdn, country, continent, active, maintenance, ipv4_addr, ipv6_addr, mirror, vault, debuginfo, cloud, buildlogs, msync);
```
