import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import shutil
import os
import mysql.connector
from mysql.connector import Error
from datetime import datetime

# Database connection details
DB_HOST = 'localhost'
DB_NAME = 'gov'
DB_USER = 'root'
DB_PASSWORD = 'Athsara@123'

# Path to save uploaded images
path = 'photos'
current_month = None  # Initialize current_month globally

def upload_image(name, age, phone, username, password, hr_salary):
    file_path = filedialog.askopenfilename()
    if file_path:
        filename = os.path.basename(file_path)
        new_filename = f"{name}{os.path.splitext(filename)[1]}"
        destination = os.path.join(path, new_filename)
        
        if name and age.isdigit() and phone and username and password and hr_salary.replace('.', '', 1).isdigit():
            try:
                shutil.copy(file_path, destination)
                insert_into_database(name, int(age), phone, new_filename, username, password, float(hr_salary))
                messagebox.showinfo("Success", f"Image uploaded successfully as {new_filename}.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to upload image: {e}")
        else:
            messagebox.showerror("Error", "Please fill in all fields correctly.")

def insert_into_database(name, age, phone, photo_filename, username, password, hr_salary):
    try:
        con = mysql.connector.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASSWORD)
        if con.is_connected():
            cursor = con.cursor()
            query = """
                INSERT INTO user (name, age, phone, photo, username, password, hrSalary) 
                VALUES (%s, %s, %s, %s, %s, %s, %s);
            """
            cursor.execute(query, (name, age, phone, photo_filename, username, password, hr_salary))
            con.commit()
    except Error as e:
        print(f"Database error: {e}")
    finally:
        if con.is_connected():
            cursor.close()
            con.close()

def fetch_attendance_summary(month):
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
            return cursor.fetchall()
    except Error as e:
        print(f"Database error: {e}")
        return []
    finally:
        if con.is_connected():
            cursor.close()
            con.close()

def calculate_hours(fatime, latime):
    try:
        fatime_dt = datetime.strptime(fatime, "%H:%M:%S")
        latime_dt = datetime.strptime(latime, "%H:%M:%S")
        duration = latime_dt - fatime_dt
        return duration.total_seconds() / 3600
    except Exception as e:
        print(f"Error calculating hours: {e}")
        return 0

def show_monthly_summary(month):
    global current_month  # Declare current_month as global
    current_month = month  # Set current month
    for row in tree.get_children():
        tree.delete(row)

    summary = fetch_attendance_summary(month)
    for username, first_attendance, last_attendance, hr_salary in summary:
        total_hours = calculate_hours(first_attendance, last_attendance) if first_attendance and last_attendance else 0
        total_hours = int(total_hours)  # Truncate to integer
        monthly_pay = hr_salary * total_hours if total_hours >= 1 else 0
        tree.insert("", "end", values=(username, f"{total_hours} hours", f"Rs. {monthly_pay:.2f}"))

def show_user_details(event):
    selected_item = tree.selection()
    if selected_item:
        username = tree.item(selected_item[0], 'values')[0]
        for row in tree_details.get_children():
            tree_details.delete(row)

        details = fetch_user_details(username)
        for date, fatime, latime in details:
            tree_details.insert("", "end", values=(date, fatime, latime))

def fetch_user_details(username):
    global current_month  # Declare current_month as global
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
            return cursor.fetchall()
    except Error as e:
        print(f"Database error: {e}")
        return []
    finally:
        if con.is_connected():
            cursor.close()
            con.close()

def open_registration_window():
    registration_window = tk.Toplevel(root)
    registration_window.title("Register Employee")

    tk.Label(registration_window, text="Name:").pack()
    name_entry = tk.Entry(registration_window)
    name_entry.pack()

    tk.Label(registration_window, text="Age:").pack()
    age_entry = tk.Entry(registration_window)
    age_entry.pack()

    tk.Label(registration_window, text="Phone:").pack()
    phone_entry = tk.Entry(registration_window)
    phone_entry.pack()

    tk.Label(registration_window, text="Username:").pack()
    username_entry = tk.Entry(registration_window)
    username_entry.pack()

    tk.Label(registration_window, text="Password:").pack()
    password_entry = tk.Entry(registration_window, show='*')
    password_entry.pack()

    tk.Label(registration_window, text="Hourly Salary:").pack()
    hr_salary_entry = tk.Entry(registration_window)
    hr_salary_entry.pack()

    upload_button = tk.Button(registration_window, text="Upload Image", command=lambda: upload_image(name_entry.get(), age_entry.get(), phone_entry.get(), username_entry.get(), password_entry.get(), hr_salary_entry.get()))
    upload_button.pack(pady=20)

def open_report_window():
    report_window = tk.Toplevel(root)
    report_window.title("Attendance Report")

    month_frame = tk.Frame(report_window)
    month_frame.pack(pady=20)

    months = [("January", 1), ("February", 2), ("March", 3), ("April", 4), ("May", 5), 
              ("June", 6), ("July", 7), ("August", 8), ("September", 9), ("October", 10), 
              ("November", 11), ("December", 12)]

    for month_name, month_number in months:
        month_button = tk.Button(month_frame, text=month_name, command=lambda m=month_number: show_monthly_summary(m))
        month_button.pack(side=tk.LEFT, padx=5, pady=5)

    # Treeview for Attendance Summary
    summary_frame = tk.Frame(report_window)
    summary_frame.pack(pady=20)

    columns = ("username", "total_hours", "monthly_pay")
    global tree
    tree = ttk.Treeview(summary_frame, columns=columns, show='headings')
    tree.heading("username", text="Username")
    tree.heading("total_hours", text="Total Hours")
    tree.heading("monthly_pay", text="Monthly Pay")
    tree.pack(side=tk.LEFT)

    # Treeview for User Details
    details_frame = tk.Frame(report_window)
    details_frame.pack(pady=20)

    columns_details = ("date", "fatime", "latime")
    global tree_details
    tree_details = ttk.Treeview(details_frame, columns=columns_details, show='headings')
    tree_details.heading("date", text="Date")
    tree_details.heading("fatime", text="First Attendance Time")
    tree_details.heading("latime", text="Last Attendance Time")
    tree_details.pack(side=tk.LEFT)
    tree.bind("<<TreeviewSelect>>", show_user_details)

# Main GUI setup
root = tk.Tk()
root.title("Attendance System")

# Main Frame for Menu
menu_frame = tk.Frame(root)
menu_frame.pack(pady=20)

# Register Employee Button
register_button = tk.Button(menu_frame, text="Register Employee", command=open_registration_window, width=20, height=5)
register_button.grid(row=0, column=0, padx=20, pady=20)

# Report Button
report_button = tk.Button(menu_frame, text="Report", command=open_report_window, width=20, height=5)
report_button.grid(row=0, column=1, padx=20, pady=20)

root.mainloop()
