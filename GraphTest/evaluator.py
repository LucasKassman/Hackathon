import pprint
from Average import *
from graphtest3 import *

#
# return a list of servers to probe.
def getServers(cursor):

    query = "SELECT server FROM server_list WHERE valid= 'TRUE'"
    cursor.execute(query)
    results = cursor.fetchall()
    #print(results)
    # return just the server element, i.e. first item in the tuple
    return list(zip(*results))[0]
    #return results

#
# return the most recent time for recorded ping data
def getLastPingTime(cursor):
    query = "SELECT max(ping_time) FROM test.ping_data"
    cursor.execute(query)
    results = cursor.fetchall()
    print(results)
    print(results[0])
    print(results[0][0])
    return results[0][0]

#
# Test version of "getServers" to limit the amount of processing we do during debug...
def getServers2(cursor):
    return [
        'oldschool1.runescape.com',
        'oldschool2.runescape.com',
        'oldschool3.runescape.com',
        'oldschool4.runescape.com',
        'oldschool5.runescape.com',
        'oldschool6.runescape.com',
        'oldschool7.runescape.com',
        'oldschool8.runescape.com',
        'oldschool9.runescape.com',
        'oldschool10.runescape.com'
        ]
        

#
# Evaluate all servers (TBD: for a given region)
def evaluate(region = None):
    aves = {}
    server_data = {}
    with get_connection() as connection:
        with connection.cursor() as cursor:
            starttime = getLastPingTime(cursor) - datetime.timedelta(hours=2)
            
            #sl = getServers(cursor)
            sl = getServers2(cursor)

            # need a way to store the lowest N servers, not just the lowest one...
            lowest_avg = float('inf')
            lowest_server = None

            for server in sl:
                av, raw_data = getAveragePing(server,starttime,cursor)
                #if server not in aves:
                aves[server] = av
                server_data[server] = raw_data

                if (av < lowest_avg):
                    lowest_server = server
                    lowest_avg=av
                    print("found lower: ", lowest_server, lowest_avg)


    TOP_N = 5
    #
    # Plot the top N performing servers

    # sort by the average pings (item [1]), smallest first
    sorted_aves = sorted(aves.items(), key=lambda x: x[1])
    #print("aves", aves)
    #print("sorted_aves", sorted_aves)

    # get the top N from the list
    top_servers = sorted_aves[:TOP_N]
    print("top_servers: ", top_servers)
    pprint.pprint(top_servers)
    # another example of list(zip()), strip off the averages and just get the server names
    top_server_names = list(zip(*top_servers))[0]
    
    #print("top_server_names: ", top_server_names)
    #print("raw_data for", top_server_names[0], server_data[top_server_names[0]])
    #print(type(server_data[top_server_names[0]][0][0]))  # makeing sure that the timestamp is a python datetime.datetime object...

    # get the data for the top servers into a format that the plot routine expects
    plot_data = {}
    for s in top_server_names:
        plot_data[s] = {"timestamps":list(zip(*server_data[s]))[0],"goodness":list(zip(*server_data[s]))[1]}
        #print("----", s, ":", plot_data[s])

    # okay, got the data, plot it!
    plotIt(plot_data)


evaluate()
