import sqlite3


def add_student(name, college_id):
    connection = sqlite3.connect("students.db") 
    cursor = connection.cursor()

    try:
        #hum wahi coloumn use kar rahe hain jo database.py me bnnya tha 
        cursor.execute(
            """
            INSERT INTO students (name, college_id )
            VALUES (? , ?)
        """,
            (name,college_id),
        )

        connection.commit()
        print("student added successfully!")
    except sqlite3.IntegrityError:
          print("ERROR: ye college id phele se hi registered hai!")
    finally:
         connection.close()


       #user se input S
name =input("enter your name :")
college_id = input("enter college id:  ")

    #fuction call
add_student(name, college_id)
        
            
