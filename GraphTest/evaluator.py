from Average import *
from graphtest import *

#
# return a list of servers to probe.
def getServers2(cursor):

    query = "SELECT server FROM server_list WHERE valid= 'TRUE'"
    cursor.execute(query)
    results = cursor.fetchall()
    #print(results)
    # return just the server element, i.e. first item in the tuple
    return list(zip(*results))[0]
    #return results

#
# Test version of "getServers" to limit the amount of processing we do during debug...
def getServers(cursor):
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
    now = datetime.datetime.now()
    starttime = now - datetime.timedelta(days=2, hours=12, minutes=1)
    with get_connection() as connection:
        with connection.cursor() as cursor:

            sl = getServers(cursor)

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


    #
    # Plot the top 5 performing servers

    # sort by the average pings (item [1]), smallest first
    sorted_aves = sorted(aves.items(), key=lambda x: x[1])
    #print("aves", aves)
    #print("sorted_aves", sorted_aves)

    # get just the top 5 from the list
    top_five = sorted_aves[:5] # just testing how to get the first five, really need the lowest 'n'
    #print("top_five: ", top_five)
    
    # another example of list(zip()), strip off the averages and just get the server names
    top_five_servers = list(zip(*top_five))[0]
    
    #print("top_five_servers: ", top_five_servers)
    #print("raw_data for", top_five_servers[0], server_data[top_five_servers[0]])
    #print(type(server_data[top_five_servers[0]][0][0]))

    # get the data for the top servers into a format that the plot routine expects
    plot_data = {}
    for s in top_five_servers:
        plot_data[s] = {"timestamps":list(zip(*server_data[s]))[0],"goodness":list(zip(*server_data[s]))[1]}
        #print("----", s, ":", plot_data[s])

    # okay, got the data, plot it!
    plotIt(plot_data)


evaluate()
