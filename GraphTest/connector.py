import os
import MySQLdb

# Created a testDB_read user:
#       GRANT SELECT ON test.* TO '4P4Mongv3vUVSHz.testDB_reader'@'%';
# can show list of users by:
#   SELECT * FROM mysql.user;


current_dir = os.getcwd()
parent_dir = os.path.dirname(current_dir)
ssl_cert_path = os.path.join(parent_dir,'root_certs/cacert-2023-05-30.pem')
user_base = "4P4Mongv3vUVSHz"



def get_user_base():
    return user_base


def get_connection():
    return MySQLdb.connect(
    host="gateway01.eu-central-1.prod.aws.tidbcloud.com",
    port=4000,
    user=f"{user_base}.testDB_reader",
#    password=password,
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
