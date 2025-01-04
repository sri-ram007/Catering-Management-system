from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from waitress import serve

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Necessary for session management

# Initialize the database
def init_db():
    with sqlite3.connect("database.db") as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        )
        """)
        conn.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            morning_food TEXT,
            morning_quantity INTEGER,
            lunch TEXT,
            lunch_quantity INTEGER
        )
        """)
        conn.commit()

# Initialize the database
init_db()

# Route Handlers
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about_page():
    return render_template('about.html')

@app.route('/price')
def price():
    return render_template('price.html')

@app.route('/login', methods=['GET'])
def login():
    return render_template('login.html')

@app.route('/submit_login', methods=['POST'])
def submit_login():
    username = request.form.get('username')
    password = request.form.get('password')
    
    with sqlite3.connect("database.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        user = cursor.fetchone()
    
    if user is None:
        return jsonify(message="Invalid username or password."), 401
    
    if check_password_hash(user[2], password):
        session['username'] = username
        return jsonify(message="Login successful", redirect_url=url_for('user_dashboard')), 200
    else:
        return jsonify(message="Invalid username or password."), 401


@app.route('/user_dashboard')
def user_dashboard():
    if 'username' in session:
        username = session['username']
        return render_template('user.html', username=username)  # Pass the username to the template
    else:
        return redirect(url_for('login'))  # Redirect to login if not logged in

@app.route('/logout')
def logout():
    session.pop('username', None)  # Remove the username from the session to log the user out
    return redirect(url_for('login'))  # Redirect to the login page


@app.route('/form_page')
def form_page():
    return render_template('form.html')

@app.route('/submit_order', methods=['POST'])
def submit_order():
    morning_food = request.form.get('morning_food')
    morning_quantity = request.form.get('morning_quantity')
    lunch = request.form.get('lunch')
    lunch_quantity = request.form.get('lunch_quantity')
    
    with sqlite3.connect("database.db") as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO orders (morning_food, morning_quantity, lunch, lunch_quantity) VALUES (?, ?, ?, ?)", 
                       (morning_food, morning_quantity, lunch, lunch_quantity))
        conn.commit()
    
    return jsonify(message="Order submitted successfully!")

@app.route('/lunch_page')
def lunch_page():
    return render_template('lunch.html')

@app.route('/submit_foods', methods=['POST'])
def submit_foods():
    morning_food = request.form.get('morning_food')
    morning_quantity = request.form.get('morning_quantity')
    lunch = request.form.get('lunch')
    lunch_quantity = request.form.get('lunch_quantity')
    
    with sqlite3.connect("database.db") as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO orders (morning_food, morning_quantity, lunch, lunch_quantity) VALUES (?, ?, ?, ?)", 
                       (morning_food, morning_quantity, lunch, lunch_quantity))
        conn.commit()
    
    return jsonify(message="Order submitted successfully!")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        with sqlite3.connect("database.db") as conn:
            cursor = conn.cursor()

            # Check for existing username
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            if cursor.fetchone():
                return jsonify({'message': 'Username already taken.'}), 400

            # Hash the password and store the new user
            hashed_password = generate_password_hash(password)
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
            conn.commit()

        return jsonify({'message': 'Registered successfully!'}), 200

    return render_template('register.html')


if __name__ == '__main__':
    serve(app, host='127.0.0.1', port=5000, expose_tracebacks=True)
