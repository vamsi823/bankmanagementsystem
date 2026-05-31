import tkinter as tk
from tkinter import messagebox
import pymysql
from datetime import datetime

#DATABASE CONNECTION 
con = pymysql.connect(
    host="localhost",
    user="root",
    password="root123",
    database="bank",
    cursorclass=pymysql.cursors.DictCursor
)

cursor = con.cursor()

#CREATE TABLES 
cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) UNIQUE,
    password VARCHAR(100),
    balance DECIMAL(12,2) DEFAULT 0.00
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS transactions(
    tid INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100),
    type VARCHAR(50),
    amount DECIMAL(12,2),
    date_time VARCHAR(100)
)
""")

con.commit()

#MAIN WINDOW 
root = tk.Tk()
root.title("Bank Management System")
root.geometry("500x600")
root.config(bg="#dff6ff")

#ADD TRANSACTION
def add_transaction(username, ttype, amount):

    date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    sql = """
    INSERT INTO transactions(username,type,amount,date_time)
    VALUES(%s,%s,%s,%s)
    """

    cursor.execute(sql, (username, ttype, amount, date_time))
    con.commit()


#REGISTER 
def register():

    username = entry_user.get()
    password = entry_pass.get()

    if username == "" or password == "":
        messagebox.showerror("Error", "Please Fill All Fields")
        return

    try:
        sql = "INSERT INTO users(username,password) VALUES(%s,%s)"

        cursor.execute(sql, (username, password))

        con.commit()

        messagebox.showinfo("Success", "Registration Successful")

    except:
        messagebox.showerror("Error", "Username Already Exists")


 #LOGIN 
def login():

    username = entry_user.get()
    password = entry_pass.get()

    sql = "SELECT * FROM users WHERE username=%s AND password=%s"

    cursor.execute(sql, (username, password))

    user = cursor.fetchone()

    if user:
        messagebox.showinfo("Success", "Login Successful")
        bank_window(username)

    else:
        messagebox.showerror("Error", "Invalid Username or Password")


#BANK WINDOW 
def bank_window(username):

    win = tk.Toplevel()
    win.title("Bank Menu")
    win.geometry("500x650")
    win.config(bg="#fff4cc")

    tk.Label(
        win,
        text=f"Welcome {username}",
        font=("Arial", 18, "bold"),
        bg="#fff4cc",
        fg="blue"
    ).pack(pady=10)

#AMOUNT LABEL 
    tk.Label(
        win,
        text="Enter Amount",
        font=("Arial", 14),
        bg="#fff4cc"
    ).pack(pady=5)

    entry_amount = tk.Entry(win, font=("Arial", 14))
    entry_amount.pack(pady=5)
 #RECEIVER LABEL
    tk.Label(
        win,
        text="Receiver Username",
        font=("Arial", 14),
        bg="#fff4cc"
    ).pack(pady=5)

    entry_receiver = tk.Entry(win, font=("Arial", 14))
    entry_receiver.pack(pady=5)

 # DEPOSIT
    def deposit():

        amount_text = entry_amount.get()

        if amount_text == "":
            messagebox.showerror("Error", "Please Enter Amount")
            return

        try:
            amount = float(amount_text)

        except:
            messagebox.showerror("Error", "Enter Valid Number")
            return

        if amount <= 0:
            messagebox.showerror("Error", "Invalid Amount")
            return

        sql = "UPDATE users SET balance=balance+%s WHERE username=%s"

        cursor.execute(sql, (amount, username))

        add_transaction(username, "DEPOSIT", amount)

        con.commit()

        messagebox.showinfo("Success", "Amount Deposited")

        entry_amount.delete(0, tk.END)

# WITHDRAW
    def withdraw():

        amount_text = entry_amount.get()

        if amount_text == "":
            messagebox.showerror("Error", "Please Enter Amount")
            return

        try:
            amount = float(amount_text)

        except:
            messagebox.showerror("Error", "Enter Valid Number")
            return

        sql = "SELECT balance FROM users WHERE username=%s"

        cursor.execute(sql, (username,))

        result = cursor.fetchone()

        balance = result['balance']

        if amount <= 0:
            messagebox.showerror("Error", "Invalid Amount")
            return

        elif amount > balance:
            messagebox.showerror("Error", "Insufficient Balance")
            return

        else:

            sql = "UPDATE users SET balance=balance-%s WHERE username=%s"

            cursor.execute(sql, (amount, username))

            add_transaction(username, "WITHDRAW", amount)

            con.commit()

            messagebox.showinfo("Success", "Withdrawal Successful")

            entry_amount.delete(0, tk.END)
#TRANSFER MONEY 
    def transfer_money():
        

        receiver = entry_receiver.get()
        amount_text = entry_amount.get()

        if receiver == username:
            messagebox.showerror(
                "Error",
                "Cannot transfer money to yourself"
            )
            return

        if receiver == "" or amount_text == "":
            messagebox.showerror(
                "Error",
                "Please Fill All Fields"
            )
            return

        try:
            amount = float(amount_text)

            if amount <= 0:
                messagebox.showerror(
                    "Error",
                    "Invalid Amount"
                )
                return

        except ValueError:
            messagebox.showerror(
                "Error",
                "Enter Valid Amount"
            )
            return

    # Check sender balance
        cursor.execute(
            "SELECT balance FROM users WHERE username=%s",
            (username,)
        )

        sender = cursor.fetchone()

        if sender["balance"] < amount:
            messagebox.showerror(
                "Error",
                "Insufficient Balance"
            )
            return

     #Check receiver exists
        cursor.execute(
            "SELECT * FROM users WHERE username=%s",
            (receiver,)
        )

        rec = cursor.fetchone()

        if not rec:
            messagebox.showerror(
                "Error",
                "Receiver Not Found"
            )
            return

        try:
            con.begin()

            cursor.execute(
                "UPDATE users SET balance=balance-%s WHERE username=%s",
                (amount, username)
            )

            cursor.execute(
                "UPDATE users SET balance=balance+%s WHERE username=%s",
                (amount, receiver)
            )

            add_transaction(
                username,
                "TRANSFER SENT",
                amount
            )

            add_transaction(
                receiver,
                "TRANSFER RECEIVED",
                amount
            )

            con.commit()

            messagebox.showinfo(
                "Success",
                "Money Transferred Successfully"
            )

            entry_amount.delete(0, tk.END)
            entry_receiver.delete(0, tk.END)

        except Exception as e:
            con.rollback()

            messagebox.showerror(
                "Error",
                str(e)
            )

        

       
        

#CHECK BALANCE 
    def check_balance():

        sql = "SELECT balance FROM users WHERE username=%s"

        cursor.execute(sql, (username,))

        result = cursor.fetchone()

        messagebox.showinfo(
            "Balance",
            f"Current Balance: ₹{result['balance']}"
        )

    #TRANSACTION HISTORY 
    def history():
        sql = """
        SELECT * FROM transactions
        WHERE username=%s
        ORDER BY tid DESC
        """

        cursor.execute(sql, (username,))
        records = cursor.fetchall()

        text = ""

        for row in records:
            text += f"{row['type']} | ₹{row['amount']} | {row['date_time']}\n"

        if text == "":
            text = "No Transactions"

        messagebox.showinfo("Transaction History", text)

        

   #BUTTONS
    tk.Button(
        win,
        text="Deposit",
        font=("Arial", 12, "bold"),
        bg="green",
        fg="white",
        width=20,
        command=deposit
    ).pack(pady=10)

    tk.Button(
        win,
        text="Withdraw",
        font=("Arial", 12, "bold"),
        bg="red",
        fg="white",
        width=20,
        command=withdraw
    ).pack(pady=10)

    tk.Button(
        win,
        text="Transfer Money",
        font=("Arial", 12, "bold"),
        bg="orange",
        fg="white",
        width=20,
        command=transfer_money
    ).pack(pady=10)

    tk.Button(
        win,
        text="Check Balance",
        font=("Arial", 12, "bold"),
        bg="blue",
        fg="white",
        width=20,
        command=check_balance
    ).pack(pady=10)

    tk.Button(
        win,
        text="Transaction History",
        font=("Arial", 12, "bold"),
        bg="purple",
        fg="white",
        width=20,
        command=history
    ).pack(pady=10)

    tk.Button(
        win,
        text="Logout",
        font=("Arial", 12, "bold"),
        bg="black",
        fg="white",
        width=20,
        command=win.destroy
    ).pack(pady=10)


# TITLE 
tk.Label(
    root,
    text="BANK MANAGEMENT SYSTEM",
    font=("Arial", 20, "bold"),
    bg="#dff6ff",
    fg="darkblue"
).pack(pady=20)

 #USERNAME
tk.Label(
    root,
    text="Username",
    font=("Arial", 14),
    bg="#dff6ff"
).pack()

entry_user = tk.Entry(root, font=("Arial", 14))
entry_user.pack(pady=10)
#PASSWORD
tk.Label(
    root,
    text="Password",
    font=("Arial", 14),
    bg="#dff6ff"
).pack()

entry_pass = tk.Entry(root, show="*", font=("Arial", 14))
entry_pass.pack(pady=10)
#BUTTONS 
tk.Button(
    root,
    text="Register",
    font=("Arial", 12, "bold"),
    bg="green",
    fg="white",
    width=15,
    command=register
).pack(pady=10)

tk.Button(
    root,
    text="Login",
    font=("Arial", 12, "bold"),
    bg="blue",
    fg="white",
    width=15,
    command=login
).pack(pady=10)

tk.Button(
    root,
    text="Exit",
    font=("Arial", 12, "bold"),
    bg="red",
    fg="white",
    width=15,
    command=root.destroy
).pack(pady=10)

 #RUN
root.mainloop()
 #CLOSE CONNECTION 
con.close()



       
        
                

        



       
        
                

        
 
    
