import cachetools.func
from cachetools import cached
from cachetools import TTLCache
from cachetools.keys import hashkey
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

SERVER_KEY_CACHE_MISSES = 0

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(funcName)s(): %(message)s'
)

try:
    from tcppinglib import tcpping
except ModuleNotFoundError:
    logging.warning("tcp_ping (ping type 2) will not work. Other pings are fine")

from connector import get_connection, execute_sql
from location_utils import *

server_key_cache = TTLCache(maxsize=4096, ttl=86400)
location_key_cache = TTLCache(maxsize=64, ttl=3600)

@cached(
    server_key_cache,
    # Remove connection from the key
    key = lambda
        connection,
        server_ip,
        server_hostname,
        world_location_label,
        world_number,
        world_types,
        world_activity
    :
        hashkey(
        server_ip,
        server_hostname,
        world_location_label,
        world_number,
        world_types,
        world_activity
    )
)
def get_server_key(
    connection,
    server_ip,
    server_hostname,
    world_location_label,
    world_number,
    world_types,
    world_activity,
):
    global SERVER_KEY_CACHE_MISSES
    SERVER_KEY_CACHE_MISSES += 1
    #logging.info(f"Missed cache for {world_number}")
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

def get_server_information(connection, worlds, server_ips=None):
    global SERVER_KEY_CACHE_MISSES
    SERVER_KEY_CACHE_MISSES = 0
    if not server_ips:
        server_ips = get_ipv4_from_hostname_batch(
            [world["address"] for world in worlds]
        )

    longest_type_list = 0
    hostnames = []
    server_keys = []
    player_counts = []
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

    print(
        f"There were {SERVER_KEY_CACHE_MISSES} server_key cache misses in get_server_information"
    )
    return server_keys, player_counts

@cached(
    location_key_cache,
    # Remove connection from the key
    key = lambda connection, ip_address : hashkey(ip_address)
)
def get_location_key(connection, ip_address):
    print(f"location_key cache miss for {ip_address}")
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

def get_my_location_key(connection):
    my_ip = requests.get("http://ifconfig.me").text
    return get_location_key(connection, my_ip)

def get_my_location_key_with_retries(connection):
    while True:
        try:
            location_key = get_my_location_key(connection)
            break
        except Exception as e:
            logging.exception("Failed to determine location! Trying again in 60s...")
            time.sleep(60)
    return location_key

def measure_tcp_ping_request(hostname):
    # https://pypi.org/project/tcppinglib/
    start_time = datetime.datetime.utcnow()
    response = tcpping(hostname, count=1)
    latency_ns = round(response.avg_rtt * 1000) # avg_rtt already in ms
    return start_time, latency_ns, response.ip_address

def measure_head_request(hostname):
    start_time = datetime.datetime.utcnow()
    try:
        latency = requests.head(f"http://{hostname}").elapsed.total_seconds()
        latency_ns = round(latency * 1000000)
    except Exception:
        logging.exception("Failed to run HTTP HEAD request!")
        latency_ns = None
    return start_time, latency_ns, None

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

    return start_time, latency_ns, None


def create_ping_data_records(
    start_times, latencies, server_keys, player_counts, ping_type, location_key,
):
    records = []
    for start_time, latency, server_key, player_count in zip(
        start_times, latencies, server_keys, player_counts
    ):
        records.append(
            [start_time, latency, server_key, player_count, ping_type, location_key]
        )
    return records

def measure_latencies(measure_function, hostnames):
    futures = []
    start_times = []
    latencies = []
    ipv4_addrs = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        for hostname in hostnames:
            futures.append(executor.submit(measure_function, hostname))
        for future in futures: # Note: cannot use as_completed without tweaks; it will mess with the order
            start_time, latency, ipv4_addr = future.result()
            start_times.append(start_time)
            latencies.append(latency)
            if ipv4_addr:
                ipv4_addrs.append(ipv4_addr)

    return start_times, latencies, ipv4_addrs

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


def measure_and_format_latencies(connection, location_key=None, ping_type=0):
    if ping_type == 0:
        measure_function = measure_ping_request
    elif ping_type == 1:
        measure_function = measure_head_request
    elif ping_type == 2:
        measure_function = measure_tcp_ping_request
    else:
        raise Exception("Invalid ping_type {ping_type} specified!")

    if location_key is None:
        location_key = get_my_location_key(connection)

    worlds = query_world_info()
    hostnames = [world["address"] for world in worlds]

    start_times, latencies, ipv4_addrs = measure_latencies(
        measure_function, hostnames
    )

    server_keys, player_counts = get_server_information(
        connection, worlds, ipv4_addrs
    )

    records = create_ping_data_records(
        start_times=start_times,
        latencies=latencies,
        server_keys=server_keys,
        player_counts=player_counts,
        ping_type=ping_type,
        location_key=location_key,
    )
    return records

def store_ping_and_head_latencies(connection, i):
    location_key = get_my_location_key_with_retries(connection)

    records = measure_and_format_latencies(connection, location_key, ping_type=2)
    if i % 5 == 0: # measure ICMP pings a fifth as often
        records += measure_and_format_latencies(connection, location_key, ping_type=0)
    if i % 10 == 0: # measure head requests a tenth as often
        # This does call get_server_key twice, but it's fine since it's cached!
        records += measure_and_format_latencies(connection, location_key, ping_type=1)

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
