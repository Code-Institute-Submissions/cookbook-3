import os
from os.path import join, dirname
from dotenv import load_dotenv
from flask import Flask, render_template, flash, redirect, url_for, session, request, g
from flask_pymongo import PyMongo
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from utils import SignUpForm, LoginForm

dotenv_path = join(dirname(__file__), ".env")
load_dotenv(dotenv_path)

app = Flask(__name__)

app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config["MONGO_DBNAME"] = os.getenv("MONGO_DBNAME")
app.config["MONGO_URI"] = os.getenv("MONGO_URI")

mongo = PyMongo(app)

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if "logged_in" in session:
            return f(*args, **kwargs)
        else:
            flash("You need to login first")
            return redirect(url_for("login"))
    return wrap

@app.route("/")
def index():
    return render_template("index.html")

    
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignUpForm()
    authors = mongo.db.authors
    if form.validate_on_submit():
        user_exist = authors.find_one({"email":form.email.data})
        if user_exist:
            flash("The email is already used, please choose another one or sign in")
            return render_template('signup.html', form=form)
        else:
            authors.insert_one({
                "username": form.name.data,
                "email": form.email.data,
                "contry": form.origin.data,
                "password": generate_password_hash(form.password.data)
            })
            return redirect(url_for('login'))
        
    return render_template('signup.html', form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    authors = mongo.db.authors
    if form.validate_on_submit():
        user = authors.find_one({"email": form.email.data}) 
        if user and check_password_hash(user['password'], form.password.data):
            session["logged_in"] = True
            session["user"] = user["username"]
            flash("You are now logged in")
            return redirect(url_for("dashboard"))
        else: 
            flash("Wrong username or password")
            return render_template("login.html", form=form)
    
    return render_template("login.html", form=form)

@app.route("/logout")
@login_required
def logout():
    session.clear()
    return render_template("index.html")
    
@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")

@app.route("/addrecipe")
@login_required
def addrecipe():
    return render_template("addrecipe.html")
    
if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)