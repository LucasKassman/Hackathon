from connector import *

with get_connection() as connection:
    execute_sql(connection, """
        CREATE TABLE IF NOT EXISTS ping_data(
            ping_time timestamp,
            ping_latency_ns integer,
            server_hostname text,
            location text,
            ping_type smallint
        );
    """)
