import sqlite3

# ==============================
# STUDENT OS - DATABASE
# ==============================

conn = sqlite3.connect("student_os.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS students (
    student_id TEXT PRIMARY KEY,
    name TEXT,
    age INTEGER,
    course TEXT,
    semester INTEGER,
    email TEXT,
    phone TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS marks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT,
    subject TEXT,
    marks REAL,
    max_marks REAL,
    UNIQUE(student_id, subject),
    FOREIGN KEY(student_id) REFERENCES students(student_id)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT,
    subject TEXT,
    total_classes INTEGER,
    attended_classes INTEGER,
    UNIQUE(student_id, subject),
    FOREIGN KEY(student_id) REFERENCES students(student_id)
)
""")

conn.commit()


# ==============================
# GRADE CALCULATION
# ==============================

def calculate_grade(percentage):

    if percentage >= 90:
        return "A+"
    elif percentage >= 80:
        return "A"
    elif percentage >= 70:
        return "B"
    elif percentage >= 60:
        return "C"
    elif percentage >= 50:
        return "D"
    elif percentage >= 40:
        return "E"
    else:
        return "F"


# ==============================
# ADD STUDENT
# ==============================

def add_student():

    print("\n--- ADD NEW STUDENT ---")

    sid = input("Enter Student ID: ")
    name = input("Enter Name: ")
    age = int(input("Enter Age: "))
    course = input("Enter Course: ")
    semester = int(input("Enter Semester: "))
    email = input("Enter Email: ")
    phone = input("Enter Phone: ")

    try:
        cursor.execute("""
        INSERT INTO students
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (sid, name, age, course, semester, email, phone))

        conn.commit()
        print("\nStudent Added Successfully!")

    except sqlite3.IntegrityError:
        print("\nStudent ID already exists!")


# ==============================
# UPDATE STUDENT
# ==============================

def update_student():

    print("\n--- UPDATE STUDENT ---")

    sid = input("Enter Student ID: ")

    cursor.execute(
        "SELECT * FROM students WHERE student_id=?",
        (sid,)
    )

    student = cursor.fetchone()

    if student:

        print("Leave a field blank to keep its old value.")

        name = input(f"Name [{student[1]}]: ") or student[1]
        age = input(f"Age [{student[2]}]: ")
        course = input(f"Course [{student[3]}]: ") or student[3]
        semester = input(f"Semester [{student[4]}]: ")
        email = input(f"Email [{student[5]}]: ") or student[5]
        phone = input(f"Phone [{student[6]}]: ") or student[6]

        try:
            age = int(age) if age else student[2]
            semester = int(semester) if semester else student[4]

            cursor.execute("""
            UPDATE students
            SET name=?, age=?, course=?,
                semester=?, email=?, phone=?
            WHERE student_id=?
            """, (name, age, course, semester,
                  email, phone, sid))

            conn.commit()
            print("\nStudent Updated Successfully!")

        except ValueError:
            print("Please enter valid numbers for age and semester.")

    else:
        print("Student Not Found!")


# ==============================
# ADD OR UPDATE MARKS
# ==============================

def add_marks():

    print("\n--- MARKS MANAGEMENT ---")

    sid = input("Enter Student ID: ")

    cursor.execute(
        "SELECT * FROM students WHERE student_id=?",
        (sid,)
    )

    if not cursor.fetchone():
        print("Student Not Found!")
        return

    subject = input("Enter Subject Name: ")

    try:
        marks = float(input("Enter Obtained Marks: "))
        maximum = float(input("Enter Maximum Marks: "))

        if maximum <= 0 or marks < 0 or marks > maximum:
            print("Invalid marks!")
            return

        cursor.execute("""
        INSERT INTO marks
        (student_id, subject, marks, max_marks)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(student_id, subject)
        DO UPDATE SET
        marks=excluded.marks,
        max_marks=excluded.max_marks
        """, (sid, subject, marks, maximum))

        conn.commit()
        print("Marks Saved Successfully!")

    except ValueError:
        print("Please enter valid marks.")


# ==============================
# ATTENDANCE MANAGEMENT
# ==============================

def add_attendance():

    print("\n--- ATTENDANCE MANAGEMENT ---")

    sid = input("Enter Student ID: ")

    cursor.execute(
        "SELECT * FROM students WHERE student_id=?",
        (sid,)
    )

    if not cursor.fetchone():
        print("Student Not Found!")
        return

    subject = input("Enter Subject Name: ")

    try:
        total = int(input("Enter Total Classes: "))
        attended = int(input("Enter Attended Classes: "))

        if total <= 0 or attended < 0 or attended > total:
            print("Invalid attendance data!")
            return

        cursor.execute("""
        INSERT INTO attendance
        (student_id, subject, total_classes, attended_classes)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(student_id, subject)
        DO UPDATE SET
        total_classes=excluded.total_classes,
        attended_classes=excluded.attended_classes
        """, (sid, subject, total, attended))

        conn.commit()
        print("Attendance Saved Successfully!")

    except ValueError:
        print("Please enter valid numbers.")


# ==============================
# VIEW STUDENT PROFILE
# ==============================

def view_student():

    print("\n--- STUDENT PROFILE ---")

    sid = input("Enter Student ID: ")

    cursor.execute(
        "SELECT * FROM students WHERE student_id=?",
        (sid,)
    )

    student = cursor.fetchone()

    if not student:
        print("Student Not Found!")
        return

    print("\n================================")
    print("       STUDENT OS PROFILE")
    print("================================")

    print("Student ID:", student[0])
    print("Name:", student[1])
    print("Age:", student[2])
    print("Course:", student[3])
    print("Semester:", student[4])
    print("Email:", student[5])
    print("Phone:", student[6])

    # Display Marks

    print("\n--- MARKS AND GRADES ---")

    cursor.execute("""
    SELECT subject, marks, max_marks
    FROM marks WHERE student_id=?
    """, (sid,))

    records = cursor.fetchall()

    if records:
        for subject, marks, maximum in records:
            percentage = (marks / maximum) * 100
            grade = calculate_grade(percentage)

            print(
                subject,
                "| Marks:", marks, "/", maximum,
                "| Percentage:", round(percentage, 2), "%",
                "| Grade:", grade
            )
    else:
        print("No Marks Available.")

    # Display Attendance

    print("\n--- ATTENDANCE DETAILS ---")

    cursor.execute("""
    SELECT subject, total_classes, attended_classes
    FROM attendance WHERE student_id=?
    """, (sid,))

    records = cursor.fetchall()

    if records:
        for subject, total, attended in records:
            percentage = (attended / total) * 100

            print(
                subject,
                "| Total:", total,
                "| Attended:", attended,
                "| Attendance:", round(percentage, 2), "%"
            )
    else:
        print("No Attendance Available.")

    print("================================")


# ==============================
# VIEW ALL STUDENTS
# ==============================

def view_all_students():

    print("\n--- ALL REGISTERED STUDENTS ---")

    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()

    if students:
        for s in students:
            print(
                "ID:", s[0],
                "| Name:", s[1],
                "| Course:", s[3],
                "| Semester:", s[4]
            )
    else:
        print("No Students Registered.")


# ==============================
# DELETE STUDENT
# ==============================

def delete_student():

    sid = input("Enter Student ID to Delete: ")

    cursor.execute(
        "SELECT student_id FROM students WHERE student_id=?",
        (sid,)
    )

    if cursor.fetchone():

        confirm = input("Are you sure? (yes/no): ")

        if confirm.lower() == "yes":

            cursor.execute(
                "DELETE FROM marks WHERE student_id=?", (sid,)
            )

            cursor.execute(
                "DELETE FROM attendance WHERE student_id=?", (sid,)
            )

            cursor.execute(
                "DELETE FROM students WHERE student_id=?", (sid,)
            )

            conn.commit()
            print("Student Deleted Successfully!")

    else:
        print("Student Not Found!")


# ==============================
# MAIN STUDENT OS MENU
# ==============================

def main():

    while True:

        print("\n")
        print("================================")
        print("       WELCOME TO STUDENT OS")
        print("================================")
        print("1. Add New Student")
        print("2. Update Student Information")
        print("3. Add / Update Marks")
        print("4. Add / Update Attendance")
        print("5. View Student Profile")
        print("6. View All Students")
        print("7. Delete Student")
        print("8. Exit")
        print("================================")

        choice = input("Enter Your Choice: ")

        if choice == "1":
            add_student()

        elif choice == "2":
            update_student()

        elif choice == "3":
            add_marks()

        elif choice == "4":
            add_attendance()

        elif choice == "5":
            view_student()

        elif choice == "6":
            view_all_students()

        elif choice == "7":
            delete_student()

        elif choice == "8":
            print("Thank You For Using Student OS!")
            conn.close()
            break

        else:
            print("Invalid Choice! Try Again.")


# START PROGRAM

if __name__ == "__main__":
    main()

