from connector import *

def create_inserter_user(connection):
    inserter_password = get_password_from_file("ping_inserter")
    inserter_user = f"{get_user_base()}.ping_inserter"
    execute_sql(connection, f'''CREATE USER "{inserter_user}" IDENTIFIED BY '{inserter_password}';''')
    execute_sql(connection, f'''GRANT INSERT ON TABLE ping_data TO "{inserter_user}"''')
    execute_sql(connection, f'''GRANT INSERT, SELECT ON TABLE location_dimension TO "{inserter_user}"''')
    execute_sql(connection, f'''GRANT SELECT ON TABLE server_dimension TO "{inserter_user}"''')

def create_lambda_ping_inserter_user(connection):
    lambda_inserter_password = get_password_from_file("lamb_ping_insert")
    lambda_inserter_user = f"{get_user_base()}.lamb_ping_insert"
    execute_sql(connection, f'''CREATE USER "{lambda_inserter_user}" IDENTIFIED BY '{lambda_inserter_password}';''')
    execute_sql(connection, f'''GRANT INSERT ON TABLE ping_data TO "{lambda_inserter_user}"''')
    execute_sql(connection, f'''GRANT INSERT, SELECT ON TABLE location_dimension TO "{lambda_inserter_user}"''')
    execute_sql(connection, f'''GRANT SELECT ON TABLE server_dimension TO "{lambda_inserter_user}"''')

def create_server_updater_user(connection):
    server_updater_password = get_password_from_file("server_updater")
    server_updater_user = f"{get_user_base()}.server_updater"
    execute_sql(connection, f'''CREATE USER "{server_updater_user}" IDENTIFIED BY '{server_updater_password}';''')
    execute_sql(connection, f'''GRANT SELECT, INSERT ON TABLE server_dimension TO "{server_updater_user}"''')
    execute_sql(connection, f'''GRANT CREATE TEMPORARY TABLES ON test.* TO "{server_updater_user}"''')

def create_reader_user(connection):
    reader_user = f"{get_user_base()}.testDB_reader"
    reader_password = get_password_from_file("testDB_reader")
    execute_sql(connection, f'''CREATE USER "{reader_user}" IDENTIFIED BY '{reader_password}';''')
    execute_sql(connection, f"GRANT SELECT ON test.* TO '{reader_user}'@'%'")

with get_connection() as connection:
    create_inserter_user(connection)
    create_lambda_ping_inserter_user(connection)
    create_server_updater_user(connection)
    create_reader_user(connection)

    # can show list of users by:
    #   SELECT * FROM mysql.user;
