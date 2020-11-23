#!/usr/bin/env python3
import requests,time,random,threading
from concurrent.futures import ThreadPoolExecutor,as_completed
import config
class Node:
    def __init__(self,ip):
        self.ip=ip
        self.respond=0
        self.speed=(0,0)
    def Respond(self,count=1,verbose=0):
        headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36'}
        for i in range(config.respond['retry']):
            r=requests.get(url="http://%s/cdn-cgi/trace"%self.ip,headers=headers,timeout=config.respond['timeout']/1000)
            if r.status_code==200:break            
        if r.status_code==200:
            self.respond=r.elapsed.total_seconds()*1000
        if verbose:print(self.ip,self.respond)
def MB(s):
    return s/1024/1024
def Progress(p):
    l=20
    return "[{}] {:.2%}".format(('#'*(int(p*l))).ljust(l,'.'),p)
def respondAll():
    executor=ThreadPoolExecutor(max_workers=config.respond['threads'])
    tasks=[executor.submit(node.Respond) for node in nodes]
    done=0;lss=''
    for task in as_completed(tasks):
        print('\b'*len(lss),end='',flush=1)
        done+=1
        lss='Testing Respond %s %d/%d'%(Progress(done/len(nodes)),done,len(nodes))
        print(lss,end='',flush=1)
    print('')
def speedtest(ip,verbose=1):
    url='http://%s/__down?bytes=%d'%(ip,config.speedtest['size'])
    headers={
        'Host':'speed.cloudflare.com',
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36'
    }
    try:r=requests.get(url,headers=headers,stream=True,timeout=config.respond['timeout']/1000)
    except:return 0,0
    if r.status_code!=200:return 0,0        
    s,lst,ti,lss=0,0,time.time(),''
    mx,avg=0,0
    st=time.time()
    try:
        for chunk in r.iter_content(chunk_size=256):
            if not chunk:continue
            s+=len(chunk)
            t=time.time()-ti
            if t<0.5:continue
            p=s/config.speedtest['size']
            speed=MB(s-lst)/t
            lst=s
            mx=max(mx,speed)
            if verbose:
                print('\b'*(len(lss)),end='',flush=1)
                lss='{} {} {:>6.2f}MB/s'.format(ip,Progress(p),speed)
                print(lss,end='',flush=1)
            ti=time.time()
            if ti-st>config.speedtest['skip']['time'] and mx<config.speedtest['skip']['speed']:
                print('\b'*len(lss),end='',flush=1)
                avg=MB(s/(ti-st))
                print("{:<16} | avg: {:>6.2f}MB/s | max: {:>6.2f}MB/s".format(ip,avg,mx))
                return avg,mx
    except:
        if verbose:print('\b'*len(lss),end='',flush=1)
        return 0,0
    ed=time.time()
    if ed-st<0.1:return 0,0
    avg=MB(config.speedtest['size']/(ed-st))
    if verbose:
        print('\b'*len(lss),end='',flush=1)
        print("{:<16} | avg: {:>6.2f}MB/s | max: {:>6.2f}MB/s".format(ip,avg,mx))
    return avg,mx

def op():
    ret=open('result.csv','w',encoding='utf-8')
    ret.write("{:<16}, {:<8}, {:<6}, {:<6}\n".format("IP","Respond","Avg(MB/s)","Max(MB/s)"))
    for node in nodes:
        ret.write("{:<16}, {:<8.2f}, {:<6.2f}, {:<6.2f}\n".format(node.ip,node.respond,node.speed[0],node.speed[1]))

nodes=[Node(ip) for ip in open('ips.txt').read().split('\n')]
respondAll()
nodes.sort(key=lambda node:node.respond if node.respond>0 else 1e9)
if not config.result['all']:
    nodes=nodes[:config.speedtest['count']]
op()
for node in nodes[:config.speedtest['count']]:
    node.speed=speedtest(node.ip)
nodes.sort(key=lambda node:node.speed,reverse=True)
op()