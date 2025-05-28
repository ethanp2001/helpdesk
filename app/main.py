#Import Required Libraries
from flask import Flask, render_template, request, redirect, url_for, flash, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from dotenv import load_dotenv
import os

#Initialise Database
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
db = SQLAlchemy(app)

#Create Ticket Database Table
class Ticket(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        title = db.Column(db.String(100), nullable=False)
        description = db.Column(db.String(200), nullable=False)
        status = db.Column(db.String(20), nullable=False, default='Open')

#Create User Database Table
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)
    firstname = db.Column(db.String(150), nullable=False)
    lastname = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='user') # Set to 'user' or 'admin'

#Create User Registration Form in Flask-WTF
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=4,max=20)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8,max=30)])
    firstname = StringField('First Name', validators=[InputRequired(), Length(min=1,max=30)])
    lastname = StringField('Last Name', validators=[InputRequired(), Length(min=1,max=30)])                       
    submit = SubmitField('Register')

#Create User Login Form in Flask-WTF
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(),])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8,max=30)])
    submit = SubmitField('Login')

#Initialise login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

#Decorator function to restrict access based on role assignment
def role_required(role):
    def wrapper(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role != role:
                abort(403) #Forbidden error if not admin
            return f(*args, **kwargs)
        return decorated_function
    return wrapper

#Set up user loader function
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#Ticket page
@app.route('/createticket', methods=['GET', 'POST'])
def create_ticket():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['title']
        new_ticket = Ticket(title=title, description=description)
        db.session.add(new_ticket)
        db.session.commit()
        return redirect('/home')
    return render_template('create_ticket.html')

#Home page
@app.route('/home')
@login_required
def view_tickets():
    tickets = Ticket.query.all()
    return render_template('main_page.html', tickets=tickets)

#User Registration Page
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256')
        new_user = User(
            username=form.username.data, 
            password=hashed_password, 
            firstname=form.firstname.data, 
            lastname=form.lastname.data,
            role='user'
        )
        db.session.add(new_user)
        db.session.commit()
        flash('Registration has been successful!', 'success')
        return redirect('/login')
    return render_template('register.html', form=form)

#User login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('Username and password correct, login successful!', 'success')
            return redirect('/home')
        else:
            flash('Details are incorrect, please check your username and password and try again', 'danger')
    return render_template('login.html', form=form)

#Admin Dashboard
@app.route('/admin')
@login_required
@role_required('admin')
def admin():
    users = User.query.all()
    tickets = Ticket.query.all()
    return render_template('admin.html', users=users, tickets=tickets)

#Promote User to admin
@app.route('/promote.<int:user_id>', methods=['POST'])
@login_required
@role_required('admin')
def promote_user(user_id):
    user = User.query.get_or_404(user_id)
    user.role = 'admin'
    db.session.commit()
    flash(f'User {user.username} has been promoted to admin.', 'success')
    return redirect('/admin')

#Close tickets
@app.route('/closeticket/<int:ticket_id>', methods=['POST'])
@login_required
@role_required('admin')
def close_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    ticket.status = 'Closed'
    db.session.commit()
    flash(f'Ticket "{ticket.title}" has been closed.', 'success')
    return redirect('/admin')

#Program start
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        app.run(debug=True)