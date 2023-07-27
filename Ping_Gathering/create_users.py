from connector import *

def create_inserter_user(connection):
    inserter_password = "665404ebeb06"
    inserter_user = f"{get_user_base()}.ping_inserter"
    execute_sql(connection, f'''CREATE USER "{inserter_user}" IDENTIFIED BY '{inserter_password}';''')
    execute_sql(connection, f'''GRANT INSERT ON TABLE ping_data TO "{inserter_user}"''')
    execute_sql(connection, f'''GRANT INSERT, SELECT ON TABLE location_dimension TO "{inserter_user}"''')
    execute_sql(connection, f'''GRANT INSERT, SELECT ON TABLE server_dimension TO "{inserter_user}"''')

def create_reader_user(connection):
    reader_user = f"{get_user_base()}.testDB_reader"
    reader_password = "#%6mQjE5A#kKGQ$b"
    execute_sql(connection, f'''CREATE USER "{reader_user}" IDENTIFIED BY '{reader_password}';''')
    execute_sql(connection, f"GRANT SELECT ON test.* TO '{reader_user}'@'%'")

with get_connection() as connection:
    create_inserter_user(connection)
    create_reader_user(connection)

    # can show list of users by:
    #   SELECT * FROM mysql.user;
