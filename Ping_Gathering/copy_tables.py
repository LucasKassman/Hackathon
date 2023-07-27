import connector
import pickle
from Ping_Gathering import ping_saver


def write_server_table(connection):
    with open("server_dimension.table", "rb") as f:
        server_rows = pickle.load(f)
        with connection.cursor() as cursor:
            cursor.executemany("""
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
                    world_types ,
                    world_activity
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                );
            """, server_rows
            )
        connection.commit()

def write_location_table(connection):
    with open("location_dimension.table", "rb") as f:
        location_rows = pickle.load(f)
        with connection.cursor() as cursor:
            cursor.executemany("""
                INSERT INTO location_dimension(
                    location_key,
                    ip_address ,
                    country,
                    country_code,
                    latitude,
                    longitude
                ) VALUES (
                    %s, %s, %s, %s, %s, %s
                );
            """, location_rows
            )
        connection.commit()

def write_ping_data_table(connection):
    with open("ping_data.table", "rb") as f:
        ping_data_rows = pickle.load(f)
        print(ping_data_rows[0])
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
            """, ping_data_rows
            )
    connection.commit()

def write_tables(connection):
    write_location_table(connection)
    write_server_table(connection)
    write_ping_data_table(connection)

def copy_tables(connection):
    with open("server_dimension.table", "wb") as f:
        pickle.dump(connector.execute_sql(connection, "SELECT * FROM server_dimension"), f)

    with open("location_dimension.table", "wb") as f:
        pickle.dump(connector.execute_sql(connection, "SELECT * FROM location_dimension"), f)
    with open("ping_data.table", "wb") as f:
        pickle.dump(connector.execute_sql(connection, "SELECT * FROM ping_data"), f)

with connector.get_connection() as connection:
    # write_tables(connection)

    # copy_tables(connetion)
    pass

# debugging
'''
exit(0)
with open("ping_data.table", "rb") as f:
    result = pickle.load(f)
    print(result)
    import datetime
    print(datetime.datetime.utcnow() - result[0][0])

exit(0)

with open("server_dimension.table", "rb") as f:
    result = pickle.load(f)
    print(result)

exit(0)
'''
