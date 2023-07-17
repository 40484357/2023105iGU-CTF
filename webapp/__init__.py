from flask import Flask, url_for
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager, current_user
from dynamodb import loadUser
from .utils import User


db = SQLAlchemy()

DB_NAME = "database.db"
def create_app():
    application = Flask(__name__)
    application.config['SECRET_KEY'] = 'itsasecret'
    application.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(application)
    

    from .views import views
    from .auth import auth
    application.register_blueprint(views, url_prefix='/')
    application.register_blueprint(auth, url_prefix='/')
    from .models import users 

    with application.app_context():
        db.create_all()
     

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(application)

    @login_manager.user_loader
    def load_user(email):
        print('email is ' + email)
        items = loadUser(email)
        print(items)

        if items == None:
            return
        user = User(email=email, password=items[0]["password"], user_name=items[0]["user_name"], lecturerCode=items[0]['lecturerCode'], lecturerStatus=items[0]['lecturerStatus'])
        return user
        
    return application