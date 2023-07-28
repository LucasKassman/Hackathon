import os
import mysql.connector

user_base = "3ZB6yqw3EiU7NBm"
root_password = "ZQvEIMYbAzIe4d7I"


from pathlib import Path
file_dir = Path(__file__).resolve().parent
ssl_cert_path = file_dir / 'root_certs' / 'cacert-2023-05-30.pem'
ssl_cert_pathname = str(ssl_cert_path.absolute())

def get_user_base():
    return user_base

def get_connection(user="root", password=root_password, ssl=True):
    mysql_config = {
        'user': f"{user_base}.{user}",
        'password': password,
        'host': 'gateway01.eu-central-1.prod.aws.tidbcloud.com',
        'database': 'test',
        'port': '4000',
    }
    # Perhaps we should not require these SSL checks?
    if ssl:
        mysql_config['ssl_verify_cert'] = True
        mysql_config['ssl_verify_identity'] = True
        mysql_config['ssl_ca'] = ssl_cert_pathname
    return mysql.connector.connect(**mysql_config)

def get_read_only_connection():
    return get_connection('testDB_reader', '#%6mQjE5A#kKGQ$b')

def execute_sql(connection, sql, params=None):
    with connection.cursor() as cursor:
        if params is not None:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)
        res = cursor.fetchall()
    connection.commit()
    return res
