from flask import Flask, render_template, request, redirect, session
import yfinance as yf
import matplotlib.pyplot as plt
import os
import sqlite3
import numpy as np
import csv
from flask import Response
from sklearn.linear_model import LinearRegression

app = Flask(__name__)
app.secret_key = "Q8FU4PMTOKAW2RJ1"

# -----------------------------
# DATABASE INIT (🔥 NEW)
# -----------------------------
def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT,
        password TEXT,
        balance REAL,
        bank_name TEXT,
        account_number TEXT,
        ifsc TEXT,
        auto_trade INTEGER DEFAULT 1
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS trades (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        symbol TEXT,
        entry_price REAL,
        quantity INTEGER,
        stop_loss REAL,
        target REAL,
        status TEXT,
        profit REAL,
        loss REAL,
        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS watchlist (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        symbol TEXT
    )
    """)

    conn.commit()
    conn.close()



# -----------------------------
# DATABASE
# -----------------------------
def get_db():
    return sqlite3.connect("database.db")

# -----------------------------
# BALANCE
# -----------------------------
def get_balance():
    user_id = session.get("user_id")
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM users WHERE id=?", (user_id,))
    data = cursor.fetchone()
    conn.close()
    return data[0] if data else 10000

def update_balance(balance):
    user_id = session.get("user_id")
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET balance=? WHERE id=?", (balance, user_id))
    conn.commit()
    conn.close()

#------------------------------
#auto trade button
#------------------------------
def get_auto_trade():
    user_id = session.get("user_id")
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT auto_trade FROM users WHERE id=?", (user_id,))
    data = cursor.fetchone()
    conn.close()
    return data[0] if data else 1


def update_auto_trade(value):
    user_id = session.get("user_id")
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET auto_trade=? WHERE id=?", (value, user_id))
    conn.commit()
    conn.close()



# -----------------------------
# STOCK DATA
# -----------------------------

def fix_symbol(symbol):
    symbol = symbol.upper()

    # 🔥 FIRST TRY NSE (IMPORTANT)
    stock = yf.Ticker(symbol + ".NS")
    data = stock.history(period="1d")

    if not data.empty:
        return symbol + ".NS"

    # THEN TRY NORMAL (US)
    stock = yf.Ticker(symbol)
    data = stock.history(period="1d")

    if not data.empty:
        return symbol

    return None



def get_stock_data(symbol):
    try:
        # Try original
        stock = yf.Ticker(symbol)
        data = stock.history(period="1d")

        # If empty → try NSE
        if data.empty and not symbol.endswith(".NS"):
            stock = yf.Ticker(symbol + ".NS")
            data = stock.history(period="1d")
            symbol = symbol + ".NS"

        if data.empty:
            return None

        return {
            "symbol": symbol.upper(),
            "open": round(data["Open"].iloc[-1], 2),
            "high": round(data["High"].iloc[-1], 2),
            "low": round(data["Low"].iloc[-1], 2),
            "price": round(data["Close"].iloc[-1], 2),
            "volume": int(data["Volume"].iloc[-1])
        }

    except:
        return None

    
def predict_price(symbol):
    try:
        stock = yf.Ticker(symbol)

        # 🔥 Only 7 days data (for tomorrow prediction)
        data = stock.history(period="7d")

        if data.empty:
            return None

        data = data.dropna()

        if len(data) < 5:
            return None

        data["Days"] = np.arange(len(data))
        X = data[["Days"]]
        y = data["Close"]

        model = LinearRegression()
        model.fit(X, y)

        # Tomorrow day index
        future = [[len(data)]]
        predicted = model.predict(future)[0]

        return round(predicted, 2)

    except Exception as e:
        print("Prediction Error:", e)
        return None

# -----------------------------
# AUTO SIGNAL
# -----------------------------
def get_signal(symbol):
    try:
        stock = yf.Ticker(symbol)
        data = stock.history(period="5d")

        if len(data) < 3:
            return "HOLD"

        prices = data["Close"]

        if prices.iloc[-1] > prices.mean():
            return "BUY"
        elif prices.iloc[-1] < prices.mean():
            return "SELL"
        else:
            return "HOLD"
    except:
        return "HOLD"
    

def get_stock_history(symbol):
    stock = yf.Ticker(symbol)
    data = stock.history(period="7d")

    dates, prices = [], []
    for date, row in data.iterrows():
        dates.append(date.strftime("%Y-%m-%d"))
        prices.append(round(row["Close"], 2))

    return dates, prices

def create_graph(dates, prices):
    if not os.path.exists("static"):
        os.makedirs("static")

    plt.figure(figsize=(7, 4))
    plt.plot(dates, prices, marker="o")
    plt.xticks(rotation=45)
    plt.tight_layout()

    path = "static/stock_graph.png"
    plt.savefig(path)
    plt.close()

    return "/static/stock_graph.png"

# -----------------------------
# ROUTES
# -----------------------------
@app.route("/")
def home():
    return redirect("/login")

# -----------------------------
# LOGIN
# -----------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            session["user_id"] = user[0]
            return redirect("/dashboard")

        return render_template("login.html", message="Invalid Login")

    return render_template("login.html")

# -----------------------------
# REGISTER
# -----------------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
    "INSERT INTO users(email,password,balance,auto_trade) VALUES(?,?,?,?)",
    (email, password, 10000, 1)
)
        
        
        conn.commit()
        conn.close()

        return redirect("/login")

    return render_template("register.html")

#------------------------
#forget password
#------------------------
@app.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form["email"]
        new_password = request.form["new_password"]

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE email=?", (email,))
        user = cursor.fetchone()

        if not user:
            conn.close()
            return render_template("forgot_password.html", message="❌ Email Not Found")

        cursor.execute("UPDATE users SET password=? WHERE email=?", (new_password, email))
        conn.commit()
        conn.close()

        return render_template("forgot_password.html", message="✅ Password Updated! Now Login")

    return render_template("forgot_password.html")

# -----------------------------
# DASHBOARD
# -----------------------------
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/login")

    balance = get_balance()
    trade = session.get("trade")

    error_msg = session.pop("error_msg", None)

    stock = None
    investment = None
    profit = 0
    loss = 0
    current_price = None
    trade_status = None
    max_qty = None

    # ---------------- SIGNAL ----------------
    symbol = session.get("last_symbol")
    signal = None
    predicted_price = None
    auto_trade = get_auto_trade()

    if symbol:
        stock = get_stock_data(symbol)
        signal = get_signal(symbol)
        predicted_price = predict_price(symbol)   # 👈 ADD THIS


    # ---------------- AUTO BUY (FIXED) ----------------
    # ---------------- AUTO BUY FIXED ----------------
    if not trade and stock:
        auto_trade = get_auto_trade()  # 1 = ON, 0 = OFF
        if auto_trade == 1:
            signal = get_signal(symbol)
            if signal == "BUY":
            # Only auto-trade ON & BUY signal → execute
                entry = stock["price"]
                qty = 1
                session["trade"] = {
                    "symbol": symbol,
                    "entry_price": entry,
                    "quantity": qty,
                    "stop_loss": entry * 0.98,
                    "take_profit": entry * 1.03
                }
                trade = session["trade"]
                trade_status = "🤖 AUTO BUY EXECUTED"

    # ---------------- TRADE RUN ----------------
    if trade:
        stock = get_stock_data(trade["symbol"])

        if stock:
            entry = trade["entry_price"]
            qty = trade["quantity"]
            current_price = stock["price"]

            investment = entry * qty

            # 🔥 PNL CALCULATION
            pnl = (current_price - entry) * qty

            if pnl > 0:
                profit = round(pnl, 2)
                loss = 0
            elif pnl < 0:
                profit = 0
                loss = round(abs(pnl), 2)
            else:
                profit = 0
                loss = 0

            print("ENTRY:", entry)
            print("CURRENT:", current_price)
            print("PNL:", pnl)

            trade_status = "📊 Trade Running"

            # 🔥 EXIT FLAG
            exit_trade = False

           

           # ---------------- STOP LOSS FIRST ----------------
        if current_price <= trade["stop_loss"]:
            trade_status = "🔴 Stop Loss Hit"
            exit_trade = True

        # ---------------- TARGET SECOND ----------------
        elif current_price >= trade["take_profit"]:
            trade_status = "🟢 Target Hit"
            exit_trade = True

        # ---------------- AUTO SELL LAST ----------------
        elif signal == "SELL" and auto_trade == 1:
            trade_status = "🤖 AUTO SELL EXIT"
            exit_trade = True

            # 🔥 FINAL EXIT (BALANCE UPDATE)
            if exit_trade:
                old_balance = get_balance()

                new_balance = old_balance + pnl

                update_balance(new_balance)

                print("OLD BALANCE:", old_balance)
                print("PNL:", pnl)
                print("NEW BALANCE:", new_balance)

                # DB UPDATE
                conn = get_db()
                cursor = conn.cursor()
                cursor.execute("""
                UPDATE trades 
                SET status=?, profit=?, loss=? 
                WHERE id = (
                    SELECT MAX(id) FROM trades WHERE user_id=?
                )
                """, (
                    trade_status,
                    profit,
                    loss,
                    session["user_id"]
               ))
                conn.commit()
                conn.close()

                session.pop("trade")

    

            max_qty = int((balance * 5) // entry)
            
            


    return render_template(
        "dashboard.html",
        balance=round(balance, 2),
        stock=stock,
        signal=signal,
        investment=round(investment, 2) if investment else None,
        profit=round(profit, 2),
        loss=round(loss, 2),
        current_price=current_price,
        trade_status=trade_status,
        max_qty=max_qty,
        predicted_price=predicted_price,
        auto_trade=auto_trade,
        error_msg=error_msg 
        
    )


#-------------------------
#toggle_auto_trade
#-------------------------
@app.route("/toggle_auto_trade")
def toggle_auto_trade():
    if "user_id" not in session:
        return redirect("/login")

    current = get_auto_trade()
    new_value = 0 if current == 1 else 1
    update_auto_trade(new_value)

    return redirect("/dashboard")


# -----------------------------
# WATCHLIST ROUTES
# -----------------------------
@app.route("/add_watchlist", methods=["POST"])
def add_watchlist():
    if "user_id" not in session:
        return redirect("/login")

    symbol = request.form["symbol"]

    fixed_symbol = fix_symbol(symbol)

    if not fixed_symbol:
        return redirect("/dashboard")

    conn = get_db()
    cursor = conn.cursor()

    # duplicate avoid
    cursor.execute("SELECT * FROM watchlist WHERE user_id=? AND symbol=?",
                   (session["user_id"], fixed_symbol))
    exist = cursor.fetchone()

    if not exist:
        cursor.execute("INSERT INTO watchlist(user_id, symbol) VALUES(?,?)",
                       (session["user_id"], fixed_symbol))

    conn.commit()
    conn.close()

    return redirect("/dashboard")


@app.route("/remove_watchlist/<symbol>")
def remove_watchlist(symbol):
    if "user_id" not in session:
        return redirect("/login")

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM watchlist WHERE user_id=? AND symbol=?",
                   (session["user_id"], symbol))

    conn.commit()
    conn.close()

    return redirect("/dashboard")


@app.route("/watchlist")
def watchlist_page():
    if "user_id" not in session:
        return redirect("/login")

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT symbol FROM watchlist WHERE user_id=?", (session["user_id"],))
    watchlist = cursor.fetchall()
    conn.close()

    return render_template("watchlist.html", watchlist=watchlist, balance=get_balance())

@app.route("/watch/<symbol>")
def watch(symbol):
    session["last_symbol"] = symbol
    return redirect("/dashboard")


#-----------------------
#protofil
#------------------------
@app.route("/portfolio")
def portfolio():
    if "user_id" not in session:
        return redirect("/login")

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM trades WHERE user_id=? ORDER BY id DESC", (session["user_id"],))
    trades = cursor.fetchall()

    conn.close()

    total_profit = sum([t[8] for t in trades])
    total_loss = sum([t[9] for t in trades])
    net = total_profit - total_loss

    return render_template(
        "portfolio.html",
        trades=trades,
        total_profit=round(total_profit, 2),
        total_loss=round(total_loss, 2),
        net=round(net, 2),
        balance=round(get_balance(), 2)
    )

#---------------------------
#risk analisys
#----------------------

@app.route("/risk_analysis")
def risk_analysis():
    if "user_id" not in session:
        return redirect("/login")

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT status, profit, loss FROM trades WHERE user_id=?", (session["user_id"],))
    trades = cursor.fetchall()

    conn.close()

    target_hits = 0
    stoploss_hits = 0
    auto_sell = 0
    running = 0

    total_profit = 0
    total_loss = 0

    for t in trades:
        status = t[0]
        profit = t[1]
        loss = t[2]

        total_profit += profit
        total_loss += loss

        if "Target" in status:
            target_hits += 1
        elif "Stop" in status:
            stoploss_hits += 1
        elif "AUTO SELL" in status:
            auto_sell += 1
        else:
            running += 1

    total_trades = len(trades)
    win_rate = (target_hits / total_trades) * 100 if total_trades > 0 else 0

    return render_template(
        "risk_analysis.html",
        total_trades=total_trades,
        target_hits=target_hits,
        stoploss_hits=stoploss_hits,
        auto_sell=auto_sell,
        running=running,
        total_profit=round(total_profit, 2),
        total_loss=round(total_loss, 2),
        win_rate=round(win_rate, 2)
    )


# -----------------------------
# ADD FUNDS
# -----------------------------
@app.route("/add_funds", methods=["POST"])
def add_funds():
    amount = float(request.form["amount"])
    balance = get_balance()
    balance += amount
    update_balance(balance)
    return redirect("/dashboard")

# -----------------------------
# SEARCH
# -----------------------------
@app.route("/search", methods=["POST"])
def search():
    symbol = request.form["symbol"]

    fixed_symbol = fix_symbol(symbol)

    if not fixed_symbol:
        session["last_symbol"] = None
        session["error_msg"] = "❌ Invalid Stock Symbol"
        return redirect("/dashboard")

    session["last_symbol"] = fixed_symbol
    return redirect("/dashboard")

#-----------------------------
#trade
#-----------------------------

@app.route("/trade", methods=["POST"])
def trade():

    # 🔴 STEP 1: CHECK FIRST (IMPORTANT)
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM trades WHERE user_id=? AND status='Running'", (session["user_id"],))
    running = cursor.fetchone()

    if running:
        conn.close()
        session["error_msg"] = "⚠ Trade already running! First SELL"
        return redirect("/dashboard")

    # 🔵 STEP 2: GET FORM DATA
    symbol = request.form["symbol"]
    entry_price = float(request.form["entry_price"])
    quantity = int(request.form["quantity"])
    stop_loss = float(request.form["stop_loss"])
    take_profit = float(request.form["take_profit"])

    balance = get_balance()
    margin = balance * 5
    investment = entry_price * quantity

    # 🔴 STEP 3: LIMIT CHECK
    if investment > margin:
        conn.close()
        session["error_msg"] = f"❌ Max limit ₹{round(margin,2)}"
        return redirect("/dashboard")

    # 🔵 STEP 4: SAVE TO SESSION
    session["trade"] = {
        "symbol": symbol,
        "entry_price": entry_price,
        "quantity": quantity,
        "stop_loss": stop_loss,
        "take_profit": take_profit
    }

    # 🔵 STEP 5: SAVE TO DATABASE
    cursor.execute("""
    INSERT INTO trades(user_id, symbol, entry_price, quantity, stop_loss, target, status, profit, loss)
    VALUES(?,?,?,?,?,?,?,?,?)
    """, (
        session["user_id"],
        symbol,
        entry_price,
        quantity,
        stop_loss,
        take_profit,
        "Running",
        0,
        0
    ))

    conn.commit()
    conn.close()

    return redirect("/dashboard")

@app.route("/sell", methods=["POST"])
def sell():
    conn = get_db()
    cursor = conn.cursor()

    # running trade close cheyyi
    cursor.execute("""
    UPDATE trades 
    SET status='CLOSED'
    WHERE user_id=? AND status='Running'
    """, (session["user_id"],))

    conn.commit()
    conn.close()

    # session trade remove
    session.pop("trade", None)

    return redirect("/dashboard")


# -----------------------------
# LIVE DATA (🔥 NEW)
# -----------------------------
@app.route("/live_data")
def live_data():
    if "trade" not in session:
        return {"status": "NO TRADE"}

    trade = session.get("trade")

    stock = get_stock_data(trade["symbol"])

    if not stock:
        return {"status": "ERROR"}

    current_price = stock["price"]
    entry = trade["entry_price"]
    qty = trade["quantity"]

    pnl = (current_price - entry) * qty

    status = "RUNNING"

    if current_price <= trade["stop_loss"]:
        status = "STOP LOSS HIT"
    elif current_price >= trade["take_profit"]:
        status = "TARGET HIT"

    return {
        "status": status,
        "price": current_price,
        "profit": round(pnl, 2)
    }

# -----------------------------
# TRADE HISTORY (🔥 NEW)
# -----------------------------
@app.route("/trade_history")
def trade_history():
    if "user_id" not in session:
        return redirect("/login")

    status_filter = request.args.get("status")

    conn = get_db()
    cursor = conn.cursor()

    if status_filter and status_filter != "ALL":
        cursor.execute(
            "SELECT * FROM trades WHERE user_id=? AND status LIKE ? ORDER BY id DESC",
            (session["user_id"], f"%{status_filter}%")
        )
    else:
        cursor.execute(
            "SELECT * FROM trades WHERE user_id=? ORDER BY id DESC",
            (session["user_id"],)
        )

    trades = cursor.fetchall()
    conn.close()

    total_profit = sum([t[8] for t in trades])
    total_loss = sum([t[9] for t in trades])
    net = total_profit - total_loss

    return render_template(
        "trade_history.html",
        trades=trades,
        total_profit=round(total_profit, 2),
        total_loss=round(total_loss, 2),
        net=round(net, 2),
        status_filter=status_filter if status_filter else "ALL"
    )


#--------------
#download files
#-------------------


@app.route("/download_history")
def download_history():
    if "user_id" not in session:
        return redirect("/login")

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT symbol, entry_price, quantity, stop_loss, target, status, profit, loss, date
        FROM trades WHERE user_id=?
    """, (session["user_id"],))
    trades = cursor.fetchall()
    conn.close()

    csv_data = "Stock,Entry,Qty,StopLoss,Target,Status,Profit,Loss,Date\n"

    for t in trades:
        csv_data += f"{t[0]},{t[1]},{t[2]},{t[3]},{t[4]},{t[5]},{t[6]},{t[7]},{t[8]}\n"

    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=trade_history.csv"}
    )

# -----------------------------
# ADD BANK ACCOUNT
# -----------------------------
@app.route("/add_bank", methods=["GET", "POST"])
def add_bank():
    if "user_id" not in session:
        return redirect("/login")

    if request.method == "POST":
        bank = request.form["bank"]
        account = request.form["account"]
        ifsc = request.form["ifsc"]

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("""
        UPDATE users 
        SET bank_name=?, account_number=?, ifsc=?
        WHERE id=?
        """, (bank, account, ifsc, session["user_id"]))

        conn.commit()
        conn.close()

        return redirect("/profile")

    return render_template("add_bank.html")

   


#-------------
#profile
#--------------------
# -----------------------------
# PROFILE
# -----------------------------
@app.route("/profile")
def profile():
    if "user_id" not in session:
        return redirect("/login")

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT email, balance, bank_name, account_number, ifsc 
    FROM users WHERE id=?
    """, (session["user_id"],))

    user = cursor.fetchone()
    conn.close()

    return render_template(
        "profile.html",
        email=user[0],
        balance=user[1],
        bank=user[2],
        account=user[3],
        ifsc=user[4]
    )


# -----------------------------
# SETTINGS
# -----------------------------
@app.route("/settings")
def settings():
    if "user_id" not in session:
        return redirect("/login")
    return render_template("settings.html")
# -----------------------------
# CHANGE PASSWORD
# -----------------------------
@app.route("/change_password", methods=["POST"])
def change_password():
    if "user_id" not in session:
        return redirect("/login")

    old_password = request.form["old_password"]
    new_password = request.form["new_password"]

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT password FROM users WHERE id=?", (session["user_id"],))
    user = cursor.fetchone()

    if not user or user[0] != old_password:
        conn.close()
        return render_template("settings.html", message="❌ Old Password Wrong!")

    cursor.execute("UPDATE users SET password=? WHERE id=?",
                   (new_password, session["user_id"]))
    conn.commit()
    conn.close()

    return render_template("settings.html", message="✅ Password Updated Successfully!")


# -----------------------------
# UPDATE PROFILE EMAIL
# -----------------------------
@app.route("/update_profile", methods=["POST"])
def update_profile():
    if "user_id" not in session:
        return redirect("/login")

    new_email = request.form["email"]

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET email=? WHERE id=?",
                   (new_email, session["user_id"]))
    conn.commit()
    conn.close()

    return render_template("settings.html", message="✅ Email Updated Successfully!")


# -----------------------------
# RESET BALANCE
# -----------------------------
@app.route("/reset_balance", methods=["POST"])
def reset_balance():
    if "user_id" not in session:
        return redirect("/login")

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET balance=? WHERE id=?",
                   (10000, session["user_id"]))
    conn.commit()
    conn.close()

    return render_template("settings.html", message="✅ Balance Reset to ₹10000")


# -----------------------------
# DELETE ACCOUNT
# -----------------------------
@app.route("/delete_account", methods=["POST"])
def delete_account():
    if "user_id" not in session:
        return redirect("/login")

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM trades WHERE user_id=?", (session["user_id"],))
    cursor.execute("DELETE FROM watchlist WHERE user_id=?", (session["user_id"],))
    cursor.execute("DELETE FROM users WHERE id=?", (session["user_id"],))

    conn.commit()
    conn.close()

    session.clear()
    return redirect("/register")

# -----------------------------
# LOGOUT
# -----------------------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

#--------------------------------
#help center
#------------------------
@app.route("/help")
def help_page():
    return render_template("help.html")


# -----------------------------
# RUN
# -----------------------------
if __name__ == "__main__":
    init_db()   # 🔥 IMPORTANT
    app.run(debug=True)


