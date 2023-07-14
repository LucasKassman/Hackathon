import datetime
from connector import *
def getAveragePing(servernum,cursor):
    #with get_connection() as connection:
        #with connection.cursor() as cursor:

            # example of you to create a query for a specific timeframe
            now = datetime.datetime.now()
            starttime = now - datetime.timedelta(days=2, hours=12, minutes=1)
            #print(starttime)

            #query = "SELECT ping_latency_ns FROM ping_data WHERE server_hostname = %s"
            query = "SELECT * from test.ping_data A where server_hostname='"+servernum+"' and A.ping_time >= '"+starttime.strftime("%Y-%m:%d %H:%M:%S")+"'"
            #print(query)
            #query = "SELECT ping_latency_ns, server_hostname FROM ping_data"
            #desired_value = 'desired_value'
            cursor.execute(query)
            results = cursor.fetchall()
            #print(results)

            total = 0
            count = 0
            for row in results:
                value = row[1]  # since we're getting the whole row and not just ping_latency_ns, need to index into ping_latency_ns
                total += value
                count += 1

            if count > 0:
                average = total / count
                #print("The average ping from world 1 is: ", average)
                #print("\nThe total was: ", total)
                #print("\nThe number of entries was: ",count)
                return average, results
            else:
                print("No results found for ", servernum)
                #ERROR MSG
                return float("inf"), {}












