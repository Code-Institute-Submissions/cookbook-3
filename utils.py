import os
from os.path import join, dirname
from dotenv import load_dotenv
from flask import Flask
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, TextAreaField
from wtforms.fields.html5 import URLField
from wtforms.validators import InputRequired, Email, Length, EqualTo, ValidationError
from flask_pymongo import PyMongo
from bson.objectid import ObjectId

dotenv_path = join(dirname(__file__), ".env")
load_dotenv(dotenv_path)

app = Flask(__name__)

app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config["MONGO_DBNAME"] = os.getenv("MONGO_DBNAME")
app.config["MONGO_URI"] = os.getenv("MONGO_URI")

mongo = PyMongo(app)

class SignUpForm(FlaskForm):
    name = StringField('Full Name', 
                        validators=[InputRequired(), 
                                    Length(min=2, max=70)],
                        render_kw={"placeholder": "Enter full name"})
    origin = StringField('Place of origin', 
                        validators=[InputRequired(), 
                                    Length(min=2, max=255)],
                        render_kw={"placeholder": "Enter country of origin"})
    email = StringField('Email address', 
                        validators=[InputRequired(), 
                                    Email(message="Invalid email address"), 
                                    Length(min=3, max=255)],
                        render_kw={"placeholder": "Enter email"})
    password = PasswordField('Password', 
                        validators=[InputRequired(), 
                                    EqualTo('confirm', message='Passwords must match'), 
                                    Length(min=4, max=12)],
                        render_kw={"placeholder": "Enter password"})
    confirm = PasswordField('Confirm password',
                        render_kw={"placeholder": "Confirm your password"})
                        
class LoginForm(FlaskForm):
    email = StringField('Email address', 
                        validators=[InputRequired(), 
                                    Email(message="Invalid email address"), 
                                    Length(min=3, max=255)],
                        render_kw={"placeholder": "Enter email"})
    password = PasswordField('Password', 
                        validators=[InputRequired(), 
                                    Length(min=4, max=12)],
                        render_kw={"placeholder": "Enter password"})


# Related to AddRecipe class / Generate to SON object
def convert_to_son_obj(db):
    list = []
    
    for key in db["names"]:
        list.append((key, db["names"][key]))
    
    return list    
    
class AddRecipe(FlaskForm):
    db_cuisines = mongo.db.cuisines
    db_cuisines = db_cuisines.find_one({"_id": ObjectId("5b2bc74ae7179a5892864640")})
    
    cuisine = convert_to_son_obj(db_cuisines)
    
    name = StringField("Recipe Name", 
                        validators=[InputRequired(),
                        Length(min=4, max=100)])
    image_url = URLField("Image URL", 
                        validators=[InputRequired()],
                        render_kw={"placeholder": "http://..."})
    cuisine  = SelectField("Cuisine", choices=cuisine, 
                            validators=[InputRequired()])
    servings = SelectField("Servings", 
                            choices=[("1", "1"), ("2", "2"), ("3", "3"), ("4", "4"), ("5", "5")], 
                            validators=[InputRequired()])
    ingredients = StringField("Ingredients", 
                                validators=[InputRequired()],
                                description="Separate ingredients with comma",
                                render_kw={"placeholder": "white rice, chicken, olive oil"})
    description = TextAreaField("Description", 
                                validators=[InputRequired()])
    
# Like and Dislike actions

def value_in_list(value, list):
    if value in list:
        boolean = True
    else:
        boolean = False
    return boolean
    
def update_author_data_liked_recipe(data, author_id, operator, value):
    data.update({"_id": ObjectId(author_id)},
                    {
                       operator: {"liked_recipe": value}
                    })