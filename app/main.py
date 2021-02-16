# main.py program
# login page route
# logout page route
# home page route
# profile page route
# register page


#importing all the libraries
from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
from flask import send_file
import MySQLdb.cursors
import re
from werkzeug.utils import secure_filename
import os
from flask import send_from_directory
import glob
app = Flask(__name__)

# Change this to your secret key (can be anything, it's for extra protection)
app.secret_key = 'sumankalapatapu'
UPLOAD_FOLDER = "/home/ubuntu/flaskapp/userprofiles/"
app.config["UPLOAD_FOLDER"] = "/home/ubuntu/flaskapp/userprofiles/"
app.config["ALLOWED_IMAGE_EXTENSIONS"] = ["JPEG", "JPG", "PNG", "GIF"]
app.config["MAX_UPLOAD_FILESIZE"] = 0.5 * 1024 * 1024

# Enter your database connection details below
app.config['MYSQL_HOST'] = 'db'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_PORT'] = '3306'
app.config['MYSQL_DB'] = 'pythonlogin'


# Intialize MySQL
mysql = MySQL(app)


# http://localhost:5000/login/ - this will be the login page, we need to use both GET and POST requests
#@app.route('/login/', methods=['GET', 'POST'])

@app.route('/login/', methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password))
        # Fetch one record and return result
        account = cursor.fetchone()
        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            # Redirect to home page
            #return 'Logged in successfully!'
            return redirect(url_for('home'))
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
    # Show the login form with message (if any)
    return render_template('index.html', msg=msg)

# http://localhost:5000/login/logout - this will be the logout page
@app.route('/login/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   # Redirect to login page
   return redirect(url_for('login'))

# http://localhost:5000/login/register - this will be the registration page.
@app.route('/login/register', methods=['GET', 'POST'])
def register():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if (request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form
       and 'firstname' in request.form and 'lastname' in request.form):
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        email = request.form['email']

         # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        #cursor.execute('SELECT * FROM accounts WHERE username = %s', (username))
        cursor.execute('SELECT * FROM accounts WHERE username = %s', [username])
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO accounts VALUES (NULL, %s, %s, %s, %s, %s)', (username, password, firstname, lastname, email))
            mysql.connection.commit()
            msg = 'You have successfully registered!'


    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('register.html', msg=msg)

# http://localhost:5000/pythinlogin/home - this will be the home page, only accessible for loggedin users
@app.route('/login/home', methods=['GET', 'POST'])
def home():
    # Check if user is loggedin
    previousvalue=0
    filevalue=[0,'None']
    if 'loggedin' in session:

        msg=''
        if request.method == 'POST':
        # check if the post request has the file part
            #if 'file' not in request.files:
            #    msg = 'No file part'
            #    return redirect(request.url)
            f = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
            if f.filename == '':
                msg1 = 'No selected file'
                return redirect(request.url)
                #render_template('home.html', username=session['username'],count=prevcount,file=d1[1],msg1=msg1)
            #if f and allowed_file(f.filename):
            filename = secure_filename(f.filename)
            UPLOAD_FOLDER = '/home/ubuntu/flaskapp/userprofiles/'+session['username']+'/'
            access_rights=0o777
            isnotdir = os.path.isdir(UPLOAD_FOLDER)
            if isnotdir == False:
                os.mkdir(UPLOAD_FOLDER,access_rights)
                #CreateNewDir()
            #global UPLOAD_FOLDER
            f.save(os.path.join(UPLOAD_FOLDER, filename))
            path_file='/home/ubuntu/flaskapp/userprofiles/' + session['username'] +'/' + secure_filename(f.filename)
           # path_file='/home/ubuntu/flaskapp/' + secure_filename(f.filename)
            file = open(path_file, "rt")
            data = file.read()
            words = data.split()
            prevcount=len(words)
            print('Number of words in text file :', previousvalue)
            filevalue = path_file.split(session['username']+'/')

            #return redirect(url_for('uploaded_file',filename=filename))
            msg = 'File uploaded Successfully!'
            return render_template('home.html', username=session['username'],count=prevcount,file=filevalue[1])
        
        #To print previous logged in details and files,count values
        list_files = glob.glob('/home/ubuntu/flaskapp/userprofiles/'+session['username']+'/*') # * means all if need specific format then *.csv
        if list_files:
            latest = max(list_files, key=os.path.getctime)
            file = open(latest, "rt")
            data = file.read()
            words = data.split()
            previousvalue=len(words)
            filevalue = latest.split(session['username']+'/')


        return render_template('home.html', username=session['username'],count=previousvalue,file=filevalue[1])
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))


# http://localhost:5000/login/profile - this will be the profile page, only accessible for loggedin users
@app.route('/login/profile', methods=['GET', 'POST'])
def profile():
    #render_template('profile.html', account=account)
    # Check if user is loggedin
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE id = %s', [session['id']])
        account = cursor.fetchone()
        # Show the profile page with account info
    return render_template('profile.html', account=account)


@app.route('/login/download')
def download_file():
    if 'loggedin' in session:
        listfiles = glob.glob('/home/ubuntu/flaskapp/userprofiles/'+session['username']+'/*') # * means all if need specific format then *.csv
        if listfiles:
            latest1 = max(listfiles, key=os.path.getctime)
            print(latest1)
            return send_file(latest1, as_attachment=True,cache_timeout=-1)
        else:
            msg='No file to Download'
            return render_template('home.html', username=session['username'],msg=msg)
    return redirect(url_for('login'))


if __name__ == '__main__':
  app.run(host='0.0.0.0',debug=True)
