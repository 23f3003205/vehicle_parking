from flask import Flask
import os
from application.database import db        #3
from dotenv import load_dotenv
load_dotenv()  # loads variables from .env

app=None

def create_app():
    app=Flask(__name__) # creates a web app instance in flask class and figure out necessay files/packages like templates , static
    app.debug=True
    app.config["SQLALCHEMY_DATABASE_URI"]=  os.getenv("DATABASE_URL") #3  #sets up flask web application  with a SQLIte database using SQLAlchemy
    app.config["SECRET_KEY"]= os.getenv("SECRET_KEY")  #its secret that can  not be disclose it used for session creation
    db.init_app(app) #connect database object with flask app   #3
    app.app_context().push()# brings down everything in context of flask application , throws runtime error when not applied
    return app

app=create_app() #call this function to create app

with app.app_context():
    db.create_all()
from application.controllers import * #2
from application.resources import *   # api implementation




if __name__=="__main__": #this module app.py , run when runned explicitly
    app.run()
