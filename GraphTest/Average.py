from connector import *

with get_connection() as connection:
    with connection.cursor as cursor:
        query = "SELECT ping_latency_ns FROM ping_data WHERE server_hostname = oldschool1.runescape.com"
        desired_value = 'desired_value'
        cursor.execute(query, (desired_value,))
        results = cursor.fetchall()

        total = 0
        count = 0
        for row in results:
            value = row[0]
            total += value
            count += 1

        if count > 0:
            average = total / count
            print("The average ping from world 1 is: ", average)
        else:
            print("No results found.")
        cursor.close()
        connection.close()













