import json

from connector import *
from location_utils import *

CONNECTION = None
def get_cached_connection(user):
    # TOCONSIDER de-dupe - move to connector.py? Test w/ lambda
    global CONNECTION
    if CONNECTION is None:
        print("Establishing new connection")
        CONNECTION = get_connection(user=user)
    return CONNECTION

def write_server_data(connection, server_tuples):
    with connection.cursor() as cursor:
        cursor.execute("""
            CREATE TEMPORARY TABLE unknown_servers (
                max_key smallint unsigned,
                server_hostname varchar(64),

                server_ip varchar(16),
                server_country varchar(32),
                server_country_code varchar(8),
                server_latitude decimal(11, 7),
                server_longitude decimal(11, 7),

                world_location_label varchar(32),
                world_number smallint,
                world_types varchar(128),
                world_activity varchar(128)
            );
            """
        )
        cursor.executemany("""
            INSERT INTO unknown_servers(
                max_key,
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
            ), max_existing_key AS (
                SELECT COALESCE(MAX(server_key), 0) AS max_key FROM server_dimension
            )
            SELECT max_key, server_hostname,
                server_ip, server_country, server_country_code, server_latitude, server_longitude,
                world_location_label, world_number, world_types, world_activity
            FROM record_to_insert
            LEFT JOIN existing_server ON TRUE
            CROSS JOIN max_existing_key
            WHERE existing_server.server_key IS NULL;
        """, server_tuples)
        cursor.execute("""
            INSERT INTO server_dimension(
                server_key,
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
            SELECT
                max_key + row_number() OVER (ORDER BY world_number) AS server_key,
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
            FROM unknown_servers;
        """
        )
    connection.commit()

def update_servers(connection):
    worlds = query_world_info()
    longest_type_list = 0
    server_ips = get_ipv4_from_hostname_batch([world["address"] for world in worlds])
    location_info = getLocationBatch(server_ips)
    server_tuples = []
    for world, location_info in zip(worlds, location_info):
        server_tuples.append(
            (
                world["address"],

                location_info["ip_address"],
                location_info["country"],
                location_info["countryCode"],
                location_info["lat"],
                location_info["lon"],

                get_world_location_label_from_integer(world["location"]),
                world["id"],
                json.dumps(world["types"]),
                world["activity"],
            )
        )
    write_server_data(connection, server_tuples)

def lambda_handler(event, context):
    connection = get_cached_connection(user="server_updater")
    update_servers(connection)

if __name__ == "__main__":
    with get_connection("server_updater") as connection:
        update_servers(connection)
