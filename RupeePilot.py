import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import csv
import os

# ==========================
# DATA
# ==========================
DATA_DIR = os.path.join(os.path.expanduser("~"), "Documents", "finance_tracker_data")
os.makedirs(DATA_DIR, exist_ok=True)

CATEGORIES = ["Food", "Transport", "Rent", "Education", "Shopping", "Health", "Entertainment", "Savings"]

# ==========================
# COLORS (POSH PALETTE)
# ==========================
BG = "#0B1220"
CARD = "#121A2F"
SURFACE = "#0F172A"
ACCENT = "#4EA8DE"
TEXT = "#E5ECF4"
MUTED = "#94A3B8"

INCOME = "#22C55E"
EXPENSE = "#EF4444"

# ==========================
# FONTS
# ==========================
FONT = ("Segoe UI", 11)
FONT_BOLD = ("Segoe UI", 11, "bold")
FONT_TITLE = ("Segoe UI", 22, "bold")

# ==========================
# STATE
# ==========================
current_user = None
transactions = []

# ==========================
# FILE HELPERS
# ==========================
def user_file(username):
    return os.path.join(DATA_DIR, f"{username}.csv")

def load_user(username):
    global transactions
    transactions = []
    if os.path.exists(user_file(username)):
        with open(user_file(username), newline="") as f:
            for row in csv.reader(f):
                transactions.append(row)

def save_transaction(row):
    with open(user_file(current_user), "a", newline="") as f:
        csv.writer(f).writerow(row)

# ==========================
# LOGIN
# ==========================
def login():
    global current_user
    user = user_entry.get().strip()
    if not user:
        return
    current_user = user
    load_user(user)
    login_frame.pack_forget()
    app_frame.pack(fill="both", expand=True)
    refresh()

# ==========================
# CORE
# ==========================
def add_transaction(t_type):
    try:
        amt = float(amount_entry.get())
        cat = category_box.get()
        if amt <= 0 or not cat:
            raise ValueError

        row = [
            datetime.now().strftime("%d %b %Y"),
            datetime.now().strftime("%Y-%m"),
            t_type,
            cat,
            amt
        ]

        transactions.append(row)
        save_transaction(row)
        amount_entry.delete(0, tk.END)
        refresh()

    except:
        messagebox.showerror("Invalid Input", "Please enter valid data")

def refresh():
    ledger.delete(*ledger.get_children())

    total_i = total_e = 0
    for d in transactions:
        if d[2] == "INCOME":
            total_i += float(d[4])
        else:
            total_e += float(d[4])

    income_lbl.config(text=f"₹{total_i:.2f}")
    expense_lbl.config(text=f"₹{total_e:.2f}")
    balance_lbl.config(text=f"₹{(total_i-total_e):.2f}")

    m = month_filter.get()
    c = category_filter.get()

    visible = 0
    for i, d in enumerate(transactions):
        if (m == "All" or d[1] == m) and (c == "All" or d[3] == c):
            tag = "income" if d[2] == "INCOME" else "expense"
            alt = "alt" if i % 2 == 0 else ""
            ledger.insert("", "end",
                values=(d[0], d[3], d[2], f"₹{float(d[4]):.2f}"),
                tags=(tag, alt)
            )
            visible += 1

    count_label.config(text=f"{visible} transactions")
    insights()

# ==========================
# INSIGHTS
# ==========================
def insights():
    spend = {}
    for d in transactions:
        if d[2] == "EXPENSE":
            spend[d[3]] = spend.get(d[3], 0) + float(d[4])

    insight_box.delete(0, tk.END)

    if not spend:
        insight_box.insert(tk.END, "Not enough data yet.")
        return

    top = max(spend, key=spend.get)
    insight_box.insert(tk.END, f"Highest spending: {top}")
    if spend[top] > 0.5 * sum(spend.values()):
        insight_box.insert(tk.END, f"⚠ {top} dominates your expenses")

# ==========================
# EXPORT
# ==========================
def export_csv():
    path = filedialog.asksaveasfilename(defaultextension=".csv")
    if not path:
        return
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Date", "Month", "Type", "Category", "Amount"])
        writer.writerows(transactions)
    messagebox.showinfo("Exported", "CSV exported successfully")

# ==========================
# ROOT
# ==========================
root = tk.Tk()
root.title("RUPEE PILOT")
root.geometry("920x670")
root.configure(bg=BG)

# ==========================
# TTK STYLE (POSH)
# ==========================
style = ttk.Style()
style.theme_use("default")

style.configure("Treeview",
    background=CARD,
    foreground=TEXT,
    fieldbackground=CARD,
    rowheight=28,
    borderwidth=0
)

style.map("Treeview", background=[("selected", "#1E293B")])

style.configure("Treeview.Heading",
    background=SURFACE,
    foreground=MUTED,
    font=FONT_BOLD
)

style.configure("TCombobox",
    fieldbackground=CARD,
    background=CARD,
    foreground=TEXT
)

style.configure("TScrollbar", background=CARD)

# ==========================
# LOGIN UI
# ==========================
login_frame = tk.Frame(root, bg=BG)
login_frame.pack(expand=True)

tk.Label(login_frame, text="RUPEE PILOT", fg=ACCENT, bg=BG, font=FONT_TITLE).pack(pady=20)

user_entry = tk.Entry(login_frame, font=FONT, bg=CARD, fg=TEXT, insertbackground=TEXT, relief="flat", width=28)
user_entry.pack(pady=10, ipady=6)

tk.Button(
    login_frame,
    text="LOGIN / CREATE USER",
    command=login,
    bg=ACCENT,
    fg=BG,
    font=FONT_BOLD,
    relief="flat",
    padx=20,
    pady=8
).pack(pady=10)

# ==========================
# APP
# ==========================
app_frame = tk.Frame(root, bg=BG)

# STATS CARD
stats = tk.Frame(app_frame, bg=CARD)
stats.pack(fill="x", padx=14, pady=14)

def stat(title, color):
    f = tk.Frame(stats, bg=CARD)
    f.pack(side="left", expand=True, padx=10, pady=10)
    tk.Label(f, text=title, fg=MUTED, bg=CARD).pack()
    l = tk.Label(f, text="₹0", fg=color, bg=CARD, font=("Segoe UI", 17, "bold"))
    l.pack()
    return l

income_lbl = stat("INCOME", INCOME)
expense_lbl = stat("EXPENSE", EXPENSE)
balance_lbl = stat("BALANCE", TEXT)

# CONTROLS
ctrl = tk.Frame(app_frame, bg=CARD)
ctrl.pack(fill="x", padx=14)

amount_entry = tk.Entry(ctrl, bg=SURFACE, fg=TEXT, insertbackground=TEXT, relief="flat", width=12)
amount_entry.pack(side="left", padx=6, ipady=5)

category_box = ttk.Combobox(ctrl, values=CATEGORIES, state="readonly", width=16)
category_box.set("Food")
category_box.pack(side="left", padx=6)

tk.Button(ctrl, text="Add Income", bg=INCOME, fg=BG, command=lambda: add_transaction("INCOME"), relief="flat").pack(side="left", padx=6)
tk.Button(ctrl, text="Add Expense", bg=EXPENSE, fg="white", command=lambda: add_transaction("EXPENSE"), relief="flat").pack(side="left", padx=6)
tk.Button(ctrl, text="Export CSV", bg=SURFACE, fg=TEXT, command=export_csv, relief="flat").pack(side="right", padx=6)

# FILTERS
filters = tk.Frame(app_frame, bg=CARD)
filters.pack(fill="x", padx=14, pady=8)

month_filter = ttk.Combobox(filters, values=["All"], width=14)
month_filter.set("All")
month_filter.pack(side="left", padx=6)

category_filter = ttk.Combobox(filters, values=["All"] + CATEGORIES, width=16)
category_filter.set("All")
category_filter.pack(side="left", padx=6)

tk.Button(filters, text="Apply Filters", bg=ACCENT, fg=BG, command=refresh, relief="flat").pack(side="left", padx=6)

# LEDGER
console = tk.Frame(app_frame, bg=CARD)
console.pack(fill="both", expand=True, padx=14, pady=10)

header = tk.Frame(console, bg=CARD)
header.pack(fill="x", pady=(6, 2))

tk.Label(header, text="Transactions", fg=ACCENT, bg=CARD, font=("Segoe UI", 13, "bold")).pack(side="left")
count_label = tk.Label(header, text="", fg=MUTED, bg=CARD)
count_label.pack(side="right")

table_frame = tk.Frame(console, bg=CARD)
table_frame.pack(fill="both", expand=True)

scrollbar = ttk.Scrollbar(table_frame)
scrollbar.pack(side="right", fill="y")

ledger = ttk.Treeview(
    table_frame,
    columns=("Date", "Category", "Type", "Amount"),
    show="headings",
    yscrollcommand=scrollbar.set
)

scrollbar.config(command=ledger.yview)

ledger.heading("Date", text="Date")
ledger.heading("Category", text="Category")
ledger.heading("Type", text="Type")
ledger.heading("Amount", text="Amount")

ledger.column("Date", width=120, anchor="center")
ledger.column("Category", width=200)
ledger.column("Type", width=90, anchor="center")
ledger.column("Amount", width=120, anchor="e")

ledger.pack(fill="both", expand=True)

ledger.tag_configure("income", foreground=INCOME)
ledger.tag_configure("expense", foreground=EXPENSE)
ledger.tag_configure("alt", background="#0B1328")

# INSIGHTS
insight_frame = tk.Frame(app_frame, bg=CARD)
insight_frame.pack(fill="x", padx=14, pady=10)

tk.Label(insight_frame, text="SMART INSIGHTS", fg=ACCENT, bg=CARD, font=FONT_BOLD).pack(anchor="w")

insight_box = tk.Listbox(
    insight_frame,
    height=4,
    bg=SURFACE,
    fg=TEXT,
    relief="flat",
    highlightthickness=0
)
insight_box.pack(fill="x", pady=6)

root.mainloop()
