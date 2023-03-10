from flask import Flask, render_template, request, redirect, url_for, abort
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_wtf.csrf import CSRFError, CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
from source.userManager import UserManager
from source.dbManager import DBManager
from source.noteManager import NoteManager
from source.models import RegisterForm, LoginForm, LockForm, UnlockForm, MarkdownForm, NoteForm, PasswordRecoveryForm, PasswordRecoveryTokenForm, LogoutForm
from werkzeug.middleware.proxy_fix import ProxyFix 
import os

load_dotenv()

login_manager=LoginManager()
db_manager=DBManager()
user_manager=UserManager()
note_manager=NoteManager()
csrf=CSRFProtect()


app=Flask(__name__)
app.config['SECRET_KEY']=os.getenv('SECRET_KEY')
app.config['WTF_CSRF_SECRET_KEY']=os.getenv('CSRF_SECRET_KEY')
app.wsgi_app = ProxyFix(app.wsgi_app)

csrf.init_app(app)
login_manager.init_app(app)
db_manager.init()
limiter=Limiter(get_remote_address, app=app, default_limits=[os.getenv('REQUESTS_LIMIT')], storage_uri="memory://")

@login_manager.user_loader
def user_loader(username):
    return user_manager.find(username)


@login_manager.request_loader
def request_loader(request):
    username=request.form.get('username')
    user=user_loader(username)
    return user

# Main page
@app.route('/')
def main():
    return render_template('main.html')

# Registration
@app.route('/register', methods=['GET', 'POST'])
@limiter.limit("50/day", methods=['POST'])
@limiter.limit("10/minute" , methods=['POST'])
def register():
    form=RegisterForm()

    if request.method=='GET':
        return render_template('register.html', form=form)

    if request.method=='POST':
        if form.validate_on_submit():

            username=request.form.get('username')
            password=request.form.get('password')
            email=request.form.get('email')

            error=user_manager.add(username, password, email)
        
            if error:
                return render_template('register.html', form=form, error=error)
            else:
                return redirect('/login')
        else:
            return render_template('register.html', form=form)

    return redirect('/register')

# Login
@app.route('/login', methods=['GET','POST'])
@limiter.limit("50/day", methods=['POST'])
@limiter.limit("5/minute", methods=['POST'])
def login():
    form=LoginForm()

    if request.method=='GET':
        return render_template('login.html', form=form)

    if request.method=='POST':
        if form.validate_on_submit():
            username=request.form.get('username')
            password=request.form.get('password')
            host=request.remote_addr

            if user_manager.reach_limit(username, host):
                return render_template('login.html', form=form, error='Too many attempts! Wait a few minutes.')

            user=user_loader(username)
            if user_manager.validate(password, user):
                login_user(user)
                return redirect('/welcom')
            else:
                return render_template('login.html', form=form, error='Incorrect login or password!')

        return render_template('login.html', form=form)

# Logout
@app.route('/logout', methods=['POST'])
def logout():
    logout_user()
    return redirect('/')

# Password recovery
@limiter.limit("50/day", methods=['POST'])
@limiter.limit("5/minute", methods=['POST'])
@app.route('/password_recovery', methods=['GET', 'POST'])
def password_recovery():
    form=PasswordRecoveryForm()
    token_form=PasswordRecoveryTokenForm()

    if request.method=='GET':
        return render_template('password.html', state=1, form=form)

    if request.method=='POST':
        if form.validate_on_submit():
            username=request.form.get('username')
            email=request.form.get('email')
            error=user_manager.validate_recovery_data(username, email)

            if error is not None:
                return render_template('password.html', state=1, form=form, error=error)
            else:
                token=user_manager.generate_token(username, email)

                if token is not None:
                    return render_template('password.html', state=2, form=token_form, token=token, username=username, email=email)
        else:
            return render_template('password.html', state=1, form=form)
    
    abort(404)

# New password
@limiter.limit("50/day", methods=['POST'])
@limiter.limit("5/minute", methods=['POST'])
@app.route('/password_new', methods=['POST'])
def password_new():
    token_form=PasswordRecoveryTokenForm()

    if request.method=='POST':
        username=request.form.get('username')
        email=request.form.get('email')

        if token_form.validate_on_submit():
            token=request.form.get('token')

            new_pass=request.form.get('new_password')


            error=user_manager.set_password(username, email, token, new_pass)

            if error is not None:
                return render_template('password.html', state=2, form=token_form, error=error, username=username, email=email)
            else:
                return redirect('/login')
        else:
            return render_template('password.html', state=2, form=token_form, username=username, email=email)
    
    abort(404)

# Main user panel
@app.route('/welcom', methods=['GET'])
@login_required
def welcom():
    if request.method=='GET':
        form=NoteForm()
        logout_form=LogoutForm()

        username=current_user.id
        notes=note_manager.find_by_author(username)
        public_notes=note_manager.find_public(username)
        draft=note_manager.find_draft(username)
        logs=user_manager.find_logs(username)

        return render_template('welcom.html', form=form, username=username, notes=notes, public_notes=public_notes, draft=draft, logs=logs, logout_form=logout_form)

    return redirect('/login')

# Obtain key for encrypt note
@app.route('/lock', methods=['GET', 'POST'])
@login_required
def lock():
    form=LockForm()
    username=current_user.id

    if request.method=='GET':
        return render_template('key.html', state=True, form=form)

    if request.method=='POST':
        if form.validate_on_submit():
            key=request.form.get('key')
            note_manager.lock(username, key)
            return redirect('/welcom')
        else:
            return render_template('key.html', state=True, form=form)
    abort(404)

# Obtain key for decrypt note
@app.route('/unlock/<rendered_id>', methods=['GET', 'POST'])
@login_required
def unlock(rendered_id):
    key_form=UnlockForm()
    logout_form=LogoutForm()
    
    if note_manager.is_author(rendered_id, current_user.id):
        if request.method=='GET':
            return render_template('key.html', form=key_form, rendered_id=rendered_id)

        if request.method=='POST':
            if key_form.validate_on_submit():
                key=request.form.get('key')

                rendered=note_manager.find_by_id_encrypted(rendered_id, key)
        
                if rendered is not None:
                    return render_template('markdown.html', rendered=rendered, logout_form=logout_form)
                else:
                    return render_template('key.html', form=key_form, rendered_id=rendered_id, error="Key is invalid!")

            else:
                return render_template('key.html', form=key_form)
    abort(404)

# Rendered note panel
@app.route('/render', methods=['POST'])
@login_required
def render():
    form=MarkdownForm()
    logout_form=LogoutForm()

    rendered, is_safe=note_manager.render(current_user.id, request.form.get('markdown',''))
    
    if is_safe:
        return render_template('markdown.html', form=form, rendered=rendered, logout_form=logout_form)
    else:
        return render_template('markdown.html', form=form, rendered=rendered, error='Some information has been transformed due to safety policy!', logout_form=logout_form)

@app.route('/save', methods=['POST'])
@login_required
def save():
    username=current_user.id

    try:
        type=int(request.form.get('type'))
    except:
        type=1

    if type==1:
        note_manager.save(username, False)
    
    if type==2:
        return redirect('/lock')

    if type==3:
        note_manager.save(username, True)
    
    return redirect('/welcom')
    

# Previous note panel
@app.route('/show/<int:rendered_id>', methods=['GET'])
@login_required
def show(rendered_id):
    logout_form=LogoutForm()

    if note_manager.is_author(rendered_id, current_user.id):

        if note_manager.is_encrypted(rendered_id):

            return redirect(url_for('unlock', rendered_id=rendered_id))
        else:
            rendered=note_manager.find_by_id(rendered_id)

        if rendered is not None:
            return render_template('markdown.html', rendered=rendered, logout_form=logout_form)

    if note_manager.is_public(rendered_id):
        rendered=note_manager.find_by_id(rendered_id)

        if rendered is not None:
            return render_template('markdown.html', rendered=rendered, logout_form=logout_form)

    abort(404)

@app.errorhandler(Exception)
def handle_exception(e):
    return_btn=True
    login_btn=False
    error=None

    try:
        code=e.code
    except:
        code=None 

    if code==401:
        login_btn=True
        error='Authorization required for this page...'
    elif code==404:
        error='Page not found...'
    elif code==429:
        # Limiter error handler
        error='Too many request! Slow down...'

    return render_template('error.html', error=error, return_btn =return_btn, login_btn=login_btn)

@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    return render_template('error.html', error='CSRF Protection')