#!/usr/bin/env python3

import requests
import os

API_KEY = os.environ['PEERINGDB_API_KEY']
IN_FILE = '/etc/bird/peers.tsv'
OUT_FILE = '/etc/bird/prefix_limits.conf'

asns = []
names = {}

with open(IN_FILE) as fd:
    for line in fd.readlines():
        [name, as_set] = line.split('\t')
        asn = as_set.split(':')[0][2:]
        names[asn] = name
        asns.append(asn)

out = ''

def limit(name, v4, v6):
    global out
    out += 'define LIMIT_%s_V4 = %s;\n' % (name, v4)
    out += 'define LIMIT_%s_V6 = %s;\n' % (name, v6)

response = requests.get(
    "https://peeringdb.com/api/net?asn__in=%s" % ','.join(asns),
    headers={"Authorization": "Api-Key " + API_KEY}
)
for net in response.json()['data']:
    name = names.pop(str(net['asn']))
    limit(name, net['info_prefixes4'], net['info_prefixes6'])

# for any that didn't return results
for name in names:
    limit(name, 0, 0)

with open(OUT_FILE, 'w') as f:
    f.write(out)
