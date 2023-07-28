import datetime
import math
import copy
from connector import *
from Data_Handling.location import *

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
    for row in data:
        if row['ping_latency_ns'] != None:
            row['ping_latency_ns'] = row['ping_latency_ns'] / 1000
    return data


"""
Controls the weights, y is the difference of time, and k is
the constant which controls how fast the weights tend to 0.
If k is very large, the function will quickly tend to 0
"""
def exponential_decay(y,k):
    return math.exp(-k * y)


def get_distance_apart(location, location_data, location_key):
    latlocal = location['lat']
    lonlocal = location['lon']
    for row in location_data:
        if row[0] == location_key:
            location_data_row = row
    latref = float(location_data_row[4])
    lonref = float(location_data_row[5])
    distance_between = distance(latlocal, lonlocal, latref, lonref)
    return distance_between

#Calculates the weights for each data point depending on how recent the data point is
def calculateWeight(row,reference_time,location=None,location_data=None):

    value = row['ping_latency_ns']
    row_time = row['ping_time']
    time_difference = abs(reference_time - row_time)
    seconds_apart = time_difference.total_seconds()
    weight = exponential_decay(seconds_apart, .0001)


    if (location_data!=None):
        distance_apart = get_distance_apart(location, location_data, row['location_key'])
        weight = weight * exponential_decay(distance_apart, .001)


    return value,weight

def trim_data(data):
    for row in data:
        row_list = list(row)
        if (row_list[1] != None):

            row_list[1] = row_list[1] / 1000
        updated_row = tuple(row_list)
        row = updated_row


def getAveragePing(servernums, since, cursor,first_time,location,location_data):
    averages = []
    weightedAverages = []
    results = []
    variances = []
    display_data = []


    data= getData(servernums, since, cursor)
    #trim_data(passedResults)
    print("first time variable:", since)

    for server in servernums:
        server_data = [row for row in data if row['server_hostname'] == server]
        total = 0
        count = 0
        totalWeighted = 0
        total_weight = 0
        time_block_begin = since
        current_running_data = {
            'ping_latency_ns': 0,
            'ping_time': time_block_begin,
            'total_weight': 0,
            'server_hostname': server
        }
        
        last_server="none"
        for row in server_data:
            time_block_current = row['ping_time']
            value,incremental_weight = calculateWeight(row, first_time,location,location_data)

            if value != None:
                weighted = value * incremental_weight
                totalWeighted += weighted
                total_weight += incremental_weight
                total += value
                count += 1
                current_running_data['ping_latency_ns'] += weighted
                current_running_data['total_weight'] += incremental_weight

                time_diff = abs(time_block_current - time_block_begin).total_seconds()
                #print("time delta: ", time_diff)
                #if time_diff > 180:
                if time_diff > 360:
                    current_running_data['ping_latency_ns'] = current_running_data['ping_latency_ns'] / current_running_data['total_weight']
                    time_block_begin = time_block_current
                    display_data.append(copy.copy(current_running_data))

                    current_running_data = {
                        'ping_latency_ns': 0,
                        'ping_time': time_block_begin,
                        'total_weight': 0,
                        'server_hostname': server
                    }
                    last_server = server

        #
        # flush out the end of the current server's data (if any has been collected since the last time)
        if current_running_data['ping_latency_ns'] != 0:
            current_running_data['ping_latency_ns'] = current_running_data['ping_latency_ns'] / current_running_data['total_weight']
            time_block_begin = time_block_current
            display_data.append(copy.copy(current_running_data))

        print("--------------------------")
        print(display_data)

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

    
    print("display data: ", display_data)
    #display_data.reverse()
    return averages, display_data, weightedAverages, variances


