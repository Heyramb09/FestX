# main.py - Main blueprint
from flask import Blueprint, render_template, current_app
from flask_login import current_user
from .models import Announcement, Event, FAQ
from datetime import datetime

main = Blueprint('main', __name__)

@main.route('/')
def index():
    # Get upcoming events
    upcoming_events = Event.query.filter(Event.date > datetime.utcnow()).order_by(Event.date).limit(3).all()
    
    # Get recent announcements
    announcements = Announcement.query.order_by(Announcement.created_at.desc()).limit(5).all()
    
    return render_template('main/index.html', 
                           upcoming_events=upcoming_events,
                           announcements=announcements)

@main.route('/about')
def about():
    return render_template('main/about.html')

@main.context_processor
def inject_user():
    return dict(current_user=current_user)
