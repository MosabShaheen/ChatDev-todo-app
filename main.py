'''
This is the main file of the Flask to-do app.
'''
from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from decouple import config
app = Flask(__name__)
app.secret_key = config('SECRET_KEY', default='your_default_secret_key')
app.config['SQLALCHEMY_DATABASE_URI'] = config('DATABASE_URI', default='sqlite:///default.db')
db = SQLAlchemy(app)
# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    tasks = db.relationship('Task', backref='user', lazy=True)
# Task model
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    due_date = db.Column(db.DateTime, nullable=True)
    priority = db.Column(db.Integer, nullable=True)
    category = db.Column(db.String(50), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
# Home route
@app.route('/')
def home():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        tasks = user.tasks
        return render_template('home.html', tasks=tasks)
    return redirect(url_for('login'))
# Register route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')
# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['user_id'] = user.id
            return redirect(url_for('home'))
        else:
            return render_template('login.html', error='Invalid username or password')
    return render_template('login.html')
# Logout route
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))
# Add task route
@app.route('/add_task', methods=['POST'])
def add_task():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        title = request.form['title']
        completed = False
        due_date = datetime.strptime(request.form['due_date'], '%Y-%m-%d')
        priority = int(request.form['priority'])
        category = request.form['category']
        task = Task(title=title, completed=completed, due_date=due_date, priority=priority, category=category, user=user)
        db.session.add(task)
        db.session.commit()
    return redirect(url_for('home'))
# Update task route
@app.route('/update_task/<int:task_id>', methods=['POST'])
def update_task(task_id):
    if 'user_id' in session:
        task = Task.query.get(task_id)
        task.title = request.form['title']
        task.completed = True if request.form.get('completed') else False
        task.due_date = datetime.strptime(request.form['due_date'], '%Y-%m-%d')
        task.priority = int(request.form['priority'])
        task.category = request.form['category']
        db.session.commit()
    return redirect(url_for('home'))
# Delete task route
@app.route('/delete_task/<int:task_id>')
def delete_task(task_id):
    if 'user_id' in session:
        task = Task.query.get(task_id)
        db.session.delete(task)
        db.session.commit()
    return redirect(url_for('home'))
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)