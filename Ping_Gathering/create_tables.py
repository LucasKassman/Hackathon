from connector import *

with get_connection() as connection:
    execute_sql(connection, """
        CREATE TABLE IF NOT EXISTS ping_data(
            ping_time timestamp,
            ping_latency_ns integer,
            server_hostname text,
            location text,
            ping_type smallint,
            ip_addr text,
            location_key integer,
        );
    """)

    execute_sql(connection, """
        CREATE TABLE IF NOT EXISTS location_dimension(
            location_key serial,
            ip_address text,
            country text,
            country_code text,
            latitude decimal(11, 7),
            longitude decimal(11, 7)
        )
    """)
