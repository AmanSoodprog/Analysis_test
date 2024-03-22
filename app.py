from flask import Flask, render_template, request
import requests
from tradingview_ta import TA_Handler, Interval
import redis
from pymongo import MongoClient
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from flask import session

app = Flask(__name__)

app.secret_key = 'uh3di2gf92fufb2u2393n9nc'

client = MongoClient('mongodb+srv://Pixel:Pixel7788@cluster0.3dpfxx3.mongodb.net/')
db = client['SnapStocks']
users = db['users']

redis_host = 'redis-10435.c321.us-east-1-2.ec2.cloud.redislabs.com'
redis_port = 10435
redis_db = 0
redis_password = 'wYYoKplw6iKoE9FIcewxehUIiiVmbNIb'  # Replace with your actual Redis password
redis_client = redis.StrictRedis(
        host=redis_host, port=redis_port, db=redis_db, password=redis_password
    )
@app.route('/')
def index():
    return render_template('index.html')





@app.route('/login', methods=['GET','POST'])
def logins():
    if(request.method == 'POST'):
        username = request.form['username']
        password = request.form['password']

        # Fetch the user from the database
        user = users.find_one({'username': username})

        # If the user exists and the password is correct
        if user and check_password_hash(user['password'], password):
            # Log the user in by setting a session variable
            session['logged_in'] = True
            session['username'] = username
            return render_template('login.html')
        else:
            return 'Invalid username or password'
    return render_template('login.html')

@app.route('/predict', methods=['POST'])
def predict():
        stock_symbol = request.form['stock_symbol']

        output= TA_Handler(symbol=stock_symbol, screener="India",exchange="NSE",interval="15m")
        indicator_data=output.get_analysis().summary
        prediction = indicator_data
        indicators=output.get_analysis().indicators
        indicators['SMA50'] = "{:.2f}".format(indicators['SMA50'])
        indicators['SMA200'] = "{:.2f}".format(indicators['SMA200'])
        indicators['EMA50'] = "{:.2f}".format(indicators['EMA50'])
        indicators['EMA200'] = "{:.2f}".format(indicators['EMA200'])
        indicators['RSI'] = "{:.2f}".format(indicators['RSI'])
        li=""
        if 'logged_in' in session:
            li="Yes"
        else:
            li="No"
        #test
        return render_template('result.html', prediction=prediction,indicators=indicators,symbol=stock_symbol,li=li)
    
@app.route('/scan', methods=['POST'])
def scan():
        result_data={}
        stock_names = redis_client.lrange("stock_names", 0, -1)
        print(stock_names)
        for name in stock_names:
            name= name.decode('utf-8')
            stock_symbol = name
            output= TA_Handler(symbol=stock_symbol, screener="India",exchange="NSE",interval="15m")
            indicator_data=output.get_analysis().summary
            prediction = indicator_data
            result_data[name] = indicator_data
        print(result_data)
        return render_template('bulk.html', data=result_data)
        
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
