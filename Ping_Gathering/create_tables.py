from connector import *

with get_connection() as connection:
    execute_sql(connection, """
        CREATE TABLE IF NOT EXISTS ping_data(
            ping_time timestamp,
            ping_latency_ns integer,
            server_key smallint,
            ping_type tinyint,
            location_key integer,
            player_count smallint
        );
    """)

    execute_sql(connection, """
        CREATE TABLE IF NOT EXISTS location_dimension(
            location_key INT UNSIGNED NOT NULL AUTO_INCREMENT UNIQUE,
            ip_address varchar(16),
            country varchar(32),
            country_code varchar(8),
            latitude decimal(11, 7),
            longitude decimal(11, 7)
        )
    """)

    execute_sql(connection, """
        CREATE TABLE IF NOT EXISTS server_dimension(
            server_key SMALLINT UNSIGNED NOT NULL AUTO_INCREMENT UNIQUE,
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
        )
    """
    )
