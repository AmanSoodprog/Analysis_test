from flask import Flask, render_template, request
import requests
from tradingview_ta import TA_Handler, Interval
import redis

app = Flask(__name__)

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

@app.route('/predict', methods=['POST'])
def predict():
        stock_symbol = request.form['stock_symbol']
        
        output= TA_Handler(symbol=stock_symbol, screener="India",exchange="NSE",interval="15m")
        indicator_data=output.get_analysis().summary
        prediction = indicator_data
        return render_template('result.html', prediction=prediction)
    
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
    app.run(debug=True)
