# student_tracker.py
"""
Student Attendance & Performance Tracker (console)
Features:
- Add student
- Mark attendance (by date, default today)
- Add marks (multiple exams)
- View per-student report (attendance % and average marks)
- Save/load data to students.json automatically
"""

import json
from datetime import datetime
from pathlib import Path

DATA_FILE = Path("students.json")


def load_data():
    if DATA_FILE.exists():
        try:
            return json.loads(DATA_FILE.read_text())
        except Exception:
            print("Warning: failed to read data file, starting with empty database.")
    return {}  # roll -> {name, attendance: {date: "P"/"A"}, marks: [numbers]}


def save_data(db):
    DATA_FILE.write_text(json.dumps(db, indent=2))
    # no return


def input_nonempty(prompt):
    while True:
        s = input(prompt).strip()
        if s:
            return s


def add_student(db):
    roll = input_nonempty("Enter roll number (unique): ")
    if roll in db:
        print("That roll number already exists.")
        return
    name = input_nonempty("Enter student name: ")
    db[roll] = {"name": name, "attendance": {}, "marks": []}
    save_data(db)
    print(f"Student {name} ({roll}) added.")


def list_students(db):
    if not db:
        print("No students in database.")
        return
    print("\nStudents:")
    for r, info in sorted(db.items()):
        print(f"  {r} - {info['name']}")
    print()


def mark_attendance(db):
    if not db:
        print("No students available. Add students first.")
        return
    date_str = input("Enter date (YYYY-MM-DD) [default: today]: ").strip()
    if not date_str:
        date_str = datetime.today().strftime("%Y-%m-%d")
    else:
        # simple validation
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            print("Invalid date format. Use YYYY-MM-DD.")
            return

    print("Mark attendance: P = present, A = absent, S = skip (leave unchanged)")
    for roll, info in sorted(db.items()):
        while True:
            val = input(f"{roll} {info['name']}: (P/A/S) ").strip().upper()
            if val in {"P", "A", "S"}:
                break
            print("Please enter P, A, or S.")
        if val == "S":
            continue
        info["attendance"][date_str] = "P" if val == "P" else "A"

    save_data(db)
    print(f"Attendance recorded for {date_str}.")


def add_marks(db):
    if not db:
        print("No students available. Add students first.")
        return
    roll = input_nonempty("Enter roll number: ")
    if roll not in db:
        print("Student not found.")
        return
    try:
        mark = float(input_nonempty("Enter marks (0-100): "))
    except ValueError:
        print("Invalid number.")
        return
    db[roll]["marks"].append(mark)
    save_data(db)
    print(f"Added {mark} for {db[roll]['name']}.")


def compute_attendance_percent(attendance_dict):
    if not attendance_dict:
        return 0.0
    total = len(attendance_dict)
    present = sum(1 for v in attendance_dict.values() if v == "P")
    return (present / total) * 100.0


def view_report(db):
    if not db:
        print("No students to report.")
        return
    print("\n---- Attendance & Performance Report ----")
    for roll, info in sorted(db.items()):
        att_pct = compute_attendance_percent(info.get("attendance", {}))
        marks = info.get("marks", [])
        avg_marks = sum(marks) / len(marks) if marks else 0.0
        print(f"\nRoll: {roll}")
        print(f"  Name: {info['name']}")
        print(f"  Attendance: {att_pct:.1f}%  (Days recorded: {len(info.get('attendance', {}))})")
        print(f"  Average Marks: {avg_marks:.1f}  (Entries: {len(marks)})")
    print("-----------------------------------------\n")


def student_details(db):
    roll = input_nonempty("Enter roll number: ")
    if roll not in db:
        print("Student not found.")
        return
    info = db[roll]
    print(f"\nDetails for {info['name']} ({roll})")
    print("Attendance records:")
    if not info["attendance"]:
        print("  No attendance recorded.")
    else:
        for d, v in sorted(info["attendance"].items()):
            print(f"  {d}: {v}")
    print("Marks:")
    if not info["marks"]:
        print("  No marks recorded.")
    else:
        for i, m in enumerate(info["marks"], 1):
            print(f"  Exam {i}: {m}")
    print()


def remove_student(db):
    roll = input_nonempty("Enter roll number to remove: ")
    if roll not in db:
        print("Not found.")
        return
    confirm = input(f"Delete {db[roll]['name']} ({roll})? (y/N): ").strip().lower()
    if confirm == "y":
        del db[roll]
        save_data(db)
        print("Deleted.")


def export_csv(db):
    import csv
    path = input("CSV filename to write (default students_export.csv): ").strip() or "students_export.csv"
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["roll", "name", "attendance_days", "present_days", "attendance_pct", "avg_marks"])
        for roll, info in db.items():
            att = info.get("attendance", {})
            total = len(att)
            present = sum(1 for v in att.values() if v == "P")
            pct = (present / total * 100) if total else 0
            marks = info.get("marks", [])
            avg = sum(marks) / len(marks) if marks else 0
            writer.writerow([roll, info["name"], total, present, f"{pct:.1f}", f"{avg:.1f}"])
    print(f"Exported to {path}")


def main_menu():
    db = load_data()
    while True:
        print("\n--- Student Tracker ---")
        print("1. Add student")
        print("2. List students")
        print("3. Mark attendance")
        print("4. Add marks")
        print("5. View report (all)")
        print("6. View single student details")
        print("7. Remove student")
        print("8. Export summary CSV")
        print("9. Exit")
        choice = input("Enter choice: ").strip()
        if choice == "1":
            add_student(db)
        elif choice == "2":
            list_students(db)
        elif choice == "3":
            mark_attendance(db)
        elif choice == "4":
            add_marks(db)
        elif choice == "5":
            view_report(db)
        elif choice == "6":
            student_details(db)
        elif choice == "7":
            remove_student(db)
        elif choice == "8":
            export_csv(db)
        elif choice == "9":
            print("Goodbye!")
            break
        else:
            print("Invalid choice.")


if __name__ == "__main__":
    main_menu()
