import os
import mysql.connector

user_base = "3vSfJtobEVWYyYX"

from pathlib import Path
file_dir = Path(__file__).resolve().parent
ssl_cert_path = file_dir / 'root_certs' / 'cacert-2023-05-30.pem'
ssl_cert_pathname = str(ssl_cert_path.absolute())

def get_user_base():
    return user_base

def get_password_from_file(user):
    with open(Path(__file__).resolve().parent / "passwords" / f"{user}_password.txt") as f:
        return f.read().strip()

def get_connection(user="root", ssl=True):
    password = get_password_from_file(user)
    mysql_config = {
        'user': f"{user_base}.{user}",
        'password': password,
        'host': 'gateway01.us-east-1.prod.aws.tidbcloud.com',
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
    return get_connection('testDB_reader')

def execute_sql(connection, sql, params=None, **kwargs):
    with connection.cursor() as cursor:
        if params is not None:
            cursor.execute(sql, params, **kwargs)
        else:
            cursor.execute(sql, **kwargs)
        res = cursor.fetchall()
    connection.commit()
    return res
