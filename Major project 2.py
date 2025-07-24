import tkinter as tk
from tkinter import messagebox
import sqlite3
from datetime import datetime

menu = {
    "Burger": 100,
    "Pizza": 250,
    "Pasta": 150,
    "Fries": 80,
    "Coke": 40
}

order = {}

def init_db():
    conn = sqlite3.connect("billing.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            items TEXT,
            subtotal REAL,
            gst REAL,
            total REAL,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()

def add_item():
    item = item_var.get()
    try:
        qty = int(qty_entry.get())
        if qty <= 0:
            raise ValueError
        order[item] = order.get(item, 0) + qty
        update_bill()
        qty_entry.delete(0, tk.END)
    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter a valid quantity")

def update_bill():
    bill_text.delete(1.0, tk.END)
    total = 0
    for item, qty in order.items():
        subtotal = menu[item] * qty
        bill_text.insert(tk.END, f"{item:10} x {qty} = ₹{subtotal}\n")
        total += subtotal
    gst = total * 0.05
    grand_total = total + gst
    bill_text.insert(tk.END, f"\nSubtotal     : ₹{total}")
    bill_text.insert(tk.END, f"\nGST (5%)     : ₹{gst:.2f}")
    bill_text.insert(tk.END, f"\nTotal Amount : ₹{grand_total:.2f}")


def save_bill():
    if not order:
        messagebox.showinfo("Empty Order", "No items to save.")
        return
    total = sum(menu[item] * qty for item, qty in order.items())
    gst = total * 0.05
    grand_total = total + gst
    items_str = ", ".join([f"{item} x {qty}" for item, qty in order.items()])
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

  
    conn = sqlite3.connect("billing.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO bills (items, subtotal, gst, total, timestamp) VALUES (?, ?, ?, ?, ?)",
                   (items_str, total, gst, grand_total, timestamp))
    conn.commit()
    conn.close()

    with open("gui_bill.txt", "w") as f:
        f.write("🧾 Final Bill\n")
        f.write("-----------------------------\n")
        for item, qty in order.items():
            f.write(f"{item:10} x {qty} = ₹{menu[item] * qty}\n")
        f.write("-----------------------------\n")
        f.write(f"Subtotal     : ₹{total}\n")
        f.write(f"GST (5%)     : ₹{gst:.2f}\n")
        f.write(f"Total Amount : ₹{grand_total:.2f}\n")
        f.write(f"Date         : {timestamp}\n")

    messagebox.showinfo("Saved", "✅ Bill saved to database and gui_bill.txt")

def clear_order():
    order.clear()
    update_bill()

root = tk.Tk()
root.title("🧾 Billing System with Database")
root.geometry("500x550")
root.resizable(False, False)

tk.Label(root, text="Select Item:", font=("Arial", 12)).pack(pady=5)
item_var = tk.StringVar(value="Burger")
tk.OptionMenu(root, item_var, *menu.keys()).pack()

tk.Label(root, text="Enter Quantity:", font=("Arial", 12)).pack(pady=5)
qty_entry = tk.Entry(root)
qty_entry.pack()

tk.Button(root, text="Add Item", command=add_item, bg="lightgreen").pack(pady=10)
tk.Button(root, text="Save Bill", command=save_bill, bg="lightblue").pack(pady=5)
tk.Button(root, text="Clear Order", command=clear_order, bg="lightcoral").pack(pady=5)

tk.Label(root, text="\n🧾 Your Bill:", font=("Arial", 12, "bold")).pack()
bill_text = tk.Text(root, height=15, width=50, font=("Courier", 10))
bill_text.pack()

init_db()
root.mainloop()
