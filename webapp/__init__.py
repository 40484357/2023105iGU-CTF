from flask import Flask, url_for
from os import path
from flask_login import LoginManager, current_user
from dynamodb import loadUser
from .utils import User

def create_app():
    application = Flask(__name__)
    application.config['SECRET_KEY'] = 'itsasecret'
    

    from .views import views
    from .auth import auth
    application.register_blueprint(views, url_prefix='/')
    application.register_blueprint(auth, url_prefix='/')
     

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