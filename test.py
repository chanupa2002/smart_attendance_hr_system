import cv2
import numpy as np
import face_recognition
import os
from datetime import datetime
import mysql.connector
from mysql.connector import Error
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Database connection details
DB_HOST = 'localhost'
DB_NAME = 'gov'
DB_USER = 'root'
DB_PASSWORD = 'Athsara@123'

path = 'photos'
images = []
classNames = []
encodeListKnown = []

def load_images():
    global images, classNames, encodeListKnown
    images = []
    classNames = []
    myList = os.listdir(path)
    for cl in myList:
        curImg = cv2.imread(f'{path}/{cl}')
        images.append(curImg)
        classNames.append(os.path.splitext(cl)[0])  
    encodeListKnown = findEncodings(images)
    print('Encoding Complete')

def findEncodings(images):
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList

def markAttendance(name):
    try:
        con = mysql.connector.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASSWORD)
        if con.is_connected():
            cursor = con.cursor()

            cursor.execute("SELECT userId, username FROM user WHERE name = %s", (name,))
            result = cursor.fetchone()
            if result:
                userId, username = result
                
                now = datetime.now()
                date = now.strftime('%Y-%m-%d')
                time = now.strftime('%H:%M:%S')

                attendance_check_query = "SELECT fatime, latime FROM attendance WHERE userId = %s AND date = %s"
                cursor.execute(attendance_check_query, (userId, date))
                attendance_result = cursor.fetchone()

                if attendance_result:
                    update_attendance_query = "UPDATE attendance SET latime = %s WHERE userId = %s AND date = %s"
                    cursor.execute(update_attendance_query, (time, userId, date))
                    con.commit()
                    print(f"Attendance updated for {name}. Last attend time: {time} on {date}")
                else:
                    insert_attendance_query = "INSERT INTO attendance (userId, username, date, fatime, latime) VALUES (%s, %s, %s, %s, %s)"
                    cursor.execute(insert_attendance_query, (userId, username, date, time, time))
                    con.commit()
                    print(f"Attendance marked for {name}. First attend time: {time} on {date}")

    except Error as e:
        print(f"Database error: {e}")
    finally:
        if con.is_connected():
            cursor.close()
            con.close()

def run_face_recognition():
    cap = cv2.VideoCapture(0)  
    while True:
        success, img = cap.read()
        imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25) 
        imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

        
        facesCurFrame = face_recognition.face_locations(imgS)
        encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)

        for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
            matchIndex = np.argmin(faceDis) 
            if matches[matchIndex]:
                name = classNames[matchIndex].upper() 
                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4  
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
                cv2.putText(img, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)

                markAttendance(name)  

        cv2.imshow('Webcam', img)
        if cv2.waitKey(1) & 0xFF == ord('q'):  
            break

    cap.release()
    cv2.destroyAllWindows()

class Watcher(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith(('.png', '.jpg', '.jpeg')):
            load_images()  

def start_watching():
    event_handler = Watcher()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=False)
    observer.start()
    try:
        while True:
            pass  
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    load_images() 
    threading.Thread(target=start_watching).start()  
    run_face_recognition() 
