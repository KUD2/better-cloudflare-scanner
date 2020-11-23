#!/usr/bin/env python3
import requests
iprs=requests.get("https://service.freecdn.workers.dev").text.split('\n')[6:]
if not iprs[-1]:iprs=iprs[:-1]
open("ips.txt","w").write('\n'.join(iprs))
