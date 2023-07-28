from connector import *
def makeIndex(cursor):
     drop_server_index_query = "DROP INDEX IF EXISTS server_index ON ping_data"
     cursor.execute(drop_server_index_query)

     server_index_query = "CREATE INDEX server_index ON ping_data (server_key) USING BTREE"
     cursor.execute(server_index_query)

     drop_time_index_query = "DROP INDEX IF EXISTS ping_time_index ON ping_data"
     cursor.execute(drop_time_index_query)

     time_index_query = "CREATE INDEX ping_time_index ON ping_data (ping_time) USING BTREE"
     cursor.execute(time_index_query)

     check_index_query = "SELECT * FROM INFORMATION_SCHEMA.STATISTICS WHERE table_schema = 'test' AND table_name = 'ping_data' AND index_name = 'ping_time_index'"
     cursor.execute(check_index_query)
     index_info = cursor.fetchone()

     if index_info:
         print("Index was created successfully.")
     else:
         print("Index creation failed.")


with get_connection() as connection:
     with connection.cursor() as cursor:
        makeIndex(cursor)

