'''
Author: Sarthak Pradhan
Date: 04/01/2023
Description: Desktop app to interface with openai to respond to queries and complete tasks
'''
import os
import tkinter as tk
import requests
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

# Alpha Vantage API endpoint and API key
API_ENDPOINT = 'https://www.alphavantage.co/query'
API_KEY = os.getenv("AV_apis_key")
stock_symbol='MSFT'
def grab_data(stock_symbol):
    # Make an API request to Alpha Vantage to get the latest stock data
    params = {
        'function': 'TIME_SERIES_INTRADAY',
        'symbol': stock_symbol,
        'interval': '1min',
        'apikey': API_KEY,
    }
    response = requests.get(API_ENDPOINT, params=params)
    data = response.json()
    stock_prices = data['Time Series (1min)']
    prices_list = [(k, float(v['4. close'])) for k, v in stock_prices.items()]

    # Calculate the time range to display on the chart (last 30 minutes)
    current_time = prices_list[0][0]
    thirty_minutes_ago = pd.Timestamp(current_time) - pd.Timedelta(minutes=30)
    prices_list_30 = [(k, v) for k, v in prices_list if pd.Timestamp(k) >= thirty_minutes_ago]
    return data

class StockApp(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.create_widgets()

    def create_widgets(self):
        # Dropdown menu for selecting stock
        self.stock_var = tk.StringVar(self)
        self.stock_var.set('select stock')  # default stock selection
        self.stock_options = ['AAPL', 'MSFT', 'AMZN', 'GOOGL']
        self.stock_dropdown = tk.OptionMenu(self, self.stock_var, *self.stock_options, command=self.fetch_stock_data)
        self.stock_dropdown.pack()

        # Label for displaying stock data
        self.stock_data_label = tk.Label(self)
        self.stock_data_label.pack()

        # Create a figure and canvas for the stock chart
        self.stock_figure = plt.Figure(figsize=(8, 4), dpi=100)
        self.stock_canvas = FigureCanvasTkAgg(self.stock_figure, master=self)
        self.stock_canvas.get_tk_widget().pack()

    def fetch_stock_data(self, *args):
        # Retrieve the selected stock symbol from the dropdown menu
        stock_symbol = self.stock_var.get()

        data = grab_data(stock_symbol)

        # Parse the stock data from the API response
        try:
            stock_prices = data['Time Series (1min)']
        except KeyError:
            self.stock_data_label.config(text='Error retrieving data.')
            return

        # Convert the stock prices to a list of tuples (timestamp, price)
        prices_list = [(k, float(v['4. close'])) for k, v in stock_prices.items()]

        # Calculate the time range to display on the chart (last 30 minutes)
        current_time = prices_list[0][0]
        thirty_minutes_ago = pd.Timestamp(current_time) - pd.Timedelta(minutes=30)
        prices_list = [(k, v) for k, v in prices_list if pd.Timestamp(k) >= thirty_minutes_ago]

        # Update the label to display the latest stock data
        last_price = prices_list[0][1]
        stock_data_text = f'{stock_symbol}: ${last_price:.2f}'
        self.stock_data_label.config(text=stock_data_text)

        # Clear the previous chart and plot the new data
        self.stock_figure.clear()
        ax = self.stock_figure.add_subplot(111)
        ax.plot([pd.to_datetime(k) for k, _ in prices_list], [v for _, v in prices_list])
        ax.set_xlabel('Time')
        ax.set_ylabel('Price')
        ax.set_title(f'{stock_symbol} Price')

        # Update the canvas to display the new chart
        self.stock_canvas.draw()


root = tk.Tk()
app = StockApp(master=root)
app.mainloop()
