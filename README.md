🏥 Hospital Management System (HMS)
A complete Hospital Management System built using Flask + SQLite as a DBMS project.
This system allows patients to book appointments, doctors to manage patients, and provides admin-like views for completed bookings, triggers, and feedback.

🚀 Features
👤 Authentication
Signup (Doctor / Patient)
Login / Logout
Role-based actions and navigation

🧑‍⚕️ Doctor Features
Register as a doctor with department
View all patient bookings
Mark patient as Attended
View Completed Appointments
View Feedback from patients
Personal Doctor Profile with feedback history

🧑‍🦽 Patient Features
Book appointment with:
Date
Time
Department
Slot (Morning/Evening/Night)
View all bookings
Edit or cancel bookings
View Completed Appointments
Submit Feedback for doctors after attending

📋 Admin / System Features
Trigger log system (Insert / Delete / Attended logs)
Doctor and patient management screens
Search by department
Fully responsive UI using Bootstrap

🛠️ Tech Stack
Layer	Technology
Backend	Flask (Python)
Database	SQLite (SQLAlchemy ORM)
Frontend	HTML, CSS, Bootstrap
Authentication	Flask-Login
Templates	Jinja2
Deployment	Localhost / GitHub

📁 Project Structure
DBMS/
│── app.py
│── instance/
│── static/
│   ├── css/
│   └── images/
│── templates/
│   ├── base.html
│   ├── index.html
│   ├── signup.html
│   ├── login.html
│   ├── patient.html
│   ├── doctor.html
│   ├── booking.html
│   ├── edit.html
│   ├── trigers.html
│   ├── completed.html
│   ├── feedback.html
│   └── doctor_profile.html
│── README.md

⚙️ How to Run the Project
▶ Step 1: Clone the Repo
git clone https://github.com/SameekshaShakya/Hospital-Management.git
▶ Step 2: Go into the folder
cd Hospital-Management
▶ Step 3: Create a virtual environment (optional but recommended)
python -m venv venv
Activate:
Windows CMD:
venv\Scripts\activate
PowerShell:
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
venv\Scripts\activate
▶ Step 4: Install dependencies
pip install flask flask_sqlalchemy flask_login werkzeug
▶ Step 5: Run the Flask app
python app.py
▶ Step 6: Open the app in your browser
http://127.0.0.1:5000/

🧠 ER Diagram (Recommended for DBMS viva)
<img width="1024" height="1024" alt="ER Diagram" src="https://github.com/user-attachments/assets/85110d3f-13f6-42d5-9e80-a96a4811a6ec" />

📝 Future Enhancements
Admin dashboard
Email notifications for appointments
Doctor schedules
Prescription and lab reports
Online payments

🙋‍♀️ Author
Sameeksha Shakya
📌 B.Tech CSE
📌 DBMS Project — Hospital Management System
📌 GitHub: SameekshaShakya
