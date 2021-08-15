from flask import request, Blueprint, jsonify
from flask.json import loads
from module.verify import Verify
from module.database import Order
import json

schedule = Blueprint("schedule",__name__)
cart = Blueprint("cart",__name__)
cancle = Blueprint("cancle",__name__)

@schedule.route("/api/booking/schedule",methods=["POST"])
def orderschedule():
    key = request.cookies.get("key")
    user = Verify.verifyuser(key)
    if(user != False):
        data = request.get_json()
        data["userId"] = user["id"]
        result = Order.schedule(data)
        return jsonify({"ok":True,"message":result["message"]})
    else:
        return jsonify({"error":True,"message":"未登入"}),403
    

@cart.route("/api/booking/cart")
def ordercart():
    key = request.cookies.get("key")
    user = Verify.verifyuser(key)
    if(user != False):
        result = Order.cart(user)
        if(result != False):
            return jsonify({
                "ok":True,
                "message":"not empty",
                "attraction":{
                    "id":result[0],
                    "name":result[1],
                    "address":result[2],
                    "image":json.loads(result[3])[0]
                },
                "date":result[4],
                "time":result[5],
                "price":result[6],
                "username":user["name"]
            })
        else:
            return jsonify({"ok":True,"username":user["name"],"message":"empty"})
    else:
        return jsonify({"error":True,"message":"未登入"}),403

@cancle.route("/api/booking/cancle",methods=["DELETE"])
def ordercancle():
    key = request.cookies.get("key")
    user = Verify.verifyuser(key)
    if(user != False):
        result = Order.cancle(user["id"])
        if(result == True):
            return jsonify({"ok":True,"message":"刪除成功"})          
        else:
            return
    else:
        return jsonify({"error":True,"message":"未登入"}),403