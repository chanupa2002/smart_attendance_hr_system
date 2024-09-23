import mysql.connector
from mysql.connector import Error

query = "INSERT INTO user (name, age, phone, username, password) VALUES (%s, %s, %s, %s, %s);"
data = ('Livni Chamathka', 21, '0715645324', 'livini', 'Livini@123')

try:
    con = mysql.connector.connect(host='localhost', database='gov', user='root', password='Athsara@123')
    
    if con.is_connected():
        cursor = con.cursor()
        cursor.execute(query, data)  
        con.commit() 
        print("Record inserted successfully")
except Error as e:
    print(f"Error: {e}")  
finally:
    if con.is_connected():
        cursor.close()  
        con.close()  
