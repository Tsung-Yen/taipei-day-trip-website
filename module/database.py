from mysql.connector import pooling
from dotenv import load_dotenv
import os
import json

load_dotenv()
try:
    pool = pooling.MySQLConnectionPool(
        pool_name = "taipeiPool",
        pool_reset_session = True,
        host = os.getenv("DBHOST"),
        port = 3306,
        user = os.getenv("DBUSER"),
        password = os.getenv("DBPASSWORD"),
        database = os.getenv("DBNAME"),
    )
except Exception as e:
    print(e)

#====================================
#景點
class Attraction:
    def attractions(name, startNum):
        try:
            connection = pool.get_connection()
            cursor = connection.cursor()
            sql = f"""select * from attractions where name 
            like '%{name}%' limit {startNum},12"""
            cursor.execute(sql)
            result = cursor.fetchall()
            connection.close()
            return result
        except Exception as e:
            connection.close()
            print(e)
            return 
    def attractionId(id):
        try:
            connection = pool.get_connection()
            cursor = connection.cursor()
            sql = f"""select * from attractions where 
            id = {id}"""
            cursor.execute(sql)
            result = cursor.fetchone()
            connection.close()
            return result
        except Exception as e:
            connection.close()
            print(e)
            return