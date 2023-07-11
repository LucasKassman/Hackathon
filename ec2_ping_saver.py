import time
import datetime
import MySQLdb
import requests

password = "665404ebeb06"
user = "3SrUVoPGAkHxoe1.ping_inserter"

connection = MySQLdb.connect(
    host="gateway01.eu-central-1.prod.aws.tidbcloud.com",
    port=4000,
    user=user,
    password=password,
    database="test",
    ssl_mode="VERIFY_IDENTITY",
    connect_timeout=5,
    ssl={
      "ca": "/etc/ssl/certs/ca-certificates.crt"
      }
    )

#with connection:
#    execute_sql(connection, f'''CREATE USER "{user}" IDENTIFIED BY '{password}';''')
#    execute_sql(connection, f'''GRANT INSERT ON TABLE ping_data TO "{user}"''')
#exit(0)

def execute_sql(connection, sql, params=None):
    with connection.cursor() as cursor:
        if params is not None:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)
        res = cursor.fetchall()
    connection.commit()
    return res

def store_head_requests(connection):

    hostnames = [f"oldschool{i+1}.runescape.com" for i in range(2)]
    latencies = []
    times = []

    for hostname in hostnames:
        response = requests.head(f"http://{hostname}")
        latencies.append(response.elapsed.total_seconds())
        times.append(datetime.datetime.now())

    print(latencies)
    #print(times)
    records = []
    for hostname, latency, times in zip(hostnames, latencies, times):
        records.append(
            (datetime.datetime.now(), int(latency*1000000), hostname, "Southern California", 1),
        )

    with connection.cursor() as cursor:
        cursor.executemany("""
            INSERT INTO ping_data(
                ping_time,
                ping_latency_ns,
                server_hostname,
                location,
                ping_type
            ) VALUES (
                %s, %s, %s, %s, %s
            );
        """, records
        )
    connection.commit()
    print(f"saved {len(hostnames)} head requests infos")

prev_end_time = time.time()
with connection:
    while True:
        store_head_requests(connection)
        end_time = time.time()
        elapsed = end_time - prev_end_time
        prev_end_time = end_time
        time.sleep(max(0, 1 - elapsed))
