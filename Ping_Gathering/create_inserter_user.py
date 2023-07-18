from connector import *

inserter_password = "665404ebeb06"
inserter_user = f"{get_user_base()}.ping_inserter"
with get_connection() as connection:
    execute_sql(connection, f'''CREATE USER "{inserter_user}" IDENTIFIED BY '{inserter_password}';''')
    execute_sql(connection, f'''GRANT INSERT ON TABLE ping_data TO "{inserter_user}"''')
