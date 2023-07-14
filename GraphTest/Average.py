import datetime
from connector import *

def getData(servernum, starttime, cursor):
    query = "SELECT * from test.ping_data A where server_hostname='"+servernum+"' and A.ping_time >= '"+starttime.strftime("%Y-%m:%d %H:%M:%S")+"'"
    cursor.execute(query)
    results = cursor.fetchall()
    return results

def getAveragePing(servernum,since, cursor):
    

    results = getData(servernum, since, cursor)
    
    total = 0
    count = 0
    for row in results:
        value = row[1]  # since we're getting the whole row and not just ping_latency_ns, need to index into ping_latency_ns
        total += value
        count += 1

    if count > 0:
        average = total/count
    else:
        average = float("inf")
    
    return average, results
