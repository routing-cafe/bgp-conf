#!/usr/bin/env python3

import requests
import os
import subprocess
from collections import defaultdict

MY_ASN = os.environ["MY_ASN"]
API_KEY = os.environ["PEERINGDB_API_KEY"]
OUT_FILE = "/etc/bird/gen.conf"


def run(command):
    return subprocess.check_output(command, shell=True, text=True)


peers = defaultdict(dict)

for line in run(f"whois AS{MY_ASN}").split("\n"):
    if line.startswith("import:"):
        parts = line.split()
        peers[parts[2]]["import"] = parts[4]
    elif line.startswith("export:"):
        parts = line.split()
        peers[parts[2]]["export"] = parts[4]

for asn in peers:
    as_set = peers[asn]["import"]
    if as_set == "ANY":
        peers[asn]["irr_v4"] = f"define IRR_{asn}_V4 = [0.0.0.0/0];\n"
        peers[asn]["irr_v6"] = f"define IRR_{asn}_V6 = [::/0];\n"
        peers[asn]["irr_asn"] = f"define IRR_{asn}_ASN = [0..4294967295];\n"
    else:
        peers[asn]["irr_v4"] = run(
            f'bgpq4 -4Ab -m24 -R24 "{as_set}" -l "define IRR_{asn}_V4"'
        )
        peers[asn]["irr_v6"] = run(
            f'bgpq4 -6Ab -m48 -R48 "{as_set}" -l "define IRR_{asn}_V6"'
        )
        peers[asn]["irr_asn"] = run(
            f'bgpq4 -tb "{as_set}" -l "define IRR_{asn}_ASN"'
        )

asns = {asn[2:] for asn in peers}
response = requests.get(
    "https://peeringdb.com/api/net?asn__in=%s" % ",".join(asns),
    headers={"Authorization": "Api-Key " + API_KEY},
)
for net in response.json()["data"]:
    peers["AS" + str(net["asn"])]["limits"] = (
        net["info_prefixes4"],
        net["info_prefixes6"],
    )

out = ""
for asn in peers:
    peer = peers[asn]
    (v4, v6) = peer.get("limits") or (0, 0)
    out += f"define LIMIT_{asn}_V4 = {v4};\n"
    out += f"define LIMIT_{asn}_V6 = {v6};\n"

    out += peer["irr_v4"]
    out += peer["irr_v6"]
    out += peer["irr_asn"]

    out += "\n"

print(out)

with open(OUT_FILE, "w") as f:
    f.write(out)
