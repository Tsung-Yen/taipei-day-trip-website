from mysql.connector import pooling
from dotenv import load_dotenv
import os
import json
import hashlib
import module.sendemail as send

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
            like %s limit %s,%s"""
            cursor.execute(sql, (('%'+name+'%'), startNum, 12))
            result = cursor.fetchall()
            connection.close()
            return result
        except Exception as e:
            connection.close()
            send.Email.developer("attraction_error")
            return 
    def attractionId(id):
        try:
            connection = pool.get_connection()
            cursor = connection.cursor()
            sql = f"""select * from attractions where 
            id = %s"""
            cursor.execute(sql, (id,))
            result = cursor.fetchone()
            connection.close()
            return result
        except Exception as e:
            connection.close()
            send.Email.developer("attraction_error")
            return

#==================================
#Menber System
class Menber:
    def status(email):
        try:
            connection = pool.get_connection()
            cursor = connection.cursor()
            sql = f"""select * from user where email
            = %s"""
            cursor.execute(sql, (email,))
            result = cursor.fetchone()
            connection.close()
            return True
        except Exception as e:
            connection.close()
            send.Email.developer("user_error")
            return
    def signup(data):
        try:
            connection = pool.get_connection()
            cursor = connection.cursor()
            sql = f"""select * from user where email = %s"""
            cursor.execute(sql,(data["email"],))
            mydata = cursor.fetchone()
            if mydata:
                connection.close()
                return False
            else:
                sql = "insert into user(name,email,password) values(%s,%s,%s)"
                val = (data["name"],data["email"],hashlib.sha256
                ((data["password"]+os.getenv("Salt")).encode('utf-8')).hexdigest())
                cursor.execute(sql, val)
                connection.commit()
                connection.close()
                return True
        except Exception as e:
            connection.close()
            send.Email.developer("user_error")
            return
    def signin(data):
        try:
            connection = pool.get_connection()
            cursor = connection.cursor()
            sql = f"""select * from user where email= %s 
            and password= %s"""
            cursor.execute(sql,(data["email"],hashlib.sha256
            ((data["password"]+os.getenv("Salt")).encode('utf-8')).hexdigest()))
            result = cursor.fetchone()
            connection.close()
            if result:
                return result
            else:
                return False
        except Exception as e:
            connection.close()
            send.Email.developer("user_error")
            return

#=======================================
#Booking
class Booking:
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
            send.Email.developer("booking_error")
            return
    def cart(data):
        try:
            connection = pool.get_connection()
            cursor = connection.cursor()
            userId = data["id"]
            sql = f"""select a.id, a.name, a.address, a.images, b.date, 
            b.time, b.price from orders b join attractions a on 
            b.attractionId=a.id where userId= %s"""
            cursor.execute(sql,(userId,))
            result = cursor.fetchone()
            connection.close()
            if(result):
                return result
            else:
                return False
        except Exception as e:
            connection.close()
            send.Email.developer("booking_error")
            return
    def cancle(id):
        try:
            connection = pool.get_connection()
            cursor = connection.cursor()
            sql = f"delete from orders where userId= %s"
            cursor.execute(sql,(id,))
            connection.commit()
            connection.close()
            return True
        except Exception as e:
            connection.close()
            send.Email.developer("booking_error")
            return

#=====================================================
#Order
class Order:
    def pay(userId, phone, number, mail):
        try:
            connection = pool.get_connection()
            cursor = connection.cursor()
            sql = """update orders set phone=%s,number=%s,mail=%s,status=%s 
            where userId=%s"""
            val = (phone, number, mail, "已付款", userId)
            cursor.execute(sql,val)
            connection.commit()
            connection.close()
            return True
        except Exception as e:
            connection.close()
            send.Email.developer("order_error")
            return
    def check(id):
        try:
            connection = pool.get_connection()
            cursor = connection.cursor()
            sql = f"""select number,status,mail from orders where userId= %s"""
            cursor.execute(sql,(id,))
            result = cursor.fetchone()
            connection.close()
            if result:
                return result
            else:
                return False
        except Exception as e:
            connection.close()
            send.Email.developer("order_error")
            return