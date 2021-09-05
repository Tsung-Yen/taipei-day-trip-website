from flask import request, Blueprint, jsonify
from flask.helpers import make_response
from module.database import Menber
from module.verify import Verify

status = Blueprint("status",__name__)
signup = Blueprint("signup",__name__)
signin = Blueprint("signin",__name__)
signout = Blueprint("signout",__name__)

@status.route("/api/user/status/")
def userstatus():
    key = request.cookies.get("key")
    user = Verify.verifyuser(key)
    if(user != False):
        return jsonify({
            "ok":True,
            "data":{
                "id":user["id"],
                "name":user["name"],
                "email":user["email"]
            }
        })
    else: 
        return jsonify({"error":True,"message":"未登入"})

@signup.route("/api/user/signup/",methods=["POST"])
def usersignup():
    userInfo = request.get_json()
    if(userInfo["name"]=="" or userInfo["email"]=="" or userInfo["password"]==""):
        return jsonify({
            "error":True,
            "message":"未正確填寫資料"
        })
    data = {
        "name":userInfo["name"],
        "email":userInfo["email"],
        "password":userInfo["password"]
    }
    user = Menber.signup(data)
    if(user == True):
        return jsonify({
            "ok":True,
            "message":"註冊成功"
        })
    else:
        return jsonify({
            "error":True,
            "message":"帳號已存在"
        })

@signin.route("/api/user/signin/",methods=["PATCH"])
def usersignin():
    userInfo = request.get_json()
    if(userInfo["email"] == "" or userInfo["password"]==""):
        return jsonify({
            "error":True,
            "message":"未正確輸入"
        })
    result = Menber.signin(userInfo)
    if(result != False):
        key = Verify.encryption(result)
        response = jsonify({"ok":True})
        response.set_cookie(key="key",value=key)
        return response
    else:
        return jsonify({
            "error":True,
            "message":"帳號或密碼輸入錯誤"
        })

@signout.route("/api/user/signout/",methods=["DELETE"])
def usersignout():
    key = request.cookies.get("key")
    response = make_response(jsonify({"ok":True}))
    response.set_cookie(key="key",value="",expires=0)
    return response
    