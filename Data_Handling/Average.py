import datetime
import math
from connector import *

def getData(servernums, starttime, cursor):
    server_list = "', '".join(servernums)
    query = """SELECT * FROM test.ping_data 
        INNER JOIN server_dimension USING (server_key) 
        WHERE server_hostname IN ('{}') 
        AND ping_time >= %s 
        AND ping_type = 0""".format(server_list)
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
    weight = exponential_decay(seconds_apart, .0001)
    return value,weight


def getAveragePing(servernums, since, cursor,first_time):
    averages = []
    weightedAverages = []
    results = []
    variances = []

    data,passedResults = getData(servernums, since, cursor)

    for server in servernums:
        server_data = [row for row in data if row['server_hostname'] == server]
        total = 0
        count = 0
        totalWeighted = 0
        total_weight = 0

        for row in server_data:

            value,incremental_weight = calculateWeight(row, first_time)
            if value != None:

                weighted = value * incremental_weight
                totalWeighted += weighted
                total_weight += incremental_weight
                total += value
                count += 1

        if count > 0:
            average = total / count
            weightedAverage = totalWeighted / total_weight
        else:
            average = float("inf")
            weightedAverage = float('int')

        averages.append(average)
        weightedAverages.append(weightedAverage)
        results.append(server_data)

        #calculating variance of each server

        total_variance = 0
        for row in server_data:
            value, incremental_weight = calculateWeight(row, first_time)
            if value != None:
                weighted_sq_deviation = incremental_weight * (value - weightedAverage) ** 2
                total_variance += weighted_sq_deviation

        variances.append(total_variance / total_weight)
    return averages, passedResults, weightedAverages, variances


