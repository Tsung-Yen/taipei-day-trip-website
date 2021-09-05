from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from dotenv import load_dotenv
import os
load_dotenv()

class Email:
    def client(email):
        content = MIMEMultipart()   #建立 MIMEMultipart 物件
        content["subject"] = "台北一日遊付款資訊"   #郵件標題
        content["from"] = os.getenv("OfficialEmail")    #寄件人      
        content["to"] = email      #收件人
        content.attach(MIMEText("付款成功!! 請於您預定的行程準時參加，謝謝您"))   #郵件內容
        try:
            with smtplib.SMTP(host="smtp.gmail.com", port="587") as smtp:
                smtp.ehlo()         #驗證伺服器
                smtp.starttls()     #建立加密傳輸
                smtp.login(os.getenv("OfficialEmail"), os.getenv("OfficialPassword"))    #登入寄件人帳號
                smtp.send_message(content)  #寄件郵件
                print("Client Message send success")
                return
        except Exception as e:
            print(e)
            return

    def developer(type):
        content = MIMEMultipart()   #建立 MIMEMultipart 物件
        content["subject"] = "台北一日遊專案資料庫錯誤!!"
        content["from"] = os.getenv("OfficialEmail")
        content["to"] = os.getenv("FixEmail")
        if type == "attraction_error":
            content.attach(MIMEText("資料庫 : attractions 發生錯誤，請盡快修正。"))
        elif type == "user_error":
            content.attach(MIMEText("資料庫 : user 發生錯誤，請盡快修正。"))
        elif type == "booking_error":
            content.attach(MIMEText("資料庫 : booking 發生錯誤，請盡快修正。"))
        elif type == "order_error":
            content.attach(MIMEText("資料庫 : orders 發生錯誤，請盡快修正。"))
        with smtplib.SMTP(host="smtp.gmail.com", port="587") as smtp:
            try:
                smtp.ehlo()
                smtp.starttls()
                smtp.login(os.getenv("OfficialEmail"), os.getenv("OfficialPassword"))
                smtp.send_message(content)
                print("Send success")
                return
            except Exception as e:
                print(e)
                return