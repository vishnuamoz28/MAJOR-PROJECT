from flask import Flask, url_for, request, render_template, redirect, session, send_file
from flask_mysqldb import MySQL
import prem
from prem import predict_price


app = Flask(__name__, template_folder='templates')
app.secret_key = "amalja"  # Set a secret key for session management

# MySQL configurations
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'W7301@jqir#'  # Replace 'your_password' with your actual password
app.config['MYSQL_DB'] = 'user_log'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'  # Use dictionary cursor

# Initialize MySQL
mysql = MySQL(app)

# Route to render the login form
@app.route('/')
def login_form():
    error = request.args.get('error')  # Get error message from query parameter
    return render_template('login1.html', error=error)

# Route to render the registration page
@app.route('/register')
def register():
    return render_template('register.html')

# Route to handle user registration
@app.route('/register', methods=['POST'])
def register_user():
    # Get form data
    name = request.form['name']
    age = request.form['age']
    phn_no = request.form['phn_no']
    uname = request.form['uname']
    password = request.form['password']
    email = request.form['email']
    lic_no = request.form['lic_no']
    dob = request.form['dob']
    user_type=request.form['user_type']

    # Create cursor
    cur = mysql.connection.cursor()

    # Execute query to insert user data into database
    cur.execute("INSERT INTO user_info(name, age, phn_no, uname, password, email, lic_no, dob,user_type) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (name, age, phn_no, uname, password, email, lic_no, dob,user_type))

    # Commit to DB
    mysql.connection.commit()

    # Close connection
    cur.close()

    # Redirect to login page with success message
    return redirect(url_for('login_form', error='Registration successful! You can now log in.'))

# Route to handle login form submission
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    # Create cursor
    cur = mysql.connection.cursor()

    # Execute SQL query to fetch user by username
    result = cur.execute("SELECT * FROM user_info WHERE uname = %s", [username])

    if result > 0:
        # Get stored user data
        data = cur.fetchone()

        # Compare passwords
        if data['password'] == password:
            # Store user information in session
            session['username'] = username
            return redirect('https://demos.creative-tim.com/argon-dashboard/pages/dashboard.html')
        else:
            # If login fails, return to the login page with an error message
            error = 'Invalid username or password'
            return render_template('login1.html', error=error)

    else:
        # If login fails, return to the login page with an error message
        error = 'Invalid username or password'
        return render_template('login1.html', error=error)

@app.route('/dashboard')
def dashboard():
    # Check if user is logged in
    if 'username' in session:
        username = session['username']
        return send_file('index.html')
    else:
        # If user is not logged in, redirect to the login page with an error message
        return redirect(url_for('login_form', error='Unauthorized access'))

# Route to handle prediction
@app.route('/predict', methods=['POST'])
def predict():
    # Get user input from the form
    engine_size = int(request.form['engine_size'])
    horsepower = int(request.form['horsepower'])
    curb_weight = int(request.form['curb_weight'])

    # Call the prediction function with the user input
    prediction = prem.predict_handler(engine_size, horsepower, curb_weight, driving_history=None, coverage=None)

    # Render the dashboard template with the prediction result
    return render_template('dashboard.html', prediction=prediction)


@app.route('/premium', methods=['GET', 'POST'])
def premium():
    if request.method == 'POST':
        # Handle form submission
        engine_size = int(request.form['engine_size'])
        horsepower = int(request.form['horsepower'])
        curb_weight = int(request.form['curb_weight'])

        # Perform prediction and return the result
        # Replace this with your actual prediction logic
        prediction = prem.predict_price(engine_size, horsepower, curb_weight)

        return render_template('premium.html', prediction=prediction)

    # If it's a GET request or if the form hasn't been submitted yet
    return render_template('premium.html')

# Route to handle logout
@app.route('/logout')
def logout():
    session.pop('username', None)  # Clear user session
    return redirect(url_for('login_form'))

if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=5000)
