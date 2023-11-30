from flask import Flask, render_template, request
import requests
from tradingview_ta import TA_Handler, Interval

app = Flask(__name__)

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

if __name__ == '__main__':
    app.run(debug=True)
