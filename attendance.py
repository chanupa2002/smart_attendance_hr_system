import tkinter as tk
from tkinter import ttk
import mysql.connector
from mysql.connector import Error
from datetime import datetime

# Database connection details
DB_HOST = 'localhost'
DB_NAME = 'gov'
DB_USER = 'root'
DB_PASSWORD = 'Athsara@123'

def fetch_attendance_summary(month):
    """Fetch attendance summary and hrSalary for a given month from the database."""
    try:
        con = mysql.connector.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASSWORD)
        if con.is_connected():
            cursor = con.cursor()
            query = """
                SELECT u.username, 
                       MIN(a.fatime) AS first_attendance, 
                       MAX(a.latime) AS last_attendance,
                       u.hrSalary
                FROM attendance a
                JOIN user u ON a.username = u.username
                WHERE DATE_FORMAT(STR_TO_DATE(a.date, '%Y-%m-%d'), '%m') = %s
                GROUP BY u.username, u.hrSalary;
            """
            cursor.execute(query, (month,))
            result = cursor.fetchall()
            return result
    except Error as e:
        print(f"Database error: {e}")
        return []
    finally:
        if con.is_connected():
            cursor.close()
            con.close()

def convert_to_datetime(time_str):
    """Convert time string to datetime object."""
    try:
        return datetime.strptime(time_str, "%H:%M:%S")
    except ValueError:
        return None

def calculate_hours(fatime, latime):
    """Calculate hours between first and last attendance times."""
    try:
        fatime_dt = convert_to_datetime(fatime)
        latime_dt = convert_to_datetime(latime)
        if fatime_dt and latime_dt:
            duration = latime_dt - fatime_dt
            return duration.total_seconds() / 3600
        return 0
    except Exception as e:
        print(f"Error calculating hours: {e}")
        return 0

def show_monthly_summary(month):
    """Display the monthly summary of attendance."""
    for row in tree.get_children():
        tree.delete(row)

    summary = fetch_attendance_summary(month)
    for username, first_attendance, last_attendance, hr_salary in summary:
        if first_attendance and last_attendance:
            total_hours = calculate_hours(first_attendance, last_attendance)
            total_hours = int(total_hours)  # Truncate to integer (5.8 becomes 5)
        else:
            total_hours = 0
        
        # Condition: If total hours are less than 1 hour, monthly pay is 0
        if total_hours < 1:
            monthly_pay = 0
        else:
            monthly_pay = hr_salary * total_hours  # Calculate monthly pay using truncated hours

        tree.insert("", "end", values=(username, f"{total_hours} hours", f"Rs. {monthly_pay:.2f}"))

def on_month_button_click(month):
    """Handle month button click event."""
    global current_month
    current_month = month
    show_monthly_summary(month)

def fetch_user_details(username):
    """Fetch detailed attendance for a specific user."""
    try:
        con = mysql.connector.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASSWORD)
        if con.is_connected():
            cursor = con.cursor()
            query = """
                SELECT date, fatime, latime 
                FROM attendance
                WHERE username = %s AND DATE_FORMAT(STR_TO_DATE(date, '%Y-%m-%d'), '%m') = %s
            """
            cursor.execute(query, (username, current_month))
            result = cursor.fetchall()
            return result
    except Error as e:
        print(f"Database error: {e}")
        return []
    finally:
        if con.is_connected():
            cursor.close()
            con.close()

def show_user_details(event):
    """Display detailed records for the selected user."""
    selected_item = tree.selection()
    if selected_item:
        username = tree.item(selected_item[0], 'values')[0]
        for row in tree_details.get_children():
            tree_details.delete(row)

        details = fetch_user_details(username)
        for date, fatime, latime in details:
            tree_details.insert("", "end", values=(date, fatime, latime))

def setup_gui():
    """Setup the Tkinter GUI."""
    global root, tree, tree_details, month_buttons_frame, current_month

    root = tk.Tk()
    root.title("Attendance System")

    # Main Frame for Month Buttons
    main_frame = tk.Frame(root)
    main_frame.pack(pady=20)

    month_buttons_frame = tk.Frame(main_frame)
    month_buttons_frame.pack()

    months = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]

    for i, month_name in enumerate(months):
        month_number = i + 1
        month_button = tk.Button(month_buttons_frame, text=month_name, width=20, command=lambda m=month_number: on_month_button_click(m))
        month_button.grid(row=i//3, column=i%3, padx=5, pady=5)

    # Frame for Attendance Summary
    summary_frame = tk.Frame(root)
    summary_frame.pack(pady=20)

    columns = ("username", "total_hours", "monthly_pay")
    tree = ttk.Treeview(summary_frame, columns=columns, show='headings')
    tree.heading("username", text="Username")
    tree.heading("total_hours", text="Total Hours")
    tree.heading("monthly_pay", text="Monthly Pay")

    tree.column("username", width=150)
    tree.column("total_hours", width=150)
    tree.column("monthly_pay", width=150)
    
    tree.pack(side=tk.LEFT)
    tree.bind("<<TreeviewSelect>>", show_user_details)  # Bind selection event

    # Frame for Detailed Attendance Records
    details_frame = tk.Frame(root)
    details_frame.pack(pady=20)

    columns_details = ("date", "fatime", "latime")
    tree_details = ttk.Treeview(details_frame, columns=columns_details, show='headings')
    tree_details.heading("date", text="Date")
    tree_details.heading("fatime", text="First Attendance Time")
    tree_details.heading("latime", text="Last Attendance Time")
    
    tree_details.column("date", width=100)
    tree_details.column("fatime", width=150)
    tree_details.column("latime", width=150)
    
    tree_details.pack(side=tk.LEFT)

    root.mainloop()

if __name__ == "__main__":
    setup_gui()
