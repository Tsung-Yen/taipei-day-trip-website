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
#attractions
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

#==================================
#Menber System
class Menber:
    def status(email):
        try:
            connection = pool.get_connection()
            cursor = connection.cursor()
            sql = f"""select * from user where email
            ='{email}'"""
            cursor.execute(sql)
            result = cursor.fetchone()
            connection.close()
            return True
        except Exception as e:
            connection.close()
            print(e)
            return
    def signup(data):
        try:
            connection = pool.get_connection()
            cursor = connection.cursor()
            sql = f"""select * from user where email = '{data["email"]}'"""
            cursor.execute(sql)
            mydata = cursor.fetchone()
            if mydata:
                connection.close()
                return False
            else:
                sql = "insert into user(name,email,password) values(%s,%s,%s)"
                val = (data["name"],data["email"],data["password"])
                cursor.execute(sql, val)
                connection.commit()
                connection.close()
                return True
        except Exception as e:
            connection.close()
            print(e)
            return
    def signin(data):
        try:
            connection = pool.get_connection()
            cursor = connection.cursor()
            sql = f"""select * from user where email='{data["email"]}' 
            and password='{data["password"]}'"""
            cursor.execute(sql)
            result = cursor.fetchone()
            connection.close()
            if result:
                return result
            else:
                return False
        except Exception as e:
            connection.close()
            print(e)
            return

#=======================================
#Order
class Order:
    def schedule(data):
        try:
            connection = pool.get_connection()
            cursor = connection.cursor()
            sql = f"""select orderId from orders where userId='{data["userId"]}'"""
            cursor.execute(sql)
            result = cursor.fetchone()
            if(result):
                sql = """update orders set attractionId=%s, date=%s 
                ,time=%s, price=%s where orderId=%s"""
                val = (data["attractionId"],data["date"],data["time"]
                ,data["price"],result[0])
                cursor.execute(sql,val)
                connection.commit()
                connection.close()
                return {"ok":True,"message":"update"}
            else:
                sql = """insert into orders(userId,attractionId,date,time
                ,price,status) values(%s,%s,%s,%s,%s,%s)"""
                val = (data["userId"],data["attractionId"],data["date"],
                data["time"],data["price"],"未付款")
                cursor.execute(sql,val)
                connection.commit()
                connection.close()
                return {"ok":True,"message":"insert"}
        except Exception as e:
            connection.close()
            print(e)
            return
    def cart(data):
        try:
            connection = pool.get_connection()
            cursor = connection.cursor()
            userId = data["id"]
            sql = f"""select a.id, a.name, a.address, a.images, b.date, 
            b.time, b.price from orders b join attractions a on 
            b.attractionId=a.id where userId='{userId}'"""
            cursor.execute(sql)
            result = cursor.fetchone()
            connection.close()
            if(result):
                return result
            else:
                return False
        except Exception as e:
            connection.close()
            print(e)
            return
    def cancle(id):
        try:
            connection = pool.get_connection()
            cursor = connection.cursor()
            sql = f"delete from orders where userId='{id}'"
            cursor.execute(sql)
            connection.commit()
            connection.close()
            return True
        except Exception as e:
            connection.close()
            print(e)
            return