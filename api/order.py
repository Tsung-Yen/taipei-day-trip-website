from flask import json, request, Blueprint, jsonify
from module.verify import Verify
from dotenv import load_dotenv
from module.database import Order
from datetime import datetime
import requests
import os

load_dotenv()
pay = Blueprint("pay",__name__)
check = Blueprint("check",__name__)

@pay.route("/api/orders",methods=["POST"])
def postOrder():
    try:
        key = request.cookies.get("key")
        user = Verify.verifyuser(key)
        if(user != False):
            userInfo = request.get_json()
            prime = userInfo["prime"]
            price = userInfo["order"]["price"]
            phone = userInfo["order"]["contact"]["phone"]
            name = userInfo["order"]["contact"]["name"].encode("utf8").decode("latin1")
            email = userInfo["order"]["contact"]["email"]
            if not prime and not phone and not name and not email:
                return jsonify({"error":True,"message":"未確實填寫資料"})
            tapPayData = json.dumps({
                "prime":prime,
                "partner_key":os.getenv("PartnerKey"),
                "merchant_id":"Yanyan_TAISHIN",
                "details":"Test Pay",
                "amount":price,
                "cardholder":{
                    "phone_number":phone,
                    "name":name,
                    "email":email
                },
                "remember":True
            })
            tapPayUrl = "https://sandbox.tappaysdk.com/tpc/payment/pay-by-prime"
            headers = {
                "Content-Type":"application/json",
                "x-api-key":os.getenv("PartnerKey")
            }
            res = requests.post(tapPayUrl,data=tapPayData,headers=headers)
            response = res.json()
            now = str(datetime.today().strftime('%Y%m%d%H%M'))
            number = now + str(user["id"])
            if response["status"] == 0:
                result = Order.pay(user["id"], phone, number)
                if result == True:
                    return jsonify({
                        "ok":True,
                        "data":{"number":number,"payment":{"status":0,"message":"付款成功"}}
                    })
                else:
                    return jsonify({"error":True,"number":number,"message":"付款失敗"}),500
            else:
                return jsonify({"error":True,"number":number,"message":"付款失敗"}),500
        else:
            return jsonify({"error":True,"message":"未登入"}),400
    except Exception as e:
        print(e)
        return jsonify({"error":True,"message":"伺服器內部錯誤"}),500

@check.route("/api/order/<orderNumber>")
def getOrder(orderNumber):
    key = request.cookies.get("key")
    user = Verify.verifyuser(key)
    if user != False:
        result = Order.check(user["id"])
        if result != False:
            return jsonify({"ok":True,"data":{"number":result[0],"status":result[1]}})
        else:
            return jsonify({"error":True,"message":"沒有付款紀錄"}),400
    else:
        return jsonify({"error":True,"message":"未登入"}),400