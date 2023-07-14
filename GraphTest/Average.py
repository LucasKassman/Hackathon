import datetime
from connector import *
def getAveragePing(servernum,cursor):
    #with get_connection() as connection:
        #with connection.cursor() as cursor:

            now = datetime.datetime.now()
            starttime = now - datetime.timedelta(days=1, hours=12, minutes=1)
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
                value = row[1]
                total += value
                count += 1

            if count > 0:
                average = total / count
                #print("The average ping from world 1 is: ", average)
                #print("\nThe total was: ", total)
                #print("\nThe number of entries was: ",count)
                return average
            else:
                print("No results found for ", servernum)
                #ERROR MSG












