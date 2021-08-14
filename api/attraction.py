from flask import request, jsonify, Blueprint
from module.database import Attraction
import json

attr = Blueprint("attr",__name__)
attrId = Blueprint("attrId",__name__)

@attr.route("/api/attractions")
def attractions():
	#抓取使用者輸入頁面及關鍵字
	page = request.args.get("page",1)
	keyword = request.args.get("keyword","")
	jsonData = {
		"nextpage":0,
		"data":[]
	}
	page = int(page)
	start = None
	if(page <= 1):
		start = 0
		jsonData["nextpage"] = 2
	else:
		start = (page-1)*12
		jsonData["nextpage"] = page+1
	#從module取得資料庫資料
	mydata = Attraction.attractions(keyword, start)
	if len(mydata) == 0:
		jsonData = {
			"error":True,
			"message":"empty"
		}
		return jsonData,500
	else:
		for dict in mydata:
			listData ={}
			#將資料庫資料使用迴圈一一放入data列表中的變數
			listData["id"] = dict[0]
			listData["name"] = dict[1]
			listData["category"] = dict[2]
			listData["description"] = dict[3]
			listData["address"] = dict[4]
			listData["transport"] = dict[5]
			listData["mrt"] = dict[6]
			listData["latitude"] = dict[7]
			listData["longitude"] = dict[8]
			listData["images"] = json.loads(dict[9])	#//將json轉回list
			#把這圈的資料apppend進jsonData之中
			jsonData["data"].append(listData)
		if(len(mydata) < 12):
			jsonData["nextpage"] = None
		
		return jsonData

@attrId.route("/api/attraction/<attractionId>")
def attractionId(attractionId):
    mydata = Attraction.attractionId(attractionId)
    if mydata:
        jsonData ={
            "id":mydata[0],
            "name":mydata[1],
            "category":mydata[2],
            "description":mydata[3],
            "address":mydata[4],
            "transport":mydata[5],
            "mrt":mydata[6],
            "latitude":mydata[7],
            "longitude":mydata[8],
            "images":json.loads(mydata[9])
        }
        return jsonify(jsonData)
    else:
        return jsonify({
            "error":True,
            "message":"伺服器錯誤"
        }),500