from flask import *
import json
import mysql.connector
mydb = mysql.connector.connect(
	host="localhost",
	user="root",
	password="root",
	database="tripdata"
)
mycursor=mydb.cursor()

app=Flask(__name__)
app.config["JSON_AS_ASCII"]=False
app.config['JSON_SORT_KEYS'] = False
app.config["TEMPLATES_AUTO_RELOAD"]=True

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
			if mydata:
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
		elif count == 0 and keyword != None:
			#先把json字典中的列表清空
			jsonData["data"].clear()
			#將使用者輸入的關鍵字放入資料庫做篩選
			sql = f"select * from spot where name like '%{keyword}%' limit 12"
			mycursor.execute(sql)
			mydata = mycursor.fetchall()
			if mydata:
				#判斷資料數量來分類頁數
				if len(mydata) < 12:
					jsonData["nextPage"] = "null"
				elif len(mydata) > 12 and len(mydata) <= 24:
					jsonData["nextPage"] = 1
				elif len(mydata) > 24 and len(mydata) <= 36:
					jsonData["nextPage"] = 2
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
		else:
			#開一個存放錯誤訊息的字典，為
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
@app.route("/api/attraction/")
def attractionId():
	attractionId = request.args.get("attractionId")
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
app.run(port=3000)