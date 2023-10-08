import cachetools.func
import concurrent.futures
import socket
import time
import requests


# East/west seems to be jagex only config at-the-moment
# giving up for now, we could hardcode
# thought: store server IP

# server location
# https://github.com/runelite/api.runelite.net/blob/master/http-api/src/main/java/net/runelite/http/api/worlds/WorldRegion.java
# https://github.com/runelite/runelite/blob/b82bb71bd0db6703f31b2e66ba4bd106d683c737/runelite-client/src/main/java/net/runelite/client/game/WorldClient.java#L52
# curl https://api.runelite.net/runelite-1.10.9-SNAPSHOT/worlds.js
# curl https://api.runelite.net/runelite-1.10.8/worlds.js
# !!! https://api.runelite.net/runelite/worlds.js


# questionable usefulness
# https://github.com/runelite/runelite/blob/14dd3d2d24062f49eaae87724dee343009c18d8c/runelite-client/src/main/java/net/runelite/client/plugins/worldhopper/WorldTableRow.java#L47

def query_world_info():
    return requests.get("https://api.runelite.net/runelite/worlds.js").json()["worlds"]

@cachetools.func.ttl_cache(maxsize=4096, ttl=3600)
def get_world_location_label_from_integer(location_id):
    # https://github.com/runelite/api.runelite.net/blob/master/http-api/src/main/java/net/runelite/http/api/worlds/WorldRegion.java
    if location_id == 0:
        return "UNITED_STATES"
    elif location_id == 1:
        return "UNITED_KINGDOM"
    elif location_id == 3:
        return "AUSTRALIA"
    elif location_id == 7:
        return "GERMANY"
    else:
        return "UNKNOWN"

def get_ipv4_from_hostname(hostname):
    return socket.gethostbyname_ex(hostname)[2][0]

def get_ipv4_from_hostname_batch(hostnames):
    to_return = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=16) as executor:
        futures = []
        for hostname in hostnames:
            futures.append(executor.submit(get_ipv4_from_hostname, hostname))
        for future in futures: # Note: cannot use as_completed without tweaks; it will mess with the order
            to_return.append(future.result())
    return to_return

def split_to_batches_of_size(list_to_split, batch_size):
    batches = []
    for i in range(0, len(list_to_split), batch_size):
        batches.append(list_to_split[i:i+batch_size])
    return batches

def getLocationBatch(ip_addresses):
    endPoint = 'http://ip-api.com/batch?fields=country,countryCode,lat,lon,query'
    batches = split_to_batches_of_size(ip_addresses, 100)
    unsorted_results = []
    for i, batch in enumerate(batches):
        if i != 0:
            time.sleep(1)
        response = requests.post(endPoint, json=batch)
        response.raise_for_status()
        unsorted_results += response.json()

    results = []
    for ip_address in ip_addresses:
        for unsorted in unsorted_results:
            if unsorted["query"] == ip_address:
                unsorted["ip_address"] = ip_address
                results.append(unsorted)

    return results

def getLocation(ipAddr):
    endPoint = 'http://ip-api.com/json/%s?fields=country,countryCode,lat,lon'%(ipAddr)
    response = requests.get(endPoint)
    response.raise_for_status()
    return response.json()


if __name__ == "__main__":
    worlds = query_world_info()

    server_addresses = [world["address"] for world in worlds]

    start_time = time.time()
    threaded_server_ips = get_ipv4_from_hostname_batch(server_addresses)
    print(f"Threads took {time.time() - start_time}")

    #start_time = time.time()
    #server_ips = [get_ipv4_from_hostname(address) for address in server_addresses]
    #print(f"No threads took {time.time() - start_time}")
