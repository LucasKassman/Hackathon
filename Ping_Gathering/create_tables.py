from connector import *

with get_connection() as connection:
    execute_sql(connection, """
        CREATE TABLE IF NOT EXISTS location_dimension(
            -- If this causes a problem, change to AUTO_RANDOM bigint
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
            -- Consdier making server_key the primary key
            server_key SMALLINT UNSIGNED,
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
    execute_sql(
        connection,
        "CREATE INDEX IF NOT EXISTS server_hostname_index ON server_dimension(server_hostname) USING BTREE;"
    )

    execute_sql(connection, """
        CREATE TABLE IF NOT EXISTS ping_data(
            ping_time timestamp,
            ping_latency_ns integer,
            ping_type tinyint,
            location_key integer UNSIGNED REFERENCES location_dimension(location_key),
            player_count smallint,
            server_key smallint unsigned REFERENCES server_dimension(server_key)
        );
    """)
    execute_sql(
        connection,
        "CREATE INDEX IF NOT EXISTS ping_time_index ON ping_data (ping_time) USING BTREE;"
    )
    execute_sql(
        connection,
        "CREATE INDEX IF NOT EXISTS server_index ON ping_data (server_key) USING BTREE;"
    )
