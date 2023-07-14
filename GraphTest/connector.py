import os
import MySQLdb

jacob = False
current_dir = os.getcwd()
parent_dir = os.path.dirname(current_dir)
ssl_cert_path = os.path.join(parent_dir,'root_certs/cacert-2023-05-30.pem')
if jacob:
    with open(os.path.expanduser("~/.ssh/tidb_password")) as f:
        password = f.read().strip("\n")
    user_base = "3SrUVoPGAkHxoe1"
else:
    user_base = "4P4Mongv3vUVSHz"
    password = "IimED29zRmjOxOPU"


def get_user_base():
    return user_base


def get_connection():
    return MySQLdb.connect(
    host="gateway01.eu-central-1.prod.aws.tidbcloud.com",
    port=4000,
    user=f"{user_base}.root",
    password=password,
    database="test",
    ssl_mode="VERIFY_IDENTITY",
    ssl={
      "ca": ssl_cert_path
      }
    )


def execute_sql(connection, sql, params=None):
    with connection.cursor() as cursor:
        if params is not None:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)
        res = cursor.fetchall()
    connection.commit()
    return res
