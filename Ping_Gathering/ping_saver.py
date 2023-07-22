import time
import datetime
import logging
import requests
import json

from connector import get_connection, execute_sql

with open("Ping_Gathering/servers.json") as f:
    hostnames = json.load(f)["valid_servers"]

def getLocation(ipAddr):
    endPoint = 'http://ip-api.com/json/%s?fields=country,countryCode,lat,lon'%(ipAddr)
    response = requests.get(endPoint)
    json = response.json()
    return json

def get_location_key(ip_address):
    location = getLocation(ip_address)
    location_tuple = (
        ip_address,
        location["country"],
        location["countryCode"],
        location["lat"],
        location["lon"],
    )
    execute_sql(
        connection,
        """
        INSERT INTO location_dimension(
            ip_address, country, country_code, latitude, longitude
        )
        WITH record_to_insert AS (
        SELECT  %s as ip_address,
                %s AS country,
                %s AS country_code,
                CAST(%s AS decimal(11,7)) AS latitude,
                CAST(%s AS decimal(11,7)) AS longitude
        ), existing_location AS (
            SELECT location_key
            FROM location_dimension
            INNER JOIN record_to_insert
            USING (ip_address, country, country_code, latitude, longitude)
        )
        SELECT ip_address, country, country_code, latitude, longitude
        FROM record_to_insert
        LEFT JOIN existing_location ON TRUE
        WHERE existing_location.location_key IS NULL;
        """,
        location_tuple,
    )
    return execute_sql(
        connection,
        """
        SELECT location_key
        FROM location_dimension
        WHERE ip_address = %s
            AND country = %s
            AND country_code = %s
            AND latitude = CAST(%s AS decimal(11,7))
            AND longitude = CAST(%s AS decimal(11,7))
        """,
        location_tuple,
    )[0][0]


def store_head_requests(connection):
    while True:
        try:
            my_ip = requests.get("http://ifconfig.me").text
            location_key = get_location_key(my_ip)
            break
        except Exception as e:
            logging.exception("Failed to determine location! Trying again in 60s...")
            time.sleep(60)
    latencies = []
    times = []

    for hostname in hostnames:
        times.append(datetime.datetime.now())
        try:
            response = requests.head(f"http://{hostname}")
            latencies.append(response.elapsed.total_seconds())
        except Exception:
            latencies.append(None)

    print(latencies)
    records = []
    for hostname, latency, times in zip(hostnames, latencies, times):
        records.append(
            (datetime.datetime.now(), int(latency*1000000), hostname, 1, location_key),
        )

    with connection.cursor() as cursor:
        cursor.executemany("""
            INSERT INTO ping_data(
                ping_time,
                ping_latency_ns,
                server_hostname,
                ping_type,
                location_key
            ) VALUES (
                %s, %s, %s, %s, %s
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
