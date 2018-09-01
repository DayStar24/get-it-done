from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://get-it-done:abc123@localhost:3306/get-it-done'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'ghia4e8t948tbh4t7b4b58745t'


class Task(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    completed = db.Column(db.Boolean)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, name, owner):
        self.name = name
        self.completed = False
        self.owner = owner

    def __str__(self):
        return str(self.name) + ' ' + str(self.completed) + ' ' + str(self.owner_id)


class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    tasks = db.relationship('Task', backref='owner')

    def __init__(self, email, password):
        self.email = email
        self.password = password

@app.route('/', methods=['POST', 'GET'])
def index():

    current_user = User.query.filter_by(email=session['email']).first()

    if request.method == 'POST':
        task_name = request.form['task']
        new_task = Task(task_name, current_user)
        db.session.add(new_task)
        db.session.commit()

    tasks = Task.query.filter_by(completed=False, owner=current_user).all()
    completed_tasks = Task.query.filter_by(completed=True, owner=current_user).all()
    return render_template('todos.html',title="Get It Done!", 
        tasks=tasks, completed_tasks=completed_tasks)


@app.route('/delete-task', methods=['POST'])
def delete_task():

    task_id = int(request.form['task-id'])
    task = Task.query.get(task_id)
    task.completed = True
    db.session.add(task)
    db.session.commit()

    return redirect('/')


@app.route('/register', methods=['POST','GET'])
def register():

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']
        
        #TODO: validate the input

        exsisting_user = User.query.filter_by(email=email).first()

        if not exsisting_user:
            new_user = User(email, password)
            db.session.add(new_user)
            db.session.commit()
            session['email'] = email
            return redirect('/')
        else:
            #TODO: Make a better error message
            return '<h1>User already exists</h1>'

    return render_template('register.html')


@app.route('/login', methods=['POST','GET'])
def login():

    if request.method == 'POST':
        email = request.form['email']
        e = email
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        if user and user.password == password:
            session['email'] = email
            return redirect('/')
        else:
            flash('Password incorrect or user does not exist', 'error')

    return render_template('login.html')


@app.route('/logout')
def logout():

    del session['email']
    
    return redirect('/')


@app.before_request
def require_login():
    
    allowed_routes = ['login','register']
    
    if request.endpoint not in allowed_routes and 'email' not in session:
        return redirect('/login')


if __name__ == '__main__':
    app.run()