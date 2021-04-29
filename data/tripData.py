import json
from flask import request
import mysql.connector

mydb = mysql.connector.connect(
    host = "localhost",
    user = "root",
    password = "Gtio556$",
    database = "tripdata"
)
mycursor = mydb.cursor()



with open("taipei-attractions.json" , "r" , encoding="utf-8")as response:
    data = json.load(response)

clist = data["result"]["results"]

testImg = []
ans = []
for i in range(len(clist)):
    name = clist[i]["stitle"]
    category = clist[i]["CAT2"]
    description = clist[i]["xbody"]
    address = clist[i]["address"]
    transport = str(clist[i]["info"])
    mrt = str(clist[i]["MRT"])
    latitude = clist[i]["latitude"]
    longitude = clist[i]["longitude"]
    image = clist[i]["file"]
    splitHttp = image.split("http")

    # 移除img index[0]的空值
    splitHttp.remove(splitHttp[0])
    num = len(splitHttp)
    #移除資料中包含MP3及FLV的網址

    if "flv" in splitHttp[-1] :
        splitHttp.remove(splitHttp[-1])

    if "mp3" in splitHttp[-1] :
        splitHttp.remove(splitHttp[-1])             
        
    #將http一一加回網址中
    num = len(splitHttp)
    # print(num)
    for j in range(num):
        data = "http"+splitHttp[j]
        testImg.append(data)
    newImg = str(testImg)
    ans.append(newImg)
    testImg.clear()
    #處理完的IMG
    images = ans[i]
    # print(images)
    


將資料寫入資料庫
    sql = "insert into spot(name,category,description,address,transport,mrt,latitude,longitude,images)values(%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    val = (name,category,description,address,transport,mrt,latitude,longitude,images)
    mycursor.execute(sql,val)
    mydb.commit()
