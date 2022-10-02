#from flask import Flask, request, session, redirect, url_for, render_template
from flask import Flask, render_template, request, redirect, url_for, flash, \
    Response, session
from flask_bootstrap import Bootstrap
from filters import datetimeformat, file_type
from resources import get_bucket, get_buckets_list
from flaskext.mysql import MySQL
import pymysql 
import re 

#import netifaces as ni
import smtplib, random
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def protocoloCorreo(dia,hora,hola,user):

    anfitrion = "smtp.gmail.com"
    puerto = 587
    direccionDe = "airlinetesistest@gmail.com"
    contrasenaDe = "ssupcmsofqlwpiky"
    direccionPara = user # PAra quien

    servidor = smtplib.SMTP(anfitrion,puerto)
    servidor.starttls()
    servidor.login(direccionDe,contrasenaDe)
    print(servidor.ehlo())


    asunto = "INFORMACION SOBRE SU RESERVA"
    correo = MIMEMultipart() # SE CREA EL OBJETO
    correo['From'] = direccionDe
    correo['To'] = direccionPara
    correo['Subject'] = asunto



    message = "Estimado usuario, se ha reservado con exito el salon "+str(hola)+" el dia "+dia+" desde las "+hora
    mensaje = MIMEText(message)
    correo.attach(mensaje)


    servidor.sendmail(direccionDe,direccionPara,correo.as_string())





def correoauditorio(correo):

    anfitrion = "smtp.gmail.com"
    puerto = 587
    direccionDe = "airlinetesistest@gmail.com"
    contrasenaDe = "ssupcmsofqlwpiky"
    direccionPara = correo # PAra quien

    servidor = smtplib.SMTP(anfitrion,puerto)
    servidor.starttls()
    servidor.login(direccionDe,contrasenaDe)
    print(servidor.ehlo())


    asunto = "SU SOLICITUD HA SIDO ENVIADA	"
    correo = MIMEMultipart() # SE CREA EL OBJETO
    correo['From'] = direccionDe
    correo['To'] = direccionPara
    correo['Subject'] = asunto



    message = """Estimado usuario, se ha realizado con exito su solicutud para la reserva del auditorio. Se contactara con usted a este correo para confirmar o realizar ajustes a su reserva. Gracias por su comprension"""
    mensaje = MIMEText(message)
    correo.attach(mensaje)


    servidor.sendmail(direccionDe,direccionPara,correo.as_string())


def correoAdmin(nombre,correoo,fecha,hora,asistentes,razon):

    anfitrion = "smtp.gmail.com"
    puerto = 587
    direccionDe = "airlinetesistest@gmail.com"
    contrasenaDe = "ssupcmsofqlwpiky"
    direccionPara = "airlinetesistest@gmail.com" # PAra quien

    servidor = smtplib.SMTP(anfitrion,puerto)
    servidor.starttls()
    servidor.login(direccionDe,contrasenaDe)
    print(servidor.ehlo())


    asunto = "Solicitud de reserva : "+nombre
    correo = MIMEMultipart() # SE CREA EL OBJETO
    correo['From'] = direccionDe
    correo['To'] = direccionPara
    correo['Subject'] = asunto



    message = """Se ha realizado una nueva solicitud de reserva de auditorio, el profesor """+nombre+""" identificado con correo: """+correoo+""" desea reservar el auditorio el dia: """+str(fecha)+""" en el siguiente rango horario: """+hora+""" para una cantidad de: """+asistentes+""" Asistentes. La razon por la cual lo desea reservar es la siguiente: '"""+codigo+"'."
    #message = "Se ha realizado una nueva solicitud de reserva de auditorio, el profesor "+nombre+ "identificado con el correo: "+correoo
    mensaje = MIMEText(message)
    correo.attach(mensaje)


    servidor.sendmail(direccionDe,direccionPara,correo.as_string())


 
app = Flask(__name__)
Bootstrap(app)
app.secret_key = 'secret'
app.jinja_env.filters['datetimeformat'] = datetimeformat
app.jinja_env.filters['file_type'] = file_type
 
# Change this to your secret key (can be anything, it's for extra protection)
app.secret_key = 'cairocoders-ednalan'
 
mysql = MySQL()
   
# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'admin'
app.config['MYSQL_DATABASE_PASSWORD'] = 'UMG2022test!'
app.config['MYSQL_DATABASE_DB'] = 'salones'
app.config['MYSQL_DATABASE_HOST'] = 'aerocharter-test.cn4tyodhyfme.us-east-1.rds.amazonaws.com'
mysql.init_app(app)
a = None
b = None
dia = None
hora = None
prestamo = None
 
# http://localhost:5000/pythonlogin/ - this will be the login page
@app.route('/login/', methods=['GET', 'POST'])
def login():
 # connect
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
  
    # Output message if something goes wrong...
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        # Check if account exists using MySQL
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
            return redirect(url_for('inicio'))
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Por favor revise sus credenciales.'
    
    return render_template('index.html', msg=msg)
 
# http://localhost:5000/register - this will be the registration page
@app.route('/register', methods=['GET', 'POST'])
def register():
 # connect
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
  
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        fullname = request.form['fullname']
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
   
  #Check if account exists using MySQL
        cursor.execute('SELECT * FROM accounts WHERE username = %s', (username))
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
            cursor.execute('INSERT INTO accounts VALUES (NULL, %s, %s, %s, %s)', (fullname, username, password, email)) 
            conn.commit()
   
            msg = 'You have successfully registered!'
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('register.html', msg=msg)
  
# http://localhost:5000/home - this will be the home page, only accessible for loggedin users
@app.route('/inicio')
def inicio():
    # Check if user is loggedin
    if 'loggedin' in session:
   
        # User is loggedin show them the home page
        return render_template('inicio.html', username=session['username'])
    # User is not loggedin redirect to login page
    #return render_template('inicio.html')
  
# http://localhost:5000/logout - this will be the logout page
@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   # Redirect to login page
   return redirect(url_for('login'))
 
# http://localhost:5000/profile - this will be the profile page, only accessible for loggedin users
@app.route('/profile')
def profile(): 
 # Check if account exists using MySQL
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
  
    # Check if user is loggedin
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        cursor.execute('SELECT * FROM accounts WHERE id = %s', [session['id']])
        account = cursor.fetchone()
        # Show the profile page with account info
        return render_template('profile.html', account=account)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))
  
if __name__ == '__main__':
    app.run(debug=True)