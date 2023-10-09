import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(funcName)s(): %(message)s'
)

from Ping_Gathering.ping_saver import *
from connector import *

CONNECTION = None
def get_cached_connection(user):
    # TOCONSIDER de-dupe - move to connector.py? Test w/ lambda
    global CONNECTION
    if CONNECTION is None:
        print("Establishing new connection")
        CONNECTION = get_connection(user=user)
    return CONNECTION

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

    # print(event)

    connection = get_cached_connection(user="lamb_ping_insert")
    # with get_connection(user="lamb_ping_insert") as connection:
    records = measure_and_format_latencies(connection, ping_type=ping_type)

    save_records(connection, records)

if __name__ == "__main__":
    lambda_handler({}, {})
