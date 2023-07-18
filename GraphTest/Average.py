import datetime
from connector import *

def getData(servernums, starttime, cursor):
    server_list = "', '".join(servernums)
    query = "SELECT * FROM test.ping_data WHERE server_hostname IN ('{}') AND ping_time >= %s".format(server_list)
    cursor.execute(query, (starttime,))
    results = cursor.fetchall()
    # Retrieve column names from the cursor description
    column_names = [desc[0] for desc in cursor.description]

    data = [dict(zip(column_names, row)) for row in results]
    return data,results

def getAveragePing(servernums, since, cursor):
    averages = []
    results = []

    data,passedResults = getData(servernums, since, cursor)

    for server in servernums:
        server_data = [row for row in data if row['server_hostname'] == server]
        total = 0
        count = 0

        for row in server_data:
            value = row['ping_latency_ns']
            total += value
            count += 1

        if count > 0:
            average = total / count
        else:
            average = float("inf")

        averages.append(average)
        results.append(server_data)

    return averages, passedResults
