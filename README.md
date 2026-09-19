# 📈 Stock Tracker Basic

A Python-based stock tracking and portfolio management web application that allows users to monitor stock prices, manage a virtual portfolio, maintain a watchlist, and analyze stock performance.

## 🚀 Features

* 🔐 User Registration and Login
* 💰 Virtual Balance and Fund Management
* 📊 Real-Time/Latest Stock Price Tracking
* ⭐ Stock Watchlist
* 📈 Portfolio Management
* 💹 Buy and Sell Stock Simulation
* 🛡️ Risk Analysis
* 📉 Stock Price Visualization
* 🤖 Basic Stock Price Prediction using Machine Learning
* 🎯 Stop-Loss and Target Price Support
* 📋 Transaction/Trade Tracking

## 🛠️ Technologies Used

* **Python**
* **Flask**
* **SQLite**
* **yFinance**
* **Pandas**
* **NumPy**
* **Matplotlib**
* **Scikit-learn**
* **HTML**
* **CSS**
* **Jinja2**

## 📂 Project Structure

```text
Stock-Tracker-Basic/
│
├── app.py
├── stock_api.py
├── ml_model.py
├── create_db.py
├── add_user.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── templates/
│   ├── login.html
│   ├── dashboard.html
│   ├── portfolio.html
│   ├── watchlist.html
│   └── ...
│
└── static/
    ├── style.css
    └── ...
```

## ⚙️ How to Run

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/Stock-Tracker-Basic.git
```

### 2. Open the Project

```bash
cd Stock-Tracker-Basic
```

### 3. Install Required Libraries

```bash
pip install -r requirements.txt
```

### 4. Create the Database

```bash
python create_db.py
```

### 5. Run the Application

```bash
python app.py
```

### 6. Open in Browser

Go to:

```text
http://127.0.0.1:5000/
```

## 📊 Main Modules

### Dashboard

Displays stock-related information and portfolio details.

### Watchlist

Allows users to add and monitor stocks they are interested in.

### Portfolio

Tracks virtual holdings, available balance, and portfolio value.

### Trading

Provides simulated buying and selling of stocks.

### Risk Analysis

Provides basic analysis to help users understand potential stock risk.

### Machine Learning

Uses historical stock-price data to generate a basic price prediction.

## 👩‍💻 My Contribution

I worked as the **Team Leader** and contributed mainly to the **backend and core project functionality**.

My responsibilities included:

* Coordinating the project team
* Planning project modules
* Developing backend functionality using Python and Flask
* Working with the database
* Integrating stock market data
* Implementing portfolio and trading-related functionality
* Contributing to stock analysis and prediction features
* Testing and debugging the application

## 🎯 Project Objective

The main objective of this project is to build a simple stock-tracking platform where users can explore stock information, manage a virtual portfolio, simulate trades, and view basic stock analysis in one application.

## 🔮 Future Improvements

* Improve stock prediction accuracy
* Add more advanced technical indicators
* Add interactive charts
* Add email notifications and price alerts
* Improve authentication and security
* Deploy the application online
* Add a more advanced portfolio analytics system

## ⚠️ Disclaimer

This project is created for **educational and demonstration purposes**. Stock predictions and analysis provided by the application should not be considered financial advice.
