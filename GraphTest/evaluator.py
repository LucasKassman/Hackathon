from Average import *

def getServers(cursor):

    query = "SELECT server FROM server_list WHERE valid= 'TRUE'"
    cursor.execute(query)
    results = cursor.fetchall()
    #print(results)
    return results


def evaluate(region = None):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            sl = getServers(cursor)
            lowest_avg = 1000000
            lowest_server = None
            for tuple in sl:

                av = getAveragePing(tuple[0],cursor)

                if (av < lowest_avg):

                    lowest_server = tuple[0]
                    lowest_avg=av
                    print("found lower: ", lowest_server, lowest_avg)

evaluate()


