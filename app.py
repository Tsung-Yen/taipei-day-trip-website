from flask import *
#匯入Flask_Cors(在不同源的情況下瀏覽器會將以收到的request拒絕Javascript存取，須設定路由的response規則)
from flask_cors import CORS
import hashlib
from module.database import Attraction


app=Flask(__name__)

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

#Attraction API
from api.attraction import attr
app.register_blueprint(attr)

from api.attraction import attrId
app.register_blueprint(attrId)





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
						"phone_number":contactphone,
						"name":contactname,
						"email":contactemail
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