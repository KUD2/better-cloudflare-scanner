respond={
    'timeout':1000, # 1000ms
    'retry':3, # 重试次数
    'threads':200 # 线程数
}
speedtest={
    'count':30,
    'size':1048576*20, # 测速下载文件大小
    'skip':{
        'time':5,
        'speed':5
        # <time>秒后最高速度未达到<speed>MB/s时自动跳过
    }
}
result={
    'all':False # 导出所有结果
}