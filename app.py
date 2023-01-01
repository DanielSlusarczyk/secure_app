from flask import Flask, render_template, request, redirect
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from collections import deque
from dotenv import load_dotenv
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
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
limiter = Limiter(get_remote_address, app = app, default_limits = [os.getenv('REQUESTS_LIMIT')])

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
@limiter.limit("50/day", methods=['POST'])
@limiter.limit("10/minute" , methods=['POST'])
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
@limiter.limit("50/day", methods=['POST'])
@limiter.limit("5/minute", methods=['POST'])
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
        username = current_user.id

        notes = db_manager.many('SELECT id FROM notes WHERE owner = ?', params = (username,))

        return render_template('welcom.html', username=username, notes=notes)

    return redirect('/login')

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
        username, rendered = db_manager.one(f'SELECT owner, note FROM notes WHERE id = ?', params = (rendered_id,))
        if username != current_user.id:
            return '', 404

        return render_template('markdown.html', rendered=rendered)
    except:
        return '', 404

@app.errorhandler(401)
def limit_handler(e):
    return render_template('error.html', error='Authorization required for this page...', return_btn=True, login_btn=True)

@app.errorhandler(404)
def limit_handler(e):
    return render_template('error.html', error='Page not found...', return_btn=True)

@app.errorhandler(429)
def limit_handler(e):
    return render_template('error.html', error='Too many request... slow down!')

if __name__ == '__main__':

    app.run('0.0.0.0', 5000)