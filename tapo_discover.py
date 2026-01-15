#!/usr/bin/env python3
import os, time, subprocess
from wsdiscovery import WSDiscovery, QName

ETH_IFACE = os.environ.get("ETH_IFACE","enP8p1s0")
IP_FILE = "/opt/tapo/tapo_ip.txt"
LEASE_FILE = "/var/lib/misc/dnsmasq.leases"

def sh(cmd):
    return subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True).stdout.strip()

def from_leases():
    if not os.path.exists(LEASE_FILE): return ""
    out = sh("cat %s 2>/dev/null" % LEASE_FILE)
    for line in out.splitlines():
        parts=line.split()
        if len(parts)>=4 and (parts[3].lower().startswith("c520ws") or "tapo" in parts[3].lower() or "tp-link" in parts[3].lower()):
            return parts[2]
    return ""

def from_arp():
    out = sh(f"ip neigh show dev {ETH_IFACE}")
    for line in out.splitlines():
        token=line.split()[0]
        if token.count(".")==3: return token
    return ""

def from_onvif(timeout=20):
    wsd=WSDiscovery(); wsd.start()
    qname=QName("http://www.onvif.org/ver10/network/wsdl","NetworkVideoTransmitter")
    t0=time.time(); ip=""
    while time.time()-t0<timeout and not ip:
        for svc in wsd.searchServices(types=[qname], timeout=3):
            for xa in svc.getXAddrs() or []:
                low=xa.lower()
                if "tapo" in low or "tp-link" in low:
                    ip=xa.split("//",1)[1].split("/")[0].split(":")[0]; break
            if ip: break
    wsd.stop()
    return ip

def main():
    ip = from_leases() or from_arp() or from_onvif()
    with open(IP_FILE,"w") as f: f.write((ip or "")+"\n")
    print(f"[discover] ip={ip or 'NONE'}")

if __name__=="__main__": main()
