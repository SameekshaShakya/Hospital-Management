from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# --- APP CONFIGURATION ---
app = Flask(__name__)
app.secret_key = 'replace_with_a_real_secret_key'  # change in production
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hms.db'  # local sqlite DB
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- LOGIN MANAGER CONFIGURATION ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # route name of the login view

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- MODELS ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)
    usertype = db.Column(db.String(20), nullable=False)  # 'Patient' or 'Doctor'

class Patient(db.Model):
    pid = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    slot = db.Column(db.String(20), nullable=False)
    disease = db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(50), nullable=False)
    time = db.Column(db.String(50), nullable=False)
    dept = db.Column(db.String(100), nullable=False)
    number = db.Column(db.String(15), nullable=False)

class Doctor(db.Model):
    did = db.Column(db.Integer, primary_key=True)
    doctorname = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    dept = db.Column(db.String(100), nullable=False)

class Triggers(db.Model):
    tid = db.Column(db.Integer, primary_key=True)
    pid = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    action = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.String(50), nullable=False)
    
class CompletedBooking(db.Model):
    cid = db.Column(db.Integer, primary_key=True)
    pid = db.Column(db.Integer, nullable=False)
    doctor = db.Column(db.String(100), nullable=False)
    patient_name = db.Column(db.String(100), nullable=False)
    disease = db.Column(db.String(200), nullable=False)
    dept = db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(50), nullable=False)
    time = db.Column(db.String(50), nullable=False)
    feedback = db.Column(db.String(300), nullable=True)
    

# Create DB tables on first run
with app.app_context():
    db.create_all()

# --- ROUTES ---

@app.route('/')
def index():
    # optionally pass doctors for any page usage; index.html doesn't strictly require it
    return render_template('index.html')

# Signup
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username').strip()
        usertype = request.form.get('usertype')
        email = request.form.get('email').strip().lower()
        password = request.form.get('password')

        if not username or not email or not password or usertype not in ('Patient', 'Doctor'):
            flash("Please fill all fields correctly.", "warning")
            return redirect(url_for('signup'))

        # check duplicates
        if User.query.filter((User.email == email) | (User.username == username)).first():
            flash("Username or email already registered!", "warning")
            return redirect(url_for('signup'))

        hashed = generate_password_hash(password)
        new_user = User(username=username, usertype=usertype, email=email, password=hashed)
        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful. Please login.", "success")
        return redirect(url_for('login'))

    return render_template('signup.html')

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email').strip().lower()
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash(f"Welcome back, {user.username}!", "primary")
            return redirect(url_for('index'))
        else:
            flash("Invalid credentials. Please try again.", "danger")
            return redirect(url_for('login'))

    return render_template('login.html')

# Logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for('index'))

# Doctor registration (only accessible to logged-in doctors per your original logic)
@app.route('/doctors', methods=['GET', 'POST'])
@login_required
def doctors():
    # Restrict to users who are of type 'Doctor'
    if current_user.usertype != 'Doctor':
        flash("Access denied: Doctors only.", "danger")
        return redirect(url_for('index'))

    if request.method == 'POST':
        email = request.form.get('email').strip().lower()
        doctorname = request.form.get('doctorname').strip()
        dept = request.form.get('dept').strip()

        if not email or not doctorname or not dept:
            flash("Fill all fields.", "warning")
            return redirect(url_for('doctors'))

        existing_doctor = Doctor.query.filter_by(email=email, dept=dept).first()
        if existing_doctor:
            flash("You are already registered for this department.", "warning")
            return redirect(url_for('doctors'))

        new_doc = Doctor(email=email, doctorname=doctorname, dept=dept)
        db.session.add(new_doc)
        db.session.commit()
        flash("Doctor registration successful!", "success")
        return redirect(url_for('index'))

    return render_template('doctor.html')

# Patient booking
@app.route('/patients', methods=['GET', 'POST'])
@login_required
def patients():
    # Only patients (or all logged-in users) should be allowed to book — adjust as needed
    doct = Doctor.query.all()  # used to populate dept select in patient.html

    if request.method == 'POST':
        email = request.form.get('email').strip().lower()
        name = request.form.get('name').strip()
        gender = request.form.get('gender')
        slot = request.form.get('slot')
        time_val = request.form.get('time')
        date_val = request.form.get('date')
        disease = request.form.get('disease').strip()
        dept = request.form.get('dept')
        number = request.form.get('number').strip()

        # basic validation
        if not (email and name and gender and slot and time_val and date_val and disease and dept and number):
            flash("Please fill all fields.", "warning")
            return redirect(url_for('patients'))

        new_patient = Patient(
            email=email, name=name, gender=gender, slot=slot,
            disease=disease, date=date_val, time=time_val, dept=dept, number=number
        )
        db.session.add(new_patient)
        db.session.commit()

        # create trigger/audit record
        trigger = Triggers(
            pid=new_patient.pid,
            email=new_patient.email,
            name=new_patient.name,
            action="INSERT",
            timestamp=str(datetime.now())
        )
        db.session.add(trigger)
        db.session.commit()

        flash("Booking successful!", "success")
        return redirect(url_for('bookings'))

    return render_template('patient.html', doct=doct)

# View bookings
@app.route('/bookings')
@login_required
def bookings():
    query = Patient.query.all()
    return render_template('booking.html', query=query)

# Edit booking
@app.route('/edit/<int:pid>', methods=['GET', 'POST'])
@login_required
def edit(pid):
    posts = Patient.query.get_or_404(pid)

    # Optional: restrict edit permission (e.g., only the user who created booking or a doctor)
    if request.method == 'POST':
        posts.email = request.form.get('email').strip().lower()
        posts.name = request.form.get('name').strip()
        posts.gender = request.form.get('gender')
        posts.slot = request.form.get('slot')
        posts.time = request.form.get('time')
        posts.date = request.form.get('date')
        posts.disease = request.form.get('disease').strip()
        posts.dept = request.form.get('dept')
        posts.number = request.form.get('number').strip()

        db.session.commit()
        flash("Booking updated!", "success")
        return redirect(url_for('bookings'))

    return render_template('edit.html', posts=posts)

# Delete booking
@app.route('/delete/<int:pid>')
@login_required
def delete(pid):
    post = Patient.query.get_or_404(pid)

    # Create trigger record for deletion
    trigger = Triggers(
        pid=post.pid,
        email=post.email,
        name=post.name,
        action="DELETE",
        timestamp=str(datetime.now())
    )
    db.session.add(trigger)

    db.session.delete(post)
    db.session.commit()

    flash("Record deleted!", "danger")
    return redirect(url_for('bookings'))

# Triggers/audit view
@app.route('/trigers')
@login_required
def trigers():
    posts = Triggers.query.order_by(Triggers.tid.desc()).all()
    return render_template('trigers.html', posts=posts)

# Details (patients details) - visible to doctors
@app.route('/details')
@login_required
def details():
    if current_user.usertype != 'Doctor':
        flash("Access denied: Doctors only.", "danger")
        return redirect(url_for('index'))

    patients = Patient.query.all()
    return render_template('booking.html', query=patients)  # you may create a dedicated details.html if desired

# Search (search by department)
@app.route('/search', methods=['POST'])
def search():
    dept = request.form.get('search')
    if not dept:
        flash("Enter a department to search.", "warning")
        return redirect(url_for('index'))

    results = Patient.query.filter(Patient.dept.ilike(f"%{dept}%")).all()
    return render_template('booking.html', query=results)

@app.route('/attend/<int:pid>')
@login_required
def attend(pid):
    # Only doctors should mark patients as attended
    if current_user.usertype != 'Doctor':
        flash("Only doctors can mark attended.", "danger")
        return redirect(url_for('bookings'))

    post = Patient.query.get_or_404(pid)

    completed = CompletedBooking(
        pid=post.pid,
        doctor=current_user.username,
        patient_name=post.name,
        disease=post.disease,
        dept=post.dept,
        date=post.date,
        time=post.time,
        feedback=None
    )

    db.session.add(completed)

    # add trigger record (optional)
    trigger = Triggers(
        pid=post.pid,
        email=post.email,
        name=post.name,
        action="ATTENDED",
        timestamp=str(datetime.now())
    )
    db.session.add(trigger)

    db.session.delete(post)
    db.session.commit()

    flash("Patient marked as attended and moved to completed.", "success")
    return redirect(url_for('bookings'))

@app.route('/completed')
@login_required
def completed():
    # Patients see only their completed records, doctors see all or their own
    if current_user.usertype == 'Patient':
        # If you link CompletedBooking to patient email or username, filter accordingly.
        # Here we filter by patient_name matching user's username (or change to email)
        records = CompletedBooking.query.filter_by(patient_name=current_user.username).all()
    elif current_user.usertype == 'Doctor':
        # Show all completed bookings for this doctor
        records = CompletedBooking.query.filter_by(doctor=current_user.username).all()
    else:
        records = CompletedBooking.query.all()

    return render_template('completed.html', records=records)

@app.route('/feedback/<int:cid>', methods=['GET', 'POST'])
@login_required
def feedback(cid):
    rec = CompletedBooking.query.get_or_404(cid)

    # Ensure only the patient who had the appointment can give feedback (optional)
    if request.method == 'POST':
        fb = request.form.get('feedback', '').strip()
        rec.feedback = fb
        db.session.commit()
        flash("Feedback submitted. Thank you!", "success")
        return redirect(url_for('completed'))

    return render_template('feedback.html', record=rec)

@app.route('/doctor_profile')
@login_required
def doctor_profile():
    if current_user.usertype != 'Doctor':
        flash("Unauthorized access.", "danger")
        return redirect(url_for('index'))

    # Fetch completed bookings for this doctor (which include feedback)
    feedbacks = CompletedBooking.query.filter_by(doctor=current_user.username).all()
    return render_template('doctor_profile.html', feedbacks=feedbacks)

'''@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for('index'))'''




# Fallback / error pages can be added as needed

# --- START APP ---
if __name__ == '__main__':
    with app.app_context():
      db.create_all()
    app.run(debug=True)
