import time
import datetime
import MySQLdb
import requests
import json

from connector import get_connection, execute_sql

with open("servers.json") as f:
    hostnames = json.load(f)["valid_servers"]

def store_head_requests(connection):
    my_ip = requests.get("http://ifconfig.me").text
    latencies = []
    times = []

    for hostname in hostnames:
        response = requests.head(f"http://{hostname}")
        latencies.append(response.elapsed.total_seconds())
        times.append(datetime.datetime.now())

    print(latencies)
    records = []
    for hostname, latency, times in zip(hostnames, latencies, times):
        records.append(
            (datetime.datetime.now(), int(latency*1000000), hostname, "us-east-2", 1, my_ip),
        )

    with connection.cursor() as cursor:
        cursor.executemany("""
            INSERT INTO ping_data(
                ping_time,
                ping_latency_ns,
                server_hostname,
                location,
                ping_type,
                ip_addr
            ) VALUES (
                %s, %s, %s, %s, %s, %s
            );
        """, records
        )
    connection.commit()
    print(f"saved {len(hostnames)} head requests infos")

'''
valid_servers = []
invalid_servers = []
for i in range(400):
    try:
        requests.head(f"http://oldschool{i+1}.runescape.com")
        valid_servers.append(f"oldschool{i+1}.runescape.com")
    except:
        invalid_servers.append(f"oldschool{i+1}.runescape.com")

import json
with open("servers.json", "w") as f:
    f.write(json.dumps({"valid_servers": valid_servers, "invalid_servers": invalid_servers}))
exit(0)
'''

prev_end_time = time.time()
with get_connection(user="ping_inserter", password="665404ebeb06") as connection:
    while True:
        store_head_requests(connection)
        end_time = time.time()
        elapsed = end_time - prev_end_time
        prev_end_time = end_time
        time.sleep(max(0, 60 - elapsed))
