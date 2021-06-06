from typing import Type
from flask import *
#匯入Flask_Cors(在不同源的情況下瀏覽器會將以收到的request拒絕Javascript存取，須設定路由的response規則)
from flask_cors import CORS
import json
import hashlib
import mysql.connector
from mysql.connector import errors
from werkzeug.datastructures import Headers
import os
from dotenv import load_dotenv
load_dotenv()

#test
dbhost = os.getenv("DBHOST")
dbport = os.getenv("DBPORT")
dbuser = os.getenv("DBUSER")
dbpw = os.getenv("DBPASSWORD")
dbname = os.getenv("DBNAME")
import mysql.connector.pooling
dbconfig = {
	"host":dbhost,
	"port":dbport,
	"user":dbuser,
	"password":dbpw,
	"database":dbname
}
class MySQLPool(object):
    """
    create a pool when connect mysql, which will decrease the time spent in 
    request connection, create connection and close connection.
    """
    def __init__(self, host="localhost", port="3306", user="root",
				password="root", database="tripdata", pool_name="mypool",
				pool_size=3):
        res = {}
        self._host = host
        self._port = port
        self._user = user
        self._password = password
        self._database = database

        res["host"] = self._host
        res["port"] = self._port
        res["user"] = self._user
        res["password"] = self._password
        res["database"] = self._database
        self.dbconfig = res
        self.pool = self.create_pool(pool_name=pool_name, pool_size=pool_size)

    def create_pool(self, pool_name="mypool", pool_size=3):
        """
        Create a connection pool, after created, the request of connecting 
        MySQL could get a connection from this pool instead of request to 
        create a connection.
        :param pool_name: the name of pool, default is "mypool"
        :param pool_size: the size of pool, default is 3
        :return: connection pool
        """
        pool = mysql.connector.pooling.MySQLConnectionPool(
            pool_name=pool_name,
            pool_size=pool_size,
            pool_reset_session=True,
            **self.dbconfig)
        return pool

    def close(self, conn, cursor):
        """
        A method used to close connection of mysql.
        :param conn: 
        :param cursor: 
        :return: 
        """
        cursor.close()
        conn.close()

    def execute(self, sql, args=None, commit=False):
        """
        Execute a sql, it could be with args and with out args. The usage is 
        similar with execute() function in module pymysql.
        :param sql: sql clause
        :param args: args need by sql clause
        :param commit: whether to commit
        :return: if commit, return None, else, return result
        """
        # get connection form connection pool instead of create one.
        conn = self.pool.get_connection()
        cursor = conn.cursor()
        if args:
            cursor.execute(sql, args)
        else:
            cursor.execute(sql)
        if commit is True:
            conn.commit()
            self.close(conn, cursor)
            return None
        else:
            res = cursor.fetchall()
            self.close(conn, cursor)
            return res

    def executemany(self, sql, args, commit=False):
        """
        Execute with many args. Similar with executemany() function in pymysql.
        args should be a sequence.
        :param sql: sql clause
        :param args: args
        :param commit: commit or not.
        :return: if commit, return None, else, return result
        """
        # get connection form connection pool instead of create one.
        conn = self.pool.get_connection()
        cursor = conn.cursor()
        cursor.executemany(sql, args)
        if commit is True:
            conn.commit()
            self.close(conn, cursor)
            return None
        else:
            res = cursor.fetchall()
            self.close(conn, cursor)
            return res


app=Flask(__name__)
#只要來自此路由底下的request都允許存取
cors = CORS(app,resources={r"/api/*":{"origins":"*"}})
app.config["JSON_AS_ASCII"]=False
app.config['JSON_SORT_KEYS'] = False
app.config["TEMPLATES_AUTO_RELOAD"]=True

#創造一個字典存放使用者名稱key
currentUser={}

#訂單編號為當前日期及時間，放入response當中
from datetime import datetime
now = datetime.today().strftime('%Y-%m-%d %H:%M')
now = str(now)
now = now.replace("-","").replace(" ","").replace(":","")
now = int(now+"00")
num = 1
currentNumber = []
lastNumList = []
lastNumList.append(0)
# Pages
@app.route("/")
def index():
	return render_template("index.html")
@app.route("/attraction/<id>")
def attraction(id):
	return render_template("attraction.html")
@app.route("/booking")
def booking():
	return render_template("booking.html")
@app.route("/thankyou")
def thankyou():
	return render_template("thankyou.html")

@app.route("/api/attractions")
def attractions():
	#抓取使用者輸入頁面及關鍵字
	page = request.args.get("page")
	keyword = request.args.get("keyword")
	#先判斷使用者輸入是否符合api格式:
	if page != None:
		#使用者輸入參數為NoneType，需做轉型
		page = str(page)
		count = int(page)
		#寫一個json字典當作一頁，供每筆資料存放
		jsonData = {"nextPage":0 ,"data":[]}
		#如果使用者輸入頁數為0
		if count == 0 and keyword == None:
			#先將字典中的data列表清空
			jsonData["data"].clear()
			#判斷使用者輸入的直並做處理(需要兩筆資料來對資料庫做篩選)
			count1 = count+0
			count2 = count+12
			#抓取資料庫檔案
			pool = MySQLPool(**dbconfig)
			sql = f"select * from spot where id > '{count1}' and id <= '{count2}'"
			mydata = pool.execute(sql)
			if  mydata:
				#將下一頁資料放入字典nextPage
				jsonData["nextPage"] = count+1
				for i in range(len(mydata)):
					#開一個字典提供給資料庫資料
					listData ={}
					#將資料庫資料使用迴圈一一放入data列表中的變數
					listData["id"] = mydata[i][0]
					listData["name"] = mydata[i][1]
					listData["category"] = mydata[i][2]
					listData["description"] = mydata[i][3]
					listData["address"] = mydata[i][4]
					listData["transport"] = mydata[i][5]
					listData["mrt"] = mydata[i][6]
					listData["latitude"] = mydata[i][7]
					listData["longitude"] = mydata[i][8]
					listData["images"] = mydata[i][9]
					#把這圈的資料apppend進jsonData之中
					jsonData["data"].append(listData)
				return jsonData	
		elif count > 0 and count <=26 and keyword == None:
			#先把json字典中的列表清空
			jsonData["data"].clear()
			count1 = count*12
			count2 = count1+12
			pool = MySQLPool(**dbconfig)
			sql = f"select * from spot where id > '{count1}' and id <= '{count2}'"
			mydata = pool.execute(sql)
			if count < 26:
				jsonData["nextPage"] = count+1
			else:
				jsonData["nextPage"] = "null"
			for i in range(len(mydata)):
				#開一個字典提供給資料庫資料
				listData ={}
				#將資料庫資料使用迴圈一一放入data列表中的變數
				listData["id"] = mydata[i][0]
				listData["name"] = mydata[i][1]
				listData["category"] = mydata[i][2]
				listData["description"] = mydata[i][3]
				listData["address"] = mydata[i][4]
				listData["transport"] = mydata[i][5]
				listData["mrt"] = mydata[i][6]
				listData["latitude"] = mydata[i][7]
				listData["longitude"] = mydata[i][8]
				listData["images"] = mydata[i][9]
				#把這圈的資料apppend進jsonData之中
				jsonData["data"].append(listData)
			return jsonData
		elif keyword != None:
			#先把json字典中的列表清空
			jsonData["data"].clear()
			#將使用者輸入page轉成整數
			page = str(page)
			count = int(page)
			#將使用者輸入的關鍵字放入資料庫做篩選
			pool = MySQLPool(**dbconfig)
			sql = f"select * from spot where name like '%{keyword}%'"
			mydata = pool.execute(sql)
			if mydata:
			#判斷資料數量來分類頁數
				#處理小於12筆的資料
				if len(mydata)/12 <= 1 and count == 0:
					jsonData["nextPage"] = "null"
					for i in range(len(mydata)):
						#開一個字典提供給資料庫資料
						listData ={}
						#將資料庫資料使用迴圈一一放入data列表中的變數
						listData["id"] = mydata[i][0]
						listData["name"] = mydata[i][1]
						listData["category"] = mydata[i][2]
						listData["description"] = mydata[i][3]
						listData["address"] = mydata[i][4]
						listData["transport"] = mydata[i][5]
						listData["mrt"] = mydata[i][6]
						listData["latitude"] = mydata[i][7]
						listData["longitude"] = mydata[i][8]
						listData["images"] = mydata[i][9]
						#把這圈的資料apppend進jsonData之中
						jsonData["data"].append(listData)
					return jsonData

				#關鍵字搜尋結果超過12筆資料(0,1,2,3...頁的處理)
				elif len(mydata)/12 > 1:
					#將第一輪剩下數字存起來供第二輪迴圈做篩選
					leftData = len(mydata)
					#關鍵字搜尋展示第一輪資料共12筆
					if count == 0:
						jsonData["nextPage"] = 1
						for i in range(12):
							listData = {}
							listData["id"] = mydata[i][0]
							listData["name"] = mydata[i][1]
							listData["category"] = mydata[i][2]
							listData["description"] = mydata[i][3]
							listData["address"] = mydata[i][4]
							listData["transport"] = mydata[i][5]
							listData["mrt"] = mydata[i][6]
							listData["latitude"] = mydata[i][7]
							listData["longitude"] = mydata[i][8]
							listData["images"] = mydata[i][9]
							jsonData["data"].append(listData)
						return jsonData
					elif count == 1:
						#判斷還剩幾筆資料如果超過放到下一頁
						if leftData <= 23:
							num = leftData
							jsonData["nextPage"] = "null"
						else:
							num = 24
							jsonData["nextPage"] = count+1
						for i in range(12,num):
							listData = {}
							listData["id"] = mydata[i][0]
							listData["name"] = mydata[i][1]
							listData["category"] = mydata[i][2]
							listData["description"] = mydata[i][3]
							listData["address"] = mydata[i][4]
							listData["transport"] = mydata[i][5]
							listData["mrt"] = mydata[i][6]
							listData["latitude"] = mydata[i][7]
							listData["longitude"] = mydata[i][8]
							listData["images"] = mydata[i][9]
							jsonData["data"].append(listData)
						return jsonData
					elif count == 2:
						if leftData <= 35:
							num = leftData
							jsonData["nextPage"] = "null"
						else:
							num = 36
							jsonData["nextPage"] = 3
						for i in range(24,num):
							listData = {}
							listData["id"] = mydata[i][0]
							listData["name"] = mydata[i][1]
							listData["category"] = mydata[i][2]
							listData["description"] = mydata[i][3]
							listData["address"] = mydata[i][4]
							listData["transport"] = mydata[i][5]
							listData["mrt"] = mydata[i][6]
							listData["latitude"] = mydata[i][7]
							listData["longitude"] = mydata[i][8]
							listData["images"] = mydata[i][9]
							jsonData["data"].append(listData)
						return jsonData
					elif count == 3:
						if leftData <= 47:
							num = leftData
							jsonData["nextPage"] = "null"
						else:
							num = 48
							jsonData["nextPage"] = 4
						for i in range(36,num):
							listData = {}
							listData["id"] = mydata[i][0]
							listData["name"] = mydata[i][1]
							listData["category"] = mydata[i][2]
							listData["description"] = mydata[i][3]
							listData["address"] = mydata[i][4]
							listData["transport"] = mydata[i][5]
							listData["mrt"] = mydata[i][6]
							listData["latitude"] = mydata[i][7]
							listData["longitude"] = mydata[i][8]
							listData["images"] = mydata[i][9]
							jsonData["data"].append(listData)
						return jsonData
					elif count == 4:
						if leftData <= 59:
							num = leftData
							jsonData["nextPage"] = "null"
						else:
							num = 60
							jsonData["nextPage"] = 5
						for i in range(48,num):
							listData = {}
							listData["id"] = mydata[i][0]
							listData["name"] = mydata[i][1]
							listData["category"] = mydata[i][2]
							listData["description"] = mydata[i][3]
							listData["address"] = mydata[i][4]
							listData["transport"] = mydata[i][5]
							listData["mrt"] = mydata[i][6]
							listData["latitude"] = mydata[i][7]
							listData["longitude"] = mydata[i][8]
							listData["images"] = mydata[i][9]
							jsonData["data"].append(listData)
						return jsonData
					#使用者將關鍵字所有頁面看完，並且超過了頁數
					else:
						errorData = {
								"error":True,
								"message":"已顯示完所有資料"
						}
						return errorData
				#使用者搜尋頁數超過
				else:
					errorData = {
								"error":True,
								"message":"已超出頁數"
						}
					return errorData
			else:
				#使用者輸入鍵字並不存在
				result = {
					"error":True,
					"message":"很抱歉，您輸入的關鍵字不存在"
				}
				result = json.dumps(result)
				return result
	#伺服器壞掉回傳錯誤訊息(輸入格式錯誤)
	else:
		errorData = {
				"error":"true",
				"message":"輸入格式錯誤"
			}
		response = make_response(errorData,500)
		return 	response
@app.route("/api/attraction/<attractionId>")
def attractionId(attractionId):
	#可抓取使用者在路由上輸入的值
	assert attractionId == request.view_args["attractionId"]
	attractionId = int(attractionId)
	#判斷是否為使用者輸入造成伺服器壞掉
	if attractionId != None:
		#開一個字典當作頁面，供資料庫資料存放
		jsonData = {}
		jsonData.clear()
		#根據資料庫id篩選資料
		pool = MySQLPool(**dbconfig)
		sql = f"select * from spot where id = '{attractionId}' limit 1"
		mydata = pool.execute(sql)
		if mydata:
			#開一個dict字典放入資料庫資料
			dictData ={}
			#將資料庫資料使用迴圈一一放入data列表中的變數
			dictData["id"] = mydata[0][0]
			dictData["name"] = mydata[0][1]
			dictData["category"] = mydata[0][2]
			dictData["description"] = mydata[0][3]
			dictData["address"] = mydata[0][4]
			dictData["transport"] = mydata[0][5]
			dictData["mrt"] = mydata[0][6]
			dictData["latitude"] = mydata[0][7]
			dictData["longitude"] = mydata[0][8]
			dictData["images"] = mydata[0][9]
			#將dictData dict 放入 jsonData中
			jsonData.update(dictData)
			return jsonData
		else:
			errorData = {
				"error":"true",
				"message":"輸入Id不存在"
			}
			response = make_response(errorData,400)
			return response
	#伺服器壞掉回傳錯誤訊息(輸入格式錯誤)
	else:
		errorData = {
				"error":"true",
				"message":"輸入格式錯誤"
			}
		response = make_response(errorData,500)
		return response
#以下4個路由為(1.使用者狀態，2.註冊，3.登入，4.登出)
@app.route("/api/user/userstatus/",methods=["GET"])  #取得當前登入的使用者資訊
def status():
	userStatus= {}
	key = request.cookies.get("key")
	if key in currentUser:
		id = currentUser[key]["id"]
		name = currentUser[key]["name"]
		email = currentUser[key]["email"]
		data = {}
		data["id"] = id
		data["name"] = name
		data["email"] = email
		userStatus["data"] = data
		return userStatus
	else:
		return "null"
	
@app.route("/api/user/signup/",methods=["POST"])
def signup():
	if request.method == "POST":
		data = request.get_json()
		name = data["name"]
		email = data["email"]
		password = data["password"]
		userStatus = {}
		if name and email and password:
			print(name,email,password)
			#check user data in mysql
			pool = MySQLPool(**dbconfig)
			sql = f"select * from user where email = '{email}' limit 1"
			mydata = pool.execute(sql)

			if mydata:
				userStatus["error"] = True
				userStatus["message"] = "信箱已被註冊，請重新輸入"
				return userStatus
			elif not mydata:
				pool = MySQLPool(**dbconfig)
				sql = "insert into user(name,email,password) values(%s,%s,%s)"
				val = (name , email , password)
				mydata = pool.execute(sql,val,commit=True)
				userStatus["ok"] = True
				return userStatus
		else:
			result = {}
			result["error"] = True
			result["message"] = "未正確輸入資料"
			return result
	else:
		result = {}
		result["error"] = True
		result["message"] = "伺服器錯誤"
		return result
	

@app.route("/api/user/signin/",methods=["PATCH"])
def signin():
	userStatus = {}
	#抓取使用者輸入帳號密碼
	data = request.get_json()
	email = data["email"]
	password = data["password"]
	if email and password:
		#使用者輸入資料和db比對
		pool = MySQLPool(**dbconfig)
		sql = f"select * from user where email = '{email}' and password = '{password}' limit 1"
		mydata = pool.execute(sql)
		if mydata:
			#當前api
			userStatus["ok"] = True
			response = make_response(userStatus)
			id = mydata[0][0]
			name = mydata[0][1]
			email = mydata[0][2]
			key = hashlib.sha256((name+"afdaadasdda").encode("utf-8")).hexdigest()
			currentUser[key]={
				"id":id,
				"name":name,
				"email":email
			}
			response.set_cookie(key="key" , value=key)
			return response
		else:
			userStatus["error"] = True
			userStatus["message"] = "輸入信箱或密碼錯誤"
			return userStatus
	else:
		result = {}
		result["error"] = True
		result["message"] = "未正確輸入資料"
		return result

@app.route("/api/user/signout/",methods=["DELETE"])
def signout():
	userStatus = {}
	userStatus["ok"] = True
	outResponse = make_response(userStatus)
	outResponse.set_cookie(key="key" , value="" , expires=0)
	return outResponse

#以下三個路由為(1.使用者取得未確認下單的行程，2.建立新的預定行程，3.刪除預定行程)
@app.route("/api/booking/bookingcart/" , methods=["GET"])
def bookingCart():
	result = {}
	if request.method == "GET":
		key = request.cookies.get("key")
		if key in currentUser:
			#將當前使用者預定資料從資料庫拿出
			username = currentUser[key]["name"]
			pool = MySQLPool(**dbconfig)
			sql = f"select attractionid,date,booktime,price from bookingdataunpaid where username = '{username}' limit 1"
			mydata = pool.execute(sql)
			if mydata:
				attractionId = mydata[0][0]
				date = mydata[0][1]
				time = mydata[0][2]
				price = mydata[0][3]
				#透過id將預訂景點資訊從資料庫拿出
				tripsql = f"select name,address,images from spot where id = '{attractionId}' limit 1"
				tripdata = pool.execute(tripsql)
				if tripdata:
					image = tripdata[0][2].split(",")
					image = image[0]
					returndata= {
						"data":{
							"attraction":{
								"id":attractionId,
								"name":tripdata[0][0],
								"address":tripdata[0][1],
								"image":image
							},
							"date":date,
							"time":time,
							"price":price,
							"username":username
						}
					}
					returndata = json.dumps(returndata)
					return returndata
			#沒有預定任何資料
			else:
				result["message"] = "null"
				result["username"] = username	
				return result
		else:
			result["error"] = True
			result["message"] = "尚未登入會員"
			return result
	else:
		result["error"] = True
		result["message"] = "伺服器錯誤"
		return result,400

@app.route("/api/booking/bookingschedule/",methods=["POST"])
#此路由使用者預定行程，將已預訂未付款的所有使用者資訊寫入資料庫
def bookingSchedule():
	result = {}
	if request.method == "POST":
		key = request.cookies.get("key") 
		if key in currentUser:
			username = currentUser[key]["name"]
			data = request.get_json()
			attractionId = data["attractionId"]
			date = data["date"]
			time = data["time"]
			price = data["price"]
			if date and time and price:
				dateInt = date.replace("-","").replace(" ","")
				if time == "morning":
					timedata = "140000"
					dateInt = int(dateInt+timedata)
				else:
					timedata = "210000"
					dateInt = int(dateInt+timedata)
				if  dateInt > now:
					#先檢查使用者是否已預訂過行程，如果有直接更新資料
					pool = MySQLPool(**dbconfig)
					sql = f"select attractionid,date,booktime,price,number from bookingdataunpaid where username = '{username}' limit 1"
					mydata = pool.execute(sql)
					if mydata:
						lastNum = int(mydata[0][4])
						x = lastNum// 10**0 % 10
						y = lastNum// 10**1 % 10
						last = int(str(x)+str(y))
						if lastNumList[0] <= last:
							lastNumList[0] = last

						updatesql = f"update bookingdataunpaid set attractionid = '{attractionId}',date = '{date}', booktime = '{time}', price = '{price}' where username = '{username}'"
						pool.execute(updatesql,commit=True)
						result["status"] = "update booking"
					else:
					#新的訂單	
						#處理訂單編號
						if not lastNumList:
							number = now+1
						else:
							# n1 = currentNumber[-1]// 10**0 % 10
							# strn1 = str(n1)
							# n2 = currentNumber[-1]// 10**1 % 10
							# strn2 = str(n2)
							num = lastNumList[0]+1
							lastNumList[0] = num
							number = now+num
							
						#第一次預定資料，將使用者預定資料(未付款資料)寫入資料庫
						pool = MySQLPool(**dbconfig)
						newsql = """insert into bookingdataunpaid(username,attractionid,date,booktime,price,contactname,contactemail,
						contactphone,paidstatus,number) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
						newvalues = (username,attractionId,date,time,price," "," "," ","未付款",number) 
						pool.execute(newsql,newvalues,commit=True)
						result["status"] = "first booking"
					#預定行程建立成功，回傳成功訊息
					result["ok"] = True
					return result
				else:
					result = {}
					result["error"] = True
					result["message"] = "選定時間已過期"
					return result
			else:
				result["error"] = True
				result["message"] = "未正確輸入預定訊息"
				return result
		else:
			result["error"] = True
			result["message"] = "尚未登入會員"
			return result
	else:
		result["error"]	= True
		result["message"] = "伺服器錯誤"
		return result , 400


@app.route("/api/booking/deleteschedule/",methods=["DELETE"])
def deleteSchedule():
	result = {}
	if request.method == "DELETE":
		key = request.cookies.get("key")
		if key in currentUser:
			username = currentUser[key]["name"]
			pool = MySQLPool(**dbconfig)
			sql = f"delete from bookingdataunpaid where username ='{username}'"
			pool.execute(sql,commit=True)
			result["ok"] = True
		else:
			result["error"] = True
			result["message"] = "尚未登入會員"
		return result
	else:
		result["error"] = True
		result["message"] = "伺服器錯誤"
		return result,400

@app.route("/api/orders",methods=["POST"])
def orders():
	if request.method == "POST":
		key = request.cookies.get("key")
		if key in currentUser:
			data = request.get_json()
			prime = data["prime"]
			contactname = data["order"]["contact"]["name"]
			contactemail = data["order"]["contact"]["email"]
			contactphone = data["order"]["contact"]["phone"]
			if prime and contactname and contactemail and contactphone:
				#步驟1:聯絡資料寫入字典
				postData = {
					"prime":prime,
					"partner_key":os.getenv("PartnerKey"),
					"merchant_id":"Yanyan_TAISHIN",
					"details":"Test TapPay",
					"amount":data["order"]["price"],
					"cardholder":{
						"phone_number":contactname,
						"name":contactemail,
						"email":contactphone
					},
					"remember":True
				}
				#步驟2:將資料按照TapPay規定格式用post方發送出，連上TapPay server(結束後TapPay會回傳response)
				postData = json.dumps(postData)
				tapPayUrl = "https://sandbox.tappaysdk.com/tpc/payment/pay-by-prime"
				import requests
				headers = {
					"Content-Type":"application/json",
					"x-api-key":os.getenv("PartnerKey")
				}
				r = requests.post(tapPayUrl,data=postData,headers=headers)
				response = r.json()
				#TapPAy api 回傳狀態等於0為成功
				username = currentUser[key]["name"]
				if response["status"] == 0:
					#先將使用者狀態更新為已付款
					pool = MySQLPool(**dbconfig)
					updatesql = f"""update bookingdataunpaid set contactname = '{data["order"]["contact"]["name"]}'
					,contactemail = '{data["order"]["contact"]["email"]}',contactphone = '{data["order"]["contact"]["phone"]}',paidstatus = '已付款' 
					where username = '{username}'""" 
					pool.execute(updatesql,commit=True)
					#再將訂單狀態從資料表取出
					sql = f"select number from bookingdataunpaid where username = '{username}' limit 1"
					mydata = pool.execute(sql)
					if mydata:
						number = mydata[0][0]
					result = {
						"data":{
							"number":number,
							"payment":{
								"status":0,
								"message":"付款成功"
							}
						}
					}
				else:
					pool = MySQLPool(**dbconfig)
					errorsql = f"select number from bookingdataunpaid where username = '{username}' limit 1"
					mydata = pool.execute(errorsql)
					if mydata:
						number = mydata[0][0]
					result = {
						"number":number,
						"error":True,
						"message":"付款失敗"
					}
				returndata = json.dumps(result)
				return returndata
			else:
				result = {
					"error":True,
					"message" : "未正確填寫資料"
				}
				result = json.dumps(result)
				return result
		else:
			signYetResult = {}
			signYetResult["error"] = True
			signYetResult["message"] = "尚未登入會員"
			return signYetResult
		
	else:
		serverResult = {}
		serverResult["error"] = True
		serverResult["message"] = "伺服器錯誤"
		return serverResult,400

@app.route("/api/order/<orderNumber>")
def orderResult(orderNumber):
	assert orderNumber == request.view_args["orderNumber"]
	key = request.cookies.get("key")
	if orderNumber != None:
		if key in currentUser:
			pool = MySQLPool(**dbconfig)
			sql = f"""select price,attractionid,date,booktime,contactname,contactemail,
			contactphone,paidstatus from bookingdataunpaid where number = 
			'{orderNumber}' limit 1"""
			paidstatus = pool.execute(sql)
			if paidstatus:
				attractionId = paidstatus[0][1]
				tripsql = f"select name,address,images from spot where id = '{attractionId}' limit 1"
				mydata = pool.execute(tripsql)
				if mydata:
					images = mydata[0][2].split(",")
					image = images[0]
					if paidstatus[0][7] == "已付款":
						status = 1
					else:
						status = 0
					result = {
						"data":{
							"number":orderNumber,
							"price":paidstatus[0][0],
							"trip":{
								"attraction":{
									"id":attractionId,
									"name":mydata[0][0],
									"address":mydata[0][1],
									"image":image
								},
								"date":paidstatus[0][2],
								"time":paidstatus[0][3]
							},
							"contact":{
								"name":paidstatus[0][4],
								"email":paidstatus[0][5],
								"phone":paidstatus[0][6]
							},
							"status":status
						}
					}
					returnData = json.dumps(result)
					return returnData	 
		else:
			result = {}
			result["error"] = True
			result["message"] = "尚未登入會員"
			return result
	
if __name__=="__main__":
	app.run(host="0.0.0.0",port=3000,debug=True)