# app.py - Main application file
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = 'your-secret-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fest.db'  # Replace with your actual DB URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    
    # Set login view
    login_manager.login_view = 'auth.login'
    
    # Register blueprints
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)
    
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    from .events import events as events_blueprint
    app.register_blueprint(events_blueprint)
    
    from .admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint)
    
    from .discussion import discussion as discussion_blueprint
    app.register_blueprint(discussion_blueprint)
    
    from .contact import contact as contact_blueprint
    app.register_blueprint(contact_blueprint)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app

# Command to run the app
if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
