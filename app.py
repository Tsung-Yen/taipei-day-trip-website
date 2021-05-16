from flask import *
#匯入Flask_Cors(在不同源的情況下瀏覽器會將以收到的request拒絕Javascript存取，須設定路由的response規則)
from flask_cors import CORS
import json
import hashlib
import mysql.connector

mydb = mysql.connector.connect(
	host="localhost",
	#此處為連接instance遠端mysql的帳號密碼
	user="root",
	password="Gtio556$",
	database="tripdata"
)
mycursor=mydb.cursor()

app=Flask(__name__)
#只要來自此路由底下的request都允許存取
cors = CORS(app,resources={r"/api/*":{"origins":"*"}})
app.config["JSON_AS_ASCII"]=False
app.config['JSON_SORT_KEYS'] = False
app.config["TEMPLATES_AUTO_RELOAD"]=True

#創造一個字典存放使用者名稱
currentUser={}
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
			sql = f"select * from spot where id > '{count1}' and id <= '{count2}'"
			mycursor.execute(sql)
			mydata = mycursor.fetchall()
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
			sql = f"select * from spot where id > '{count1}' and id <= '{count2}'"
			mycursor.execute(sql)
			mydata = mycursor.fetchall()
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
			sql = f"select * from spot where name like '%{keyword}%'"
			mycursor.execute(sql)
			mydata = mycursor.fetchall()
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
		#使用者輸入鍵字並不存在
		else:
			errorData = {
							"error":True,
							"message":"輸入頁面或關鍵字不存在"
			}
			return errorData
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
		sql = f"select * from spot where id = '{attractionId}' limit 1"
		mycursor.execute(sql)
		mydata = mycursor.fetchone()
		if mydata:
			#開一個dict字典放入資料庫資料
			dictData ={}
			#將資料庫資料使用迴圈一一放入data列表中的變數
			dictData["id"] = mydata[0]
			dictData["name"] = mydata[1]
			dictData["category"] = mydata[2]
			dictData["description"] = mydata[3]
			dictData["address"] = mydata[4]
			dictData["transport"] = mydata[5]
			dictData["mrt"] = mydata[6]
			dictData["latitude"] = mydata[7]
			dictData["longitude"] = mydata[8]
			dictData["images"] = mydata[9]
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
@app.route("/api/user/userstatus/",methods=["GET"])  #取得當前登入的使用者資訊
def status():
	userStatus= {}
	key = request.cookies.get("key")
	if key in currentUser:
		id = currentUser[key]["id"]
		name = currentUser[key]["name"]
		email = currentUser[key]["email"]
		print(id,name,email)
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
	#write user data in mysql
	sql = f"select * from user where email = '{email}' limit 1"
	mycursor.execute(sql)
	mydata = mycursor.fetchone()

	if mydata:
		userStatus["error"] = True
		userStatus["message"] = "信箱已被註冊，請重新輸入"
		return userStatus
	elif  not mydata:
		sql = "insert into user(name,email,password) values(%s,%s,%s)"
		val = (name , email , password)
		mycursor.execute(sql,val)
		mydb.commit()
		userStatus["ok"] = True
		return userStatus
	else:
		userStatus["error"] = True
		userStatus["message"] = "伺服器錯誤"
		return userStatus
		
	



@app.route("/api/user/signin/",methods=["PATCH"])
def signin():
	userStatus = {}
	#抓取使用者輸入帳號密碼
	data = request.get_json()
	email = data["email"]
	password = data["password"]
	#使用者輸入資料和db比對
	sql = f"select * from user where email = '{email}' and password = '{password}' limit 1"
	mycursor.execute(sql)
	mydata = mycursor.fetchone()

	if mydata:
		userStatus["ok"] = True
		response = make_response(userStatus)
		id = mydata[0]
		name = mydata[1]
		email = mydata[2]
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

@app.route("/api/user/signout/",methods=["DELETE"])
def signout():
	userStatus = {}
	userStatus["ok"] = True
	outResponse = make_response(userStatus)
	outResponse.set_cookie(key="key" , value="" , expires=0)
	return outResponse

if __name__=="__main__":
	app.run(host="0.0.0.0",port=3000,debug=True)