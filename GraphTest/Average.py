import datetime
import timedelta
import math
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


"""
Controls the weights, y is the difference of time, and k is
the constant which controls how fast the weights tend to 0.
If k is very large, the function will quickly tend to 0
"""
def exponential_decay(y,k):
    return math.exp(-k * y)

#Calculates the weights for each data point depending on how recent the data point is
def calculateWeight(row,reference_time):
    value = row['ping_latency_ns']
    row_time = row['ping_time']
    time_difference = abs(reference_time - row_time)
    seconds_apart = time_difference.total_seconds()
    weight = exponential_decay(seconds_apart, .001)
    value = value * weight
    return value



def getAveragePing(servernums, since, cursor):
    averages = []
    weightedAverages = []
    results = []

    data,passedResults = getData(servernums, since, cursor)

    for server in servernums:
        server_data = [row for row in data if row['server_hostname'] == server]
        total = 0
        count = 0
        totalWeighted = 0

        for row in server_data:
            weighted = calculateWeight(row, since)
            totalWeighted += weighted
            value = row['ping_latency_ns']
            total += value
            count += 1

        if count > 0:
            average = total / count
            weightedAverage = totalWeighted / count
        else:
            average = float("inf")
            weightedAverage = float('int')

        averages.append(average)
        weightedAverages.append(weightedAverage)
        results.append(server_data)

    return averages, passedResults, weightedAverages


