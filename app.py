from flask import Flask, render_template, request, session, redirect, url_for, abort, flash, send_from_directory
from flask_socketio import SocketIO, join_room, leave_room, send
import random
from string import ascii_uppercase
from datetime import datetime
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import os
from werkzeug.utils import secure_filename
from functools import wraps
import typing as t

app = Flask(__name__)
app.config["SECRET_KEY"] = "your_secret_key_here"
app.config['UPLOAD_FOLDER'] = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

socketio = SocketIO(app, ssl_context=('cert.pem', 'key.pem'))

rooms = {}

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def login_is_required(func: t.Callable[..., t.Any]) -> t.Callable[..., t.Any]:
    @wraps(func)
    def check_authentication(*args: t.Any, **kwargs: t.Any) -> t.Any:
        if "user_id" not in session:
            abort(401)
        return func(*args, **kwargs)
    return check_authentication

def generate_unique_code(length: int) -> str:
    while True:
        code = "".join(random.choice(ascii_uppercase) for _ in range(length))
        if code not in rooms:
            return code

@app.route("/", methods=["POST", "GET"])
def home():
    if request.method == "POST":
        name = request.form.get("name")
        code = request.form.get("code")
        join = request.form.get("join")
        create = request.form.get("create")

        if not name:
            return render_template("home.html", error="Please enter a name", code=code, name=name)
        if join and not code:
            return render_template("home.html", error="Please enter a room code", code=code, name=name)
        
        room = code
        if create:
            room = generate_unique_code(4)
            rooms[room] = {"members": 0, "messages": []}
        elif code not in rooms:
            return render_template("home.html", error="Room does not exist", code=code, name=name)
        
        session['room'] = room
        session['name'] = name
        return redirect(url_for("room"))
    
    return render_template("home.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        conn.close()
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['name'] = user['username']
            return redirect(url_for('home'))
        else:
            flash('Invalid email or password.', 'danger')
            return redirect(url_for('login'))
    
    return render_template('login-registration.html')

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        repeat_password = request.form.get("repeat_password")

        if password != repeat_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password)
        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                         (username, email, hashed_password))
            conn.commit()
            flash('Registration successful! You can now log in.', 'success')
        except sqlite3.IntegrityError:
            flash('Email or username already exists.', 'danger')
        finally:
            conn.close()
        return redirect(url_for('login'))

    return render_template('login-registration.html')

@app.route("/logout")
def logout():
    session.clear()
    return redirect('/')

@app.route("/room")
def room():
    room = session.get("room")
    if room is None or session.get("name") is None or room not in rooms:
        return redirect(url_for("home"))
    return render_template("room.html", code=room, messages=rooms[room]["messages"])

@app.route("/profile")
@login_is_required
def profile():
    user_id = session.get("user_id")
    if not user_id:
        flash('User not found.', 'danger')
        return redirect(url_for('home'))
    
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    
    if user:
        return render_template("profile.html", user=user)
    else:
        flash('User not found.', 'danger')
        return redirect(url_for('home'))

@app.route("/update_profile", methods=["POST"])
@login_is_required
def update_profile():
    user_id = session.get("user_id")
    username = request.form.get("username")
    email = request.form.get("email")
    password = request.form.get("password")
    repeat_password = request.form.get("repeat_password")

    if password and password != repeat_password:
        flash("Passwords do not match.", 'danger')
        return redirect(url_for('profile'))
    
    hashed_password = generate_password_hash(password) if password else None
    
    conn = get_db_connection()
    try:
        if hashed_password:
            conn.execute('UPDATE users SET username = ?, email = ?, password = ? WHERE id = ?',
                         (username, email, hashed_password, user_id))
        else:
            conn.execute('UPDATE users SET username = ?, email = ? WHERE id = ?',
                         (username, email, user_id))
        conn.commit()
        flash('Profile updated successfully!', 'success')
    except sqlite3.Error as e:
        flash(f"An error occurred: {e}", 'danger')
    finally:
        conn.close()

    return redirect(url_for('profile'))

@app.route("/upload_photo", methods=["POST"])
@login_is_required
def upload_photo():
    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    if 'photo' not in request.files:
        flash('No file part', 'danger')
        return redirect(url_for('profile'))

    file = request.files['photo']
    if file.filename == '':
        flash('No selected file', 'danger')
        return redirect(url_for('profile'))

    if file and allowed_file(file.filename):
        try:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            photo_url = url_for('uploaded_file', filename=filename)

            conn = get_db_connection()
            conn.execute('UPDATE users SET profile_photo = ? WHERE id = ?', (photo_url, session.get("user_id")))
            conn.commit()
            conn.close()

            flash('Profile photo updated successfully!', 'success')
        except Exception as e:
            flash(f'Error occurred: {e}', 'danger')
    else:
        flash('Invalid file type', 'danger')
    
    return redirect(url_for('profile'))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@socketio.on("message")
def message(data):
    room = session.get("room")
    if room not in rooms:
        return
    timestamp = datetime.now().isoformat()
    content = {
        "name": session.get("name"),
        "message": data.get("message", "No message"),
        "timestamp": timestamp
    }
    send(content, to=room)
    rooms[room]["messages"].append(content)
    print(f"{session.get('name')} said: {data.get('message', 'No message')}")

@socketio.on("connect")
def connect():
    room = session.get('room')
    name = session.get("name")

    if not room or not name:
        return

    if room not in rooms:
        leave_room(room)
        return

    join_room(room)
    send({"name": name, "message": "has entered the room"}, to=room)
    rooms[room]["members"] += 1
    print(f"{name} joined room {room}")

@socketio.on("disconnect")
def disconnect():
    room = session.get('room')
    name = session.get("name")
    leave_room(room)

    if room in rooms:
        rooms[room]["members"] -= 1
        if rooms[room]["members"] <= 0:
            del rooms[room]
    send({"name": name, "message": "has left the room"}, to=room)
    print(f"{name} has left the room {room}")

if __name__ == "__main__":
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    
    cert_path = ''
    key_path = ''
    socketio.run(app, host='127.0.0.1', port=5000, 
                 ssl_context=(cert_path, key_path))
