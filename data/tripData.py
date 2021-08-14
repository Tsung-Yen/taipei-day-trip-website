import json
from flask import request
import mysql.connector
import os
from dotenv import load_dotenv
load_dotenv()

mydb = mysql.connector.connect(
    host = "localhost",
    user = os.getenv("DBUSER"),
    password = os.getenv("DBPASSWORD"),
    database = os.getenv("DBNAME")
)
mycursor = mydb.cursor()



with open("taipei-attractions.json" , "r" , encoding="utf-8")as response:
    data = json.load(response)

for dict in data["result"]["results"]:
    name = dict["stitle"]
    category = dict["CAT2"]
    description = dict["xbody"]
    address = dict["address"]
    transport = dict["info"]
    mrt = dict["MRT"]
    latitude = dict["latitude"]
    longitude = dict["longitude"]
    images = dict["file"]
    imageList = images.split("http://")
    filtImage = ["http://"+image for image in imageList if image!= ""]
    filtImage = [file for file in filtImage if "flv" not in file]
    filtImage = [file for file in filtImage if "mp3" not in file]
    filtImage = [file for file in filtImage if "gif" not in file]
#將資料寫入資料庫
    sql = "insert into attractions(name,category,description,address,transport,mrt,latitude,longitude,images)values(%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    val = (name,category,description,address,transport,mrt,latitude,longitude,json.dumps(filtImage))
    mycursor.execute(sql,val)
    mydb.commit()
