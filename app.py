import os
from os.path import join, dirname
from dotenv import load_dotenv
from flask import Flask, render_template, flash, redirect, url_for, session, request, g
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from utils import SignUpForm, LoginForm, AddRecipe, value_in_list, update_author_data_liked_recipe, convert_to_son_obj

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
    
@app.route("/page<offset>", methods=["POST", "GET"])
def next_pagination(offset):
    recipes = mongo.db.recipes.find().skip((int(offset)-1) * 6).limit(6)
    allergens = mongo.db.allergens.find_one({"_id": ObjectId("5b2bc45ee7179a5892864417")})
    cuisines = mongo.db.cuisines.find_one({"_id": ObjectId("5b2bc74ae7179a5892864640")})
    recipes_total = mongo.db.recipes.find().count()
    
    if "logged_in" in session:    
        return render_template("dashboard.html", recipes=recipes, author_id=session["id"],
                                allergens=allergens, cuisines=cuisines, offset=offset,
                                recipes_total=recipes_total)
    else:
        return render_template("index.html", recipes=recipes,
                                allergens=allergens, cuisines=cuisines, offset=offset,
                                recipes_total=recipes_total) 

@app.route("/page<offset>", methods=["POST", "GET"])
def prev_pagination(offset):
    recipes = mongo.db.recipes.find().skip((int(offset)-1) * 6).limit(6)
    allergens = mongo.db.allergens.find_one({"_id": ObjectId("5b2bc45ee7179a5892864417")})
    cuisines = mongo.db.cuisines.find_one({"_id": ObjectId("5b2bc74ae7179a5892864640")})
    recipes_total = mongo.db.recipes.find().count()
    
    if "logged_in" in session:    
        return render_template("dashboard.html", recipes=recipes, author_id=session["id"],
                                allergens=allergens, cuisines=cuisines, offset=offset,
                                recipes_total=recipes_total)
    else:
        return render_template("index.html", recipes=recipes,
                                allergens=allergens, cuisines=cuisines, offset=offset,
                                recipes_total=recipes_total)    

@app.route("/filter", methods=["POST", "GET"])
def filter():
    offset = 1
    recipes_total = mongo.db.recipes.find().count()
    recipes = mongo.db.recipes.find()
    allergens = mongo.db.allergens.find_one({"_id": ObjectId("5b2bc45ee7179a5892864417")})
    cuisines = mongo.db.cuisines.find_one({"_id": ObjectId("5b2bc74ae7179a5892864640")})
    the_allergen = ""
    
    if request.method == "POST":
        the_cuisine = request.form["cuisines"].lower()
        the_allergen = request.form["allergens"].lower()
        
        if the_cuisine != "":
            recipes = mongo.db.recipes.find({
                                            "allergens": { "$not": { "$in": [the_allergen] } },
                                            "cuisine": the_cuisine
                                            })
                                            
            recipes_total = mongo.db.recipes.find({
                                            "allergens": { "$not": { "$in": [the_allergen] } },
                                            "cuisine": the_cuisine
                                            }).count()
        else:
            recipes = mongo.db.recipes.find({
                                            "allergens": { "$not": { "$in": [the_allergen] } }
                                            })
            recipes_total = mongo.db.recipes.find({
                                            "allergens": { "$not": { "$in": [the_allergen] } }
                                            }).count()
        if "logged_in" in session: 
            direction = "dashboard.html"
            session_status = True
        else:
            direction = "index.html"
            session_status = False
            
        return render_template(direction , recipes=recipes.limit(6),
                            allergens=allergens, cuisines=cuisines, offset=offset,
                            recipes_total=recipes_total, the_cuisine=the_cuisine,
                            the_allergen=the_allergen, session=session_status)
    

@app.route("/", methods=["POST", "GET"])
def index():
    offset = 1
    recipes_total = mongo.db.recipes.find().count()
    recipes = mongo.db.recipes.find()
    allergens = mongo.db.allergens.find_one({"_id": ObjectId("5b2bc45ee7179a5892864417")})
    cuisines = mongo.db.cuisines.find_one({"_id": ObjectId("5b2bc74ae7179a5892864640")})

    
    return render_template("index.html", recipes=recipes.limit(6),
                            allergens=allergens, cuisines=cuisines, offset=offset,
                            recipes_total=recipes_total)


@app.route("/dashboard", methods=["POST", "GET"])
def dashboard():
    offset = 1
    recipes_total = mongo.db.recipes.find().count()
    recipes = mongo.db.recipes.find().limit(6)
    allergens = mongo.db.allergens.find_one({"_id": ObjectId("5b2bc45ee7179a5892864417")})
    cuisines = mongo.db.cuisines.find_one({"_id": ObjectId("5b2bc74ae7179a5892864640")})
    
    return render_template("dashboard.html", recipes=recipes, author_id=session["id"],
                            allergens=allergens, cuisines=cuisines, offset=offset,
                            recipes_total=recipes_total)
    
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
                "password": generate_password_hash(form.password.data),
                "liked_recipe": [],
                "disliked_recipe": []
            })
            return redirect(url_for('login'))
        
    return render_template('signup.html', form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    offset = 1
    recipes_total = mongo.db.recipes.find().count()
    authors = mongo.db.authors
    allergens = mongo.db.allergens.find_one({"_id": ObjectId("5b2bc45ee7179a5892864417")})
    cuisines = mongo.db.cuisines.find_one({"_id": ObjectId("5b2bc74ae7179a5892864640")})
    if form.validate_on_submit():
        user = authors.find_one({"email": form.email.data}) 
        if user and check_password_hash(user['password'], form.password.data):
            session["logged_in"] = True
            session["username"] = user["username"]
            session["id"] = str(user["_id"])
            flash("You are now logged in")
            return redirect(url_for("dashboard", author_id=session["id"], allergens=allergens,
                                    cuisines=cuisines, offset=offset,
                                    recipes_total=recipes_total))
        else: 
            flash("Wrong username or password")
            return render_template("login.html", form=form)
    
    return render_template("login.html", form=form)

@app.route("/logout")
@login_required
def logout():
    session.clear()
    offset = 1
    recipes_total = mongo.db.recipes.find().count()
    recipes = mongo.db.recipes.find()
    allergens = mongo.db.allergens.find_one({"_id": ObjectId("5b2bc45ee7179a5892864417")})
    cuisines = mongo.db.cuisines.find_one({"_id": ObjectId("5b2bc74ae7179a5892864640")})
    
    return render_template("index.html", recipes=recipes,
                            allergens=allergens, cuisines=cuisines, offset=offset,
                            recipes_total=recipes_total)

@app.route("/addrecipe", methods=["GET", "POST"])
@login_required
def addrecipe():
    form = AddRecipe()
    offset = 1
    recipes_total = mongo.db.recipes.find().count()
    # Allergens for dropdown menu (Jinja2)
    allergens = mongo.db.allergens.find_one({"_id": ObjectId("5b2bc45ee7179a5892864417")})
    cuisines = mongo.db.cuisines.find_one({"_id": ObjectId("5b2bc74ae7179a5892864640")})
    recipes = mongo.db.recipes
    if form.validate_on_submit():
        recipe_exist = recipes.find_one({ "title": form.name.data.lower() })
        
        if not recipe_exist:
            recipes.insert_one({
                "title": form.name.data.lower(),
                "author_name": session["username"].lower(),
                "author_id": session["id"],
                "img_url": form.image_url.data,
                "cuisine": form.cuisine.data,
                "servings": form.servings.data,
                "ingredients": form.ingredients.data.split(","),
                "allergens": request.form.getlist('allergens'),
                "description": form.description.data.lower(),
                "likes": 0,
                "dislikes": 0,
                "users_liked": []
            })
            return redirect(url_for("dashboard", author_id=session["id"], allergens=allergens,
                                    cuisines=cuisines, offset=offset,
                                    recipes_total=recipes_total))
        else:
            flash("The recipe already exist. Please choose another one. ")
            return render_template("addrecipe.html", form=form, allergens=allergens)
    
    return render_template("addrecipe.html", form=form, allergens=allergens)
    
@app.route("/recipe/<recipe_id>")
@login_required
def recipe(recipe_id):
    recipes = mongo.db.recipes
    current_recipe = recipes.find_one({"_id": ObjectId(recipe_id)})
    author = mongo.db.authors.find_one({"_id": ObjectId(session["id"])})
    
    return render_template("recipe.html", recipe=current_recipe, 
                    liked=value_in_list(recipe_id, author["disliked_recipe"]), 
                    disliked=value_in_list(recipe_id, author["liked_recipe"]))
    
@app.route("/recipe/like/<recipe_id>")
@login_required
def like(recipe_id):
    recipes = mongo.db.recipes
    current_recipe = recipes.find_one({"_id": ObjectId(recipe_id)})
    
    authors = mongo.db.authors
    author = authors.find_one({"_id": ObjectId(session["id"])})
    
    if str(session["id"]) in current_recipe["users_liked"] and current_recipe["likes"] > 0:
        update_author_data_liked_recipe(authors, session["id"], "$pull", recipe_id)
        
        recipes.update(
            {"_id": ObjectId(recipe_id)},
            { 
                '$inc': {"likes": -1},
                "$pull": {"users_liked": session["id"]}
            })
    else:
        update_author_data_liked_recipe(authors, session["id"], "$addToSet", recipe_id)
        
        recipes.update(
            {"_id": ObjectId(recipe_id)},
            { 
                '$inc': {"likes": 1},
                "$addToSet": {"users_liked": session["id"]}
            })
        
    return redirect(url_for("recipe", 
                    recipe=current_recipe, recipe_id=recipe_id, 
                    liked=value_in_list(recipe_id, author["disliked_recipe"]), 
                    disliked=value_in_list(recipe_id, author["liked_recipe"])))

@app.route("/recipe/dislike/<recipe_id>")
@login_required
def dislike(recipe_id):
    recipes = mongo.db.recipes
    current_recipe = recipes.find_one({"_id": ObjectId(recipe_id)})
    authors = mongo.db.authors
    author = authors.find_one({"_id": ObjectId(session["id"])})
    
    if str(session["id"]) in current_recipe["users_liked"] and current_recipe["dislikes"] > 0:
        update_author_data_liked_recipe(authors, session["id"], "$pull", recipe_id)
        
        recipes.update(
            {"_id": ObjectId(recipe_id)},
            { 
                '$inc': {"dislikes": -1},
                "$pull": {"users_liked": session["id"]}
            })
    else:
        update_author_data_liked_recipe(authors, session["id"], "$addToSet", recipe_id)
        
        recipes.update(
            {"_id": ObjectId(recipe_id)},
            { 
                '$inc': {"dislikes": 1},
                "$addToSet": {"users_liked": session["id"]}
            })
        
    return redirect(url_for("recipe", recipe=current_recipe, recipe_id=recipe_id, disliked=value_in_list(recipe_id, author["liked_recipe"])))

@app.route("/edit_recipe/<recipe_id>", methods=["GET", "POST"])
@login_required
def edit_recipe(recipe_id):
    form = AddRecipe()
    allergens = mongo.db.allergens.find_one({"_id": ObjectId("5b2bc45ee7179a5892864417")})
    recipes = mongo.db.recipes
    the_recipe = recipes.find_one({"_id": ObjectId(recipe_id)})
    cuisines = mongo.db.cuisines.find_one({"_id": ObjectId("5b2bc74ae7179a5892864640")})
    ingredients_str = ",".join(the_recipe["ingredients"])
    
    if request.method == "POST":
        try:
            recipes.update_one({"_id": ObjectId(recipe_id)},
                            {
                                "$set": {
                                    "title": form.name.data.lower(),
                                    "img_url": form.image_url.data,
                                    
                                    "servings": request.form["servings"],
                                    "cuisine": request.form["cuisine"].lower(),
                                    
                                    "ingredients": form.ingredients.data.split(","),
                                    
                                    "allergens": request.form.getlist('allergens'),
                                    "description": request.form["description"].lower()
                                }
                            }
                            )
            return redirect(url_for("dashboard", author_id=session["id"], allergens=allergens,
                                    cuisines=cuisines))
        except Exception, e:
            flash(e)
    
    return render_template("editrecipe.html", form=form, allergens=allergens,
                            the_recipe=the_recipe, cuisines=cuisines,
                            ingredients_str=ingredients_str)

@app.route("/delete_recipe/<recipe_id>")
@login_required
def delete_recipe(recipe_id):
    mongo.db.recipes.remove({"_id": ObjectId(recipe_id)})
    
    offset = 1
    recipes_total = mongo.db.recipes.find().count()
    allergens = mongo.db.allergens.find_one({"_id": ObjectId("5b2bc45ee7179a5892864417")})
    cuisines = mongo.db.cuisines.find_one({"_id": ObjectId("5b2bc74ae7179a5892864640")})
    
    return redirect(url_for("dashboard", author_id=session["id"], allergens=allergens,
                            cuisines=cuisines, offset=offset, recipes_total=recipes_total))
    
if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)