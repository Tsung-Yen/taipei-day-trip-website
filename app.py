from flask import *

app=Flask(__name__)
app.config["JSON_AS_ASCII"]=False
app.config['JSON_SORT_KEYS'] = False
app.config["TEMPLATES_AUTO_RELOAD"]=True

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

#Attractions API
from api.attraction import attr
from api.attraction import attrId
app.register_blueprint(attr)
app.register_blueprint(attrId)

#Menber System API
from api.menber import status
from api.menber import signup
from api.menber import signin
from api.menber import signout
app.register_blueprint(status)
app.register_blueprint(signup)
app.register_blueprint(signin)
app.register_blueprint(signout)

#Order
from api.order import schedule
from api.order import cart
from api.order import cancle
app.register_blueprint(schedule)
app.register_blueprint(cart)
app.register_blueprint(cancle)


# @app.route("/api/orders",methods=["POST"])
# def orders():
# 	if request.method == "POST":
# 		key = request.cookies.get("key")
# 		if key in currentUser:
# 			data = request.get_json()
# 			prime = data["prime"]
# 			contactname = data["order"]["contact"]["name"]
# 			contactemail = data["order"]["contact"]["email"]
# 			contactphone = data["order"]["contact"]["phone"]
# 			if prime and contactname and contactemail and contactphone:
# 				#步驟1:聯絡資料寫入字典
# 				postData = {
# 					"prime":prime,
# 					"partner_key":os.getenv("PartnerKey"),
# 					"merchant_id":"Yanyan_TAISHIN",
# 					"details":"Test TapPay",
# 					"amount":data["order"]["price"],
# 					"cardholder":{
# 						"phone_number":contactphone,
# 						"name":contactname,
# 						"email":contactemail
# 					},
# 					"remember":True
# 				}
# 				#步驟2:將資料按照TapPay規定格式用post方發送出，連上TapPay server(結束後TapPay會回傳response)
# 				postData = json.dumps(postData)
# 				tapPayUrl = "https://sandbox.tappaysdk.com/tpc/payment/pay-by-prime"
# 				import requests
# 				headers = {
# 					"Content-Type":"application/json",
# 					"x-api-key":os.getenv("PartnerKey")
# 				}
# 				r = requests.post(tapPayUrl,data=postData,headers=headers)
# 				response = r.json()
# 				#TapPAy api 回傳狀態等於0為成功
# 				username = currentUser[key]["name"]
# 				if response["status"] == 0:
# 					#先將使用者狀態更新為已付款
# 					pool = MySQLPool(**dbconfig)
# 					updatesql = f"""update bookingdataunpaid set contactname = '{data["order"]["contact"]["name"]}'
# 					,contactemail = '{data["order"]["contact"]["email"]}',contactphone = '{data["order"]["contact"]["phone"]}',paidstatus = '已付款' 
# 					where username = '{username}'""" 
# 					pool.execute(updatesql,commit=True)
# 					#再將訂單狀態從資料表取出
# 					sql = f"select number from bookingdataunpaid where username = '{username}' limit 1"
# 					mydata = pool.execute(sql)
# 					if mydata:
# 						number = mydata[0][0]
# 					result = {
# 						"data":{
# 							"number":number,
# 							"payment":{
# 								"status":0,
# 								"message":"付款成功"
# 							}
# 						}
# 					}
# 				else:
# 					pool = MySQLPool(**dbconfig)
# 					errorsql = f"select number from bookingdataunpaid where username = '{username}' limit 1"
# 					mydata = pool.execute(errorsql)
# 					if mydata:
# 						number = mydata[0][0]
# 					result = {
# 						"number":number,
# 						"error":True,
# 						"message":"付款失敗"
# 					}
# 				returndata = json.dumps(result)
# 				return returndata
# 			else:
# 				result = {
# 					"error":True,
# 					"message" : "未正確填寫資料"
# 				}
# 				result = json.dumps(result)
# 				return result
# 		else:
# 			signYetResult = {}
# 			signYetResult["error"] = True
# 			signYetResult["message"] = "尚未登入會員"
# 			return signYetResult
		
# 	else:
# 		serverResult = {}
# 		serverResult["error"] = True
# 		serverResult["message"] = "伺服器錯誤"
# 		return serverResult,400

# @app.route("/api/order/<orderNumber>")
# def orderResult(orderNumber):
	# assert orderNumber == request.view_args["orderNumber"]
	# key = request.cookies.get("key")
	# if orderNumber != None:
	# 	if key in currentUser:
	# 		pool = MySQLPool(**dbconfig)
	# 		sql = f"""select price,attractionid,date,booktime,contactname,contactemail,
	# 		contactphone,paidstatus from bookingdataunpaid where number = 
	# 		'{orderNumber}' limit 1"""
	# 		paidstatus = pool.execute(sql)
	# 		if paidstatus:
	# 			attractionId = paidstatus[0][1]
	# 			tripsql = f"select name,address,images from spot where id = '{attractionId}' limit 1"
	# 			mydata = pool.execute(tripsql)
	# 			if mydata:
	# 				images = mydata[0][2].split(",")
	# 				image = images[0]
	# 				if paidstatus[0][7] == "已付款":
	# 					status = 1
	# 				else:
	# 					status = 0
	# 				result = {
	# 					"data":{
	# 						"number":orderNumber,
	# 						"price":paidstatus[0][0],
	# 						"trip":{
	# 							"attraction":{
	# 								"id":attractionId,
	# 								"name":mydata[0][0],
	# 								"address":mydata[0][1],
	# 								"image":image
	# 							},
	# 							"date":paidstatus[0][2],
	# 							"time":paidstatus[0][3]
	# 						},
	# 						"contact":{
	# 							"name":paidstatus[0][4],
	# 							"email":paidstatus[0][5],
	# 							"phone":paidstatus[0][6]
	# 						},
	# 						"status":status
	# 					}
	# 				}
	# 				returnData = json.dumps(result)
	# 				return returnData	 
	# 	else:
	# 		result = {}
	# 		result["error"] = True
	# 		result["message"] = "尚未登入會員"
	# 		return result
	
if __name__=="__main__":
	app.run(host="0.0.0.0",port=3000,debug=True)