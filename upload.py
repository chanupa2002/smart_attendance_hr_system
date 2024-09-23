import tkinter as tk
from tkinter import filedialog, messagebox
import shutil
import os
import mysql.connector
from mysql.connector import Error


DB_HOST = 'localhost'
DB_NAME = 'gov'
DB_USER = 'root'
DB_PASSWORD = 'Athsara@123'

path = 'photos'

def upload_image():
    file_path = filedialog.askopenfilename()
    if file_path:
        filename = os.path.basename(file_path)
        new_name = name_entry.get().strip()
        age = age_entry.get().strip()
        phone = phone_entry.get().strip()
        username = username_entry.get().strip()
        password = password_entry.get().strip()
        hr_salary = hr_salary_entry.get().strip()  # Updated for hrSalary
        
        if new_name and age.isdigit() and phone and username and password and hr_salary.replace('.', '', 1).isdigit():
            file_ext = os.path.splitext(filename)[1]
            new_filename = f"{new_name}{file_ext}"
            destination = os.path.join(path, new_filename)
            try:
                shutil.copy(file_path, destination)

                insert_into_database(new_name, age, phone, new_filename, username, password, float(hr_salary))
                messagebox.showinfo("Success", f"Image {filename} uploaded successfully as {new_filename}.")
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
            data = (name, int(age), phone, photo_filename, username, password, hr_salary)
            cursor.execute(query, data)
            con.commit() 
    except Error as e:
        print(f"Database error: {e}")
    finally:
        if con.is_connected():
            cursor.close()
            con.close()

root = tk.Tk()
root.title("Attendance System - Upload Image")

heading = tk.Label(root, text="Attendance System - Upload Image", font=("Helvetica", 16))
heading.pack(pady=10)

name_label = tk.Label(root, text="Enter Name:")
name_label.pack(pady=5)
name_entry = tk.Entry(root, width=30)
name_entry.pack()

age_label = tk.Label(root, text="Enter Age:")
age_label.pack(pady=5)
age_entry = tk.Entry(root, width=30)
age_entry.pack()

phone_label = tk.Label(root, text="Enter Phone:")
phone_label.pack(pady=5)
phone_entry = tk.Entry(root, width=30)
phone_entry.pack()

username_label = tk.Label(root, text="Enter Username:")
username_label.pack(pady=5)
username_entry = tk.Entry(root, width=30)
username_entry.pack()

password_label = tk.Label(root, text="Enter Password:")
password_label.pack(pady=5)
password_entry = tk.Entry(root, width=30, show='*')  
password_entry.pack()

# Updated hourly salary field (hrSalary)
hr_salary_label = tk.Label(root, text="Enter Hourly Salary:")
hr_salary_label.pack(pady=5)
hr_salary_entry = tk.Entry(root, width=30)
hr_salary_entry.pack()

upload_button = tk.Button(root, text="Upload Image", command=upload_image)
upload_button.pack(pady=20)

root.mainloop()
