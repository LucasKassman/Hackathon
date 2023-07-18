# Be sure to replace the parameters in the following connection string.
# Requires mysqlclient package ('pip3 install mysqlclient'). Please check https://pypi.org/project/mysqlclient/ for install guide.

import MySQLdb
import os
import requests
import time
import datetime

with open(os.path.expanduser("~/.ssh/tidb_password")) as f:
    password = f.read().strip("\n")
user = "3SrUVoPGAkHxoe1.root"

password = "665404ebeb06"
user = "3SrUVoPGAkHxoe1.ping_inserter"
connection = MySQLdb.connect(
    host="gateway01.eu-central-1.prod.aws.tidbcloud.com",
    port=4000,
    user=user,
    password=password,
    database="test",
    ssl_mode="VERIFY_IDENTITY",
    ssl={
      "ca": "/etc/ssl/certs/ca-certificates.crt"
      }
    )

def execute_sql(connection, sql, params=None):
    with connection.cursor() as cursor:
        if params is not None:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)
        res = cursor.fetchall()
    connection.commit()
    return res

hostnames = [f"oldschool{i+1}.runescape.com" for i in range(2)]
latencies = []
times = []

#for hostname in hostnames:
#    response = requests.head(f"http://{hostname}")
#    latencies.append(response.elapsed.total_seconds())
#    times.append(datetime.datetime.now())

#print(latencies)
#print(times)
times = [datetime.datetime(2023, 7, 8, 14, 51, 43, 6461), datetime.datetime(2023, 7, 8, 14, 51, 43, 397302)]

#latencies = [0.232382, 0.412644]

#with connection:
    #execute_sql(connection, '''CREATE USER "3SrUVoPGAkHxoe1.ping_inserter" IDENTIFIED BY '665404ebeb06';''')
    #execute_sql(connection, '''GRANT INSERT ON TABLE ping_data TO "3SrUVoPGAkHxoe1.ping_inserter"''')
#exit(0)

with connection:
    execute_sql(connection, """
        CREATE TABLE IF NOT EXISTS ping_data(
            ping_time timestamp,
            ping_latency_ns integer,
            server_hostname text,
            location text,
            ping_type smallint
        );
    """)
    '''
    execute_sql(connection, """
        CREATE TYPE ping_type (
            ping_latency_ns integer,
            server_hostname text,
            location text
        );
    """)
    '''
    with connection.cursor() as cursor:
        for hostname, latency, times in zip(hostnames, latencies, times):
            cursor.execute("""
                INSERT INTO ping_data(
                    ping_time,
                    ping_latency_ns,
                    server_hostname,
                    location,
                    ping_type
                ) VALUES (
                    %s, %s, %s, %s, %s
                );
            """, (datetime.datetime.now(), int(latency*1000000), hostname, "Southern California", 1)
            )
        connection.commit()
    '''
    execute_sql(connection, """
        --ping_type[]
        CREATE OR REPLACE FUNCTION insert_ping_data(ping_batch text)
        RETURNS VOID AS $$
        INSERT INTO ping_data(
            ping_latency_ns,
            server_key,
            location_key
        )
        SELECT
            ping_latency_ns,
            insert_into_server_dimension(server_hostname),
            insert_into_location_dimension(location)
        FROM UNNEST(ping_batch)
        $$ LANGUAGE sql;
    """)
    '''
    print(execute_sql(connection, "SELECT * FROM ping_data ORDER BY ping_time DESC LIMIT 10;"))
