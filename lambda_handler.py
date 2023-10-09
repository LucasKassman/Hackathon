from Ping_Gathering.ping_saver import *
from connector import *

def lambda_handler(event, lambda_context):
    if "resources" in event:
        if "ServerScope-TCP-Ping-Timer" in event["resources"][0]:
            ping_type = 2
        elif "ServerScope-Head-Request-Timer" in event["resources"][0]:
            ping_type = 1
        else:
            raise Exception("Triggered by unknown resource {event['resources']}")
    else:
        ping_type = 2

    print(event)
    with get_connection(user="lamb_ping_insert") as connection:


        records = measure_and_format_latencies(connection, ping_type=ping_type)

        save_records(connection, records)

        '''
        measure_function = measure_head_request

        location_key = get_my_location_key(connection)

        worlds = query_world_info()
        hostnames = [world["address"] for world in worlds]

        latencies, ipv4_addrs = measure_latencies(measure_function, hostnames)

        records = create_records()

        ip_addresses_out = []
        records = measure_latencies(
            measure_head_request, hostnames, server_keys, player_counts,
            [1, location_key], ip_addresses_out
        )

        hostnames, server_keys, player_counts = get_server_information(connection)

        records = measure_latencies(
            measure_head_request, hostnames, server_keys, player_counts,
            [1, location_key]
        )

        save_records(connection, records)
        '''
