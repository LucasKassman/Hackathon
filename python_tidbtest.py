# Be sure to replace the parameters in the following connection string.
# Requires mysqlclient package ('pip3 install mysqlclient'). Please check https://pypi.org/project/mysqlclient/ for install guide.

import MySQLdb
import os

with open(os.path.expanduser("~/.ssh/tidb_password")) as f:
    password = f.read().strip("\n")

connection = MySQLdb.connect(
    host="gateway01.eu-central-1.prod.aws.tidbcloud.com",
    port=4000,
    user="3SrUVoPGAkHxoe1.root",
    password=password,
    database="test",
    ssl_mode="VERIFY_IDENTITY",
    ssl={
      "ca": "/etc/ssl/certs/ca-certificates.crt"
      }
    )

with connection:
  with connection.cursor() as cursor:
      sql = """
        CREATE TABLE IF NOT EXISTS fake_pings(ping_time timestamp, ping_latency_ms integer);
      """
      insert_sql = """INSERT INTO fake_pings(ping_time, ping_latency_ms)
        VALUES (NOW(), 42);
      """

      cursor.execute(sql)
      cursor.execute(insert_sql)
      #cursor.commit()
      cursor.execute("SELECT * FROM fake_pings;")
      res = cursor.fetchall()
      print(res)
  connection.commit()
    #cursor.execute("SELECT DATABASE();")
    #m = cursor.fetchone()
    #print(m[0]) 
