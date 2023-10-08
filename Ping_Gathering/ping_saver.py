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
from location_utils import *


@cachetools.func.ttl_cache(maxsize=4096, ttl=86400)
def get_server_key(
    connection,
    server_ip,
    server_hostname,
    world_location_label,
    world_number,
    world_types,
    world_activity,
):
    server_tuple = (
        server_hostname,
        server_ip,

        world_location_label,
        world_number,
        world_types,
        world_activity,
    )

    server_key_rows = execute_sql(
        connection,
        """
        SELECT server_key
        FROM server_dimension
        WHERE
            server_hostname = %s
            AND server_ip = %s
            AND world_location_label = %s
            AND world_number = %s
            AND world_types = %s
            AND world_activity = %s
        """,
        server_tuple,
    )
    if len(server_key_rows) > 1:
        logging.warning(
            f"Found multiple keys {server_key_rows}"
            f" for server_tuple {server_tuple}"
        )
    if len(server_key_rows) == 0:
        logging.warning(f"Found no server_key {server_key_rows} for {server_tuple}")
        # TOCONSIDER also post to trigger the server updater
        return None

    return server_key_rows[0][0]

def get_server_information(connection):
    worlds = query_world_info()
    longest_type_list = 0
    hostnames = []
    server_keys = []
    player_counts = []
    server_ips = get_ipv4_from_hostname_batch([world["address"] for world in worlds])
    for world, server_ip in zip(worlds, server_ips):
        server_key = get_server_key(
            connection,
            server_ip,
            world["address"],
            get_world_location_label_from_integer(world["location"]),
            world["id"],
            json.dumps(world["types"]),
            world["activity"],
        )
        if server_key is None:
            continue
        server_keys.append(server_key)
        hostnames.append(world["address"])
        player_counts.append(world["players"])
    return hostnames, server_keys, player_counts


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
    with concurrent.futures.ThreadPoolExecutor(max_workers=16) as executor:
        for hostname in hostnames:
            futures.append(executor.submit(measure_function, hostname))
        for future in futures: # Note: cannot use as_completed without tweaks; it will mess with the order
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

    hostnames, server_keys, player_counts = get_server_information(connection)

    records = measure_latencies(measure_ping_request, hostnames, server_keys, player_counts, [0, location_key])
    if i % 10 == 0: # measure head requests a tenth as often
        records += measure_latencies(measure_head_request, hostnames, server_keys, player_counts, [1, location_key])

    save_records(connection, records)

if __name__ == "__main__":
    logging.info("Starting up")
    with get_connection(user="lamb_ping_insert") as connection:
        '''
        start_time = time.time()
        store_ping_and_head_latencies(connection, 5)
        print(f"Took {time.time() - start_time}")
        exit(0)
        '''
        i = 0
        while True:
            loop_start = time.time()
            store_ping_and_head_latencies(connection, i)
            elapsed = time.time() - loop_start
            sleep_time = max(0, 60 - elapsed)
            logging.info(f"Waiting {sleep_time:.2f} seconds until next round of pings...")
            time.sleep(sleep_time)
            i += 1
