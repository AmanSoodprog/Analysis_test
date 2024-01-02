from flask import Flask, render_template, request
import requests
from tradingview_ta import TA_Handler, Interval
import redis

from jugaad_data.nse import NSELive

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

@app.route('/login')
def logins():
    return render_template('index.html')
     

@app.route('/predict', methods=['POST'])
def predict():
        stock_symbol = request.form['stock_symbol']
        n = NSELive()
        q = n.stock_quote(stock_symbol)
        print(q['priceInfo'])
        output= TA_Handler(symbol=stock_symbol, screener="India",exchange="NSE",interval="15m")
        indicator_data=output.get_analysis().summary
        prediction = indicator_data
        indicators=output.get_analysis().indicators
        indicators['SMA50'] = "{:.2f}".format(indicators['SMA50'])
        indicators['SMA200'] = "{:.2f}".format(indicators['SMA200'])
        indicators['EMA50'] = "{:.2f}".format(indicators['EMA50'])
        indicators['EMA200'] = "{:.2f}".format(indicators['EMA200'])
        indicators['RSI'] = "{:.2f}".format(indicators['RSI'])
        #test
        return render_template('result.html', prediction=prediction,indicators=indicators,symbol=stock_symbol,ltp=q['priceInfo']['lastPrice'])
    
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
