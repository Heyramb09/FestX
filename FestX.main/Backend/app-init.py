# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import config

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'

def create_app(config_name='default'):
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    app.config.from_object(config[config_name])
    
    db.init_app(app)
    login_manager.init_app(app)
    
    # Register blueprints
    from app.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)
    
    from app.events import events as events_blueprint
    app.register_blueprint(events_blueprint)
    
    from app.admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint)
    
    from app.discussion import discussion as discussion_blueprint
    app.register_blueprint(discussion_blueprint)
    
    from app.contact import contact as contact_blueprint
    app.register_blueprint(contact_blueprint)
    
    from app.about import about as about_blueprint
    app.register_blueprint(about_blueprint)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app

# app.py (in root directory)
from app import create_app, db
from app.models import User, Event, Team, TeamMember, IndividualRegistration, GroupRegistration
from app.models import Quiz, QuizQuestion, QuizOption, QuizAttempt, UserAnswer
from app.models import Announcement, Notification, Certificate, Result

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db, 'User': User, 'Event': Event, 'Team': Team, 
        'TeamMember': TeamMember, 'IndividualRegistration': IndividualRegistration, 
        'GroupRegistration': GroupRegistration, 'Quiz': Quiz, 
        'QuizQuestion': QuizQuestion, 'QuizOption': QuizOption, 
        'QuizAttempt': QuizAttempt, 'UserAnswer': UserAnswer,
        'Announcement': Announcement, 'Notification': Notification,
        'Certificate': Certificate, 'Result': Result
    }

if __name__ == '__main__':
    app.run(debug=True)
