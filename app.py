from flask import Flask, render_template, request, redirect
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from collections import deque
from dotenv import load_dotenv
from source.userManager import UserManager
from source.dbManager import DBManager
from source.models import RegisterForm, LoginForm

import markdown, os

load_dotenv()
app = Flask(__name__)
db_manager = DBManager()
user_manager = UserManager()
login_manager = LoginManager()
login_manager.init_app(app)
app.secret_key = os.getenv('SECRET_KEY')

@login_manager.user_loader
def user_loader(username):
    return user_manager.find(username)


@login_manager.request_loader
def request_loader(request):
    username = request.form.get('username')
    user = user_loader(username)
    return user

recent_users = deque(maxlen=3)

@app.route('/')
def main():
    return render_template('main.html')

# Registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if request.method == 'GET':
        return render_template('register.html', form = form)

    if request.method == 'POST':
        if form.validate_on_submit():

            username = request.form.get('username')
            password = request.form.get('password')

            error = user_manager.add(username, password)
        
            if error:
                return render_template('register.html', form = form, error = error)
            else:
                return redirect('/login')

    return redirect('/register')

# Login
@app.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm()

    if request.method == 'GET':
        return render_template('login.html', form = form)

    if request.method == 'POST':
        if form.validate_on_submit():
            username = request.form.get('username')
            password = request.form.get('password')

            user = user_loader(username)
            if user_manager.validate(password, user):
                login_user(user)
                return redirect('/welcom')
            else:
                return render_template('login.html', form = form, error = 'Incorrect login or password!')
        
        return render_template('login.html', form = form)

# Logout
@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')

# Main user panel
@app.route('/welcom', methods=['GET'])
@login_required
def welcom():
    if request.method == 'GET':
        print(current_user.db_id)
        username = current_user.id

        notes = db_manager.many('SELECT id FROM notes WHERE owner = ?', params = (username,))

        return render_template('welcom.html', username=username, notes=notes)

# Rendered note panel
@app.route('/render', methods=['POST'])
@login_required
def render():
    md = request.form.get('markdown','')
    rendered = markdown.markdown(md)
    username = current_user.id
    print(db_manager.insert('INSERT INTO notes (owner, note) VALUES (?, ?)', params = (username, rendered)))
    return render_template('markdown.html', rendered=rendered)

# Previous note panel
@app.route('/render/<rendered_id>')
@login_required
def render_old(rendered_id):

    try:
        username, rendered = db_manager.one(f'SELECT username, note FROM notes WHERE id = ?', params = (rendered_id,))
        if username != current_user.id:
            return 'Access to note forbidden', 403

        return render_template('markdown.html', rendered=rendered)
    except:
        return 'Note not found', 404


if __name__ == '__main__':

    app.run('0.0.0.0', 5000)