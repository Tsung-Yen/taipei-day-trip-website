from flask import *

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

#Booking API
from api.booking import schedule
from api.booking import cart
from api.booking import cancle
app.register_blueprint(schedule)
app.register_blueprint(cart)
app.register_blueprint(cancle)

#Order API
from api.order import pay
from api.order import check
app.register_blueprint(pay)
app.register_blueprint(check)

if __name__=="__main__":
	app.run(host="0.0.0.0",port=3000,debug=True)