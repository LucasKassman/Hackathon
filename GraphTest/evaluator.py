from Average import *
from graphtest import *

def getServers2(cursor):

    query = "SELECT server FROM server_list WHERE valid= 'TRUE'"
    cursor.execute(query)
    results = cursor.fetchall()
    #print(results)
    # return just the server element, i.e. first item in the tuple
    return list(zip(*results))[0]
    #return results

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

    sorted_aves = sorted(aves.items(), key=lambda x: x[1])
    #print("aves", aves)
    #print("sorted_aves", sorted_aves)
    top_five = sorted_aves[:5] # just testing how to get the first five, really need the lowest 'n'
    #print("top_five: ", top_five)
    top_five_servers = list(zip(*top_five))[0] # just pull out the server name
    print("top_five_servers: ", top_five_servers)
    print("raw_data for", top_five_servers[0], server_data[top_five_servers[0]])
    print(type(server_data[top_five_servers[0]][0][0]))

    plot_data = {}
    for s in top_five_servers:
        plot_data[s] = {"timestamps":list(zip(*server_data[s]))[0],"goodness":list(zip(*server_data[s]))[1]}
        print("----", s, ":", plot_data[s])
        #return  # for debug, only print the first one for  now...
  
    plotIt(plot_data)

evaluate()

t = ((datetime.datetime(2023, 7, 12, 0, 11, 43), 333708, 'oldschool5.runescape.com', 'us-east-2', 1), (datetime.datetime(2023, 7, 12, 0, 12, 54), 99594, 'oldschool5.runescape.com', 'us-east-2', 1), (datetime.datetime(2023, 7, 12, 0, 13, 58), 65037, 'oldschool5.runescape.com', 'us-east-2', 1), (datetime.datetime(2023, 7, 12, 0, 15, 2), 81563, 'oldschool5.runescape.com', 'us-east-2', 1), (datetime.datetime(2023, 7, 12, 0, 16, 6), 72905, 'oldschool5.runescape.com', 'us-east-2', 1), (datetime.datetime(2023, 7, 12, 0, 17, 10), 92818, 'oldschool5.runescape.com', 'us-east-2', 1), (datetime.datetime(2023, 7, 12, 0, 18, 14), 101927, 'oldschool5.runescape.com', 'us-east-2', 1), (datetime.datetime(2023, 7, 12, 0, 19, 18), 70962, 'oldschool5.runescape.com', 'us-east-2', 1), (datetime.datetime(2023, 7, 12, 0, 20, 23), 80657, 'oldschool5.runescape.com', 'us-east-2', 1), (datetime.datetime(2023, 7, 12, 0, 21, 27), 66247, 'oldschool5.runescape.com', 'us-east-2', 1), (datetime.datetime(2023, 7, 12, 0, 22, 31), 81030, 'oldschool5.runescape.com', 'us-east-2', 1), (datetime.datetime(2023, 7, 12, 0, 23, 35), 86247, 'oldschool5.runescape.com', 'us-east-2', 1), (datetime.datetime(2023, 7, 12, 0, 24, 39), 73301, 'oldschool5.runescape.com', 'us-east-2', 1), (datetime.datetime(2023, 7, 12, 0, 25, 43), 87502, 'oldschool5.runescape.com', 'us-east-2', 1), (datetime.datetime(2023, 7, 12, 0, 26, 47), 94571, 'oldschool5.runescape.com', 'us-east-2', 1), (datetime.datetime(2023, 7, 12, 0, 27, 51), 95156, 'oldschool5.runescape.com', 'us-east-2', 1), (datetime.datetime(2023, 7, 12, 0, 28, 56), 107181, 'oldschool5.runescape.com', 'us-east-2', 1), (datetime.datetime(2023, 7, 12, 0, 29, 59), 73072, 'oldschool5.runescape.com', 'us-east-2', 1), (datetime.datetime(2023, 7, 12, 0, 31, 3), 94988, 'oldschool5.runescape.com', 'us-east-2', 1), (datetime.datetime(2023, 7, 12, 0, 32, 8), 98195, 'oldschool5.runescape.com', 'us-east-2', 1), (datetime.datetime(2023, 7, 12, 0, 33, 13), 98417, 'oldschool5.runescape.com', 'us-east-2', 1), (datetime.datetime(2023, 7, 12, 0, 34, 17), 106730, 'oldschool5.runescape.com', 'us-east-2', 1), (datetime.datetime(2023, 7, 12, 0, 35, 21), 82280, 'oldschool5.runescape.com', 'us-east-2', 1))

#print(list(zip(*t))[0])