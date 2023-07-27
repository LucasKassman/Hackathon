import cachetools.func
import concurrent.futures
import datetime
import json
import logging
import platform
import re
import requests
import socket
import subprocess
import time

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(funcName)s(): %(message)s'
)


from connector import get_connection, execute_sql

# East/west seems to be jagex only config at-the-moment
# giving up for now, we could hardcode
# thought: store server IP

# server location
# https://github.com/runelite/api.runelite.net/blob/master/http-api/src/main/java/net/runelite/http/api/worlds/WorldRegion.java
# https://github.com/runelite/runelite/blob/b82bb71bd0db6703f31b2e66ba4bd106d683c737/runelite-client/src/main/java/net/runelite/client/game/WorldClient.java#L52
# curl https://api.runelite.net/runelite-1.10.9-SNAPSHOT/worlds.js
# curl https://api.runelite.net/runelite-1.10.8/worlds.js
# !!! https://api.runelite.net/runelite/worlds.js


# questionable usefulness
# https://github.com/runelite/runelite/blob/14dd3d2d24062f49eaae87724dee343009c18d8c/runelite-client/src/main/java/net/runelite/client/plugins/worldhopper/WorldTableRow.java#L47

@cachetools.func.ttl_cache(maxsize=4096, ttl=86400)
def get_server_key(
    server_ip,
    server_hostname,
    world_location_label,
    world_number,
    world_types,
    world_activity,
):
    server_location = getLocation(server_ip)
    server_tuple = (
        server_hostname,

        server_ip,
        server_location["country"],
        server_location["countryCode"],
        server_location["lat"],
        server_location["lon"],

        world_location_label,
        world_number,
        world_types,
        world_activity,
    )

    execute_sql(
        connection,
        """
        INSERT INTO server_dimension(
            server_hostname,

            server_ip,
            server_country,
            server_country_code,
            server_latitude,
            server_longitude,

            world_location_label,
            world_number,
            world_types,
            world_activity
        )
        WITH record_to_insert AS (
        SELECT  %s AS server_hostname,
                %s AS server_ip,
                %s AS server_country,
                %s AS server_country_code,
                CAST(%s AS decimal(11,7)) AS server_latitude,
                CAST(%s AS decimal(11,7)) AS server_longitude,
                %s AS world_location_label,
                %s AS world_number,
                %s AS world_types,
                %s AS world_activity
        ), existing_server AS (
            SELECT server_key
            FROM server_dimension
            INNER JOIN record_to_insert
            USING (
                server_hostname,

                server_ip,
                server_country,
                server_country_code,
                server_latitude,
                server_longitude,

                world_location_label,
                world_number,
                world_types,
                world_activity
            )
        )
        SELECT server_hostname,
            server_ip, server_country, server_country_code, server_latitude, server_longitude,
            world_location_label, world_number, world_types, world_activity
        FROM record_to_insert
        LEFT JOIN existing_server ON TRUE
        WHERE existing_server.server_key IS NULL;
        """,
        server_tuple,
    )
    return execute_sql(
        connection,
        """
        SELECT server_key
        FROM server_dimension
        WHERE server_hostname = %s

            AND server_ip = %s
            AND server_country = %s
            AND server_country_code = %s
            AND server_latitude = CAST(%s AS decimal(11,7))
            AND server_longitude = CAST(%s AS decimal(11,7))

            AND world_location_label = %s
            AND world_number = %s
            AND world_types = %s
            AND world_activity = %s
        """,
        server_tuple,
    )[0][0]

def get_world_location_label_from_integer(location_id):
    # https://github.com/runelite/api.runelite.net/blob/master/http-api/src/main/java/net/runelite/http/api/worlds/WorldRegion.java
    if location_id == 0:
        return "UNITED_STATES"
    elif location_id == 1:
        return "UNITED_KINGDOM"
    elif location_id == 3:
        return "AUSTRALIA"
    elif location_id == 7:
        return "GERMANY"
    else:
        return "UNKNOWN"

@cachetools.func.ttl_cache(maxsize=4096, ttl=3600)
def get_ipv4_from_hostname(hostname):
    return socket.gethostbyname_ex(hostname)[2][0]

def query_world_info():
    return requests.get("https://api.runelite.net/runelite/worlds.js").json()["worlds"]

def get_server_information():
    worlds = query_world_info()
    longest_type_list = 0
    hostnames = []
    server_keys = []
    player_counts = []
    for world in worlds:
        server_ip = get_ipv4_from_hostname(world["address"])
        print(server_ip)
        server_key = get_server_key(
            server_ip,
            world["address"],
            get_world_location_label_from_integer(world["location"]),
            world["id"],
            json.dumps(world["types"]),
            world["activity"],
        )
        server_keys.append(server_key)
        hostnames.append(world["address"])
        player_counts.append(world["players"])
    return hostnames, server_keys, player_counts

def split_to_batches_of_size(list_to_split, batch_size):
    batches = []
    for i in range(0, len(list_to_split), batch_size):
        batches.append(list_to_split[i:i+batch_size])
    return batches

def getLocationBatch(ip_addresses):
    endPoint = 'http://ip-api.com/batch?fields=country,countryCode,lat,lon'
    batches = split_to_batches_of_size(ip_addresses, 100)
    results = []
    for i, batch in enumerate(batches):
        print(len(batch))
        print(batch)
        #continue
        if i != 0:
            time.sleep(1)
        response = requests.post(endPoint, json=batch)
        response.raise_for_status()
        results += response.json()
    return results

def getLocation(ipAddr):
    endPoint = 'http://ip-api.com/json/%s?fields=country,countryCode,lat,lon'%(ipAddr)
    response = requests.get(endPoint)
    response.raise_for_status()
    return response.json()

@cachetools.func.ttl_cache(maxsize=64, ttl=3600)
def get_location_key(connection, ip_address):
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

def get_my_location_key():
    while True:
        try:
            my_ip = requests.get("http://ifconfig.me").text
            location_key = get_location_key(connection, my_ip)
            break
        except Exception as e:
            logging.exception("Failed to determine location! Trying again in 60s...")
            time.sleep(60)
    return location_key

def measure_head_request(hostname):
    start_time = datetime.datetime.utcnow()
    try:
        latency = requests.head(f"http://{hostname}").elapsed.total_seconds()
        latency_ns = round(latency * 1000000)
    except Exception:
        logging.exception("Failed to run HTTP HEAD request!")
        latency_ns = None
    return start_time, latency_ns

def measure_ping_request(hostname):
    param = "-n" if "windows" in platform.system().lower() else "-c"
    start_time = datetime.datetime.utcnow()
    result = None
    try:
        result = str(subprocess.check_output(["ping", param, "1", hostname]))
    except Exception:
        logging.exception("Failed to run ICMP ping!")
        latency_ns = None
    else: # if no exception
        try:
            m = re.search("time\s*=\s*([\d\.]+)\s*ms", result)
            ping_ms_string = m.group(1)
        except Exception:
            logging.exception(f"Failed to parse {result}!")
            latency_ns = None
        else: # if no exception
            try:
                latency_ns = round(float(ping_ms_string)*1000)
            except Exception:
                logging.exception(f"Failed to parse ping time of {ping_ms_string}")
                latency_ns = None

    return start_time, latency_ns


def measure_latencies(measure_function, hostnames, server_keys, player_counts, extra_rows = []):
    futures = []
    start_times = []
    latencies = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        for hostname in hostnames:
            futures.append(executor.submit(measure_function, hostname))
        for future in futures:
            start_time, latency = future.result()
            start_times.append(start_time)
            latencies.append(latency)

    records = []
    for server_key, latency, start_time, player_count in zip(server_keys, latencies, start_times, player_counts):
        records.append(
            [start_time, latency, server_key, player_count] + extra_rows
        )
    logging.info(f"Finished running {measure_function.__name__} {len(hostnames)} times")
    return records

def save_records(connection, records):
    with connection.cursor() as cursor:
        cursor.executemany("""
            INSERT INTO ping_data(
                ping_time,
                ping_latency_ns,
                server_key,
                player_count,
                ping_type,
                location_key
            ) VALUES (
                %s, %s, %s, %s, %s, %s
            );
        """, records
        )
    connection.commit()
    logging.info(f"saved {len(records)} ping measurements")

def store_ping_and_head_latencies(connection, i):
    location_key = get_my_location_key()

    hostnames, server_keys, player_counts = get_server_information()

    records = measure_latencies(measure_ping_request, hostnames, server_keys, player_counts, [0, location_key])
    if i % 10 == 0: # measure head requests a tenth as often
        records += measure_latencies(measure_head_request, hostnames, server_keys, player_counts, [1, location_key])

    save_records(connection, records)

if __name__ == "__main__":
    logging.info("Starting up")
    prev_end_time = time.time()
    with get_connection(user="ping_inserter", password="665404ebeb06") as connection:
        i = 0
        while True:
            store_ping_and_head_latencies(connection, i)
            end_time = time.time()
            elapsed = end_time - prev_end_time
            prev_end_time = end_time
            sleep_time = max(0, 60 - elapsed)
            logging.info(f"Waiting {sleep_time:.2f} seconds until next round of pings...")
            time.sleep(sleep_time)
            i += 1
