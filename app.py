from flask import Flask, render_template, request, make_response, redirect, send_file
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from collections import deque
from passlib.hash import sha256_crypt
from dotenv import load_dotenv
from source.dbManager import DBManager
import markdown, os

load_dotenv()
app = Flask(__name__)
db_manager = DBManager()
login_manager = LoginManager()
login_manager.init_app(app)
app.secret_key = os.getenv('SECRET_KEY')

class User(UserMixin):
    pass

@login_manager.user_loader
def user_loader(username):
    if username is None:
        return None

    row = db_manager.one(f"SELECT username, password FROM user WHERE username = '{username}'")
    try:
        username, password = row
    except:
        return None

    user = User()
    user.id = username
    user.password = password
    return user


@login_manager.request_loader
def request_loader(request):
    username = request.form.get('username')
    user = user_loader(username)
    return user


recent_users = deque(maxlen=3)

@app.route("/", methods=["GET","POST"])
def login():
    if request.method == "GET":
        return render_template("index.html")
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = user_loader(username)
        if user is None:
            return "Nieprawidłowy login lub hasło", 401
        if sha256_crypt.verify(password, user.password):
            login_user(user)
            return redirect('/hello')
        else:
            return "Nieprawidłowy login lub hasło", 401

@app.route("/logout")
def logout():
    logout_user()
    return redirect("/")

@app.route("/hello", methods=['GET'])
@login_required
def hello():
    if request.method == 'GET':
        print(current_user.id)
        username = current_user.id

        notes = db_manager.many(f"SELECT id FROM notes WHERE username == '{username}'")

        return render_template("hello.html", username=username, notes=notes)

@app.route("/render", methods=['POST'])
@login_required
def render():
    md = request.form.get("markdown","")
    rendered = markdown.markdown(md)
    username = current_user.id
    db_manager.execute(f"INSERT INTO notes (username, note) VALUES ('{username}', '{rendered}')")
    return render_template("markdown.html", rendered=rendered)

@app.route("/render/<rendered_id>")
@login_required
def render_old(rendered_id):

    try:
        username, rendered = db_manager.execute(f"SELECT username, note FROM notes WHERE id == {rendered_id}")

        if username != current_user.id:
            return "Access to note forbidden", 403
        return render_template("markdown.html", rendered=rendered)
    except:
        return "Note not found", 404

@app.route("/user/register", methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template("register.html")
    if request.method == 'POST':

        username = request.form.get('username')
        password = request.form.get('password')

        db_manager.execute(f"INSERT INTO user (username, password) VALUES ('{username}', '{sha256_crypt.hash(password)}')")
        
        return redirect('/')

if __name__ == "__main__":

    app.run("0.0.0.0", 5000)