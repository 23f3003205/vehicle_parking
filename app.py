from flask import Flask 
from application.database import db        #3


app=None

def create_app():
    app=Flask(__name__) # creates a web app instance in flask class and figure out necessay files/packages like templates , static
    app.debug=True
    app.config["SQLALCHEMY_DATABASE_URI"]='sqlite:///vehicle_parking.sqlite3' #3  #sets up flask web application  with a SQLIte database using SQLAlchemy
    app.config["SECRET_KEY"]="session-secret-key"  #its secret that can  not be disclose it used for session creation
    db.init_app(app) #connect database object with flask app   #3
    app.app_context().push()# brings down everything in context of flask application , throws runtime error when not applied
    return app

app=create_app() #call this function to create app

from application.controllers import * #2
from application.resources import *   # api implementation




if __name__=="__main__": #this module app.py , run when runned explicitly
    app.run()
