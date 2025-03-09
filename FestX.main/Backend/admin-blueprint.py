# admin.py - Admin blueprint
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, BooleanField, DateTimeField, SelectField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Optional
from .models import (User, Event, IndividualRegistration, GroupRegistration, Team, 
                    TeamMember, Announcement, Notification, Certificate, Result,
                    Quiz, QuizQuestion, QuizOption, FAQ, ContactQuery)
from . import db
from datetime import datetime
from functools import wraps

admin = Blueprint('admin', __name__, url_prefix='/admin')

# Admin required decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('You do not have permission to access this page.')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

# Forms
class EventForm(FlaskForm):
    name = StringField('Event Name', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    category = StringField('Category', validators=[DataRequired()])
    venue = StringField('Venue', validators=[DataRequired()])
    date = DateTimeField('Event Date', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    registration_deadline = DateTimeField('Registration Deadline', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    max_participants = IntegerField('Maximum Participants', validators=[Optional(), NumberRange(min=1)])
    is_team_event = BooleanField('Team Event')
    min_team_size = IntegerField('Minimum Team Size', validators=[Optional(), NumberRange(min=1)])
    max_team_size = IntegerField('Maximum Team Size', validators=[Optional(), NumberRange(min=1)])
    submit = SubmitField('Save Event')

class AnnouncementForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    is_pinned = BooleanField('Pin Announcement')
    submit = SubmitField('Post Announcement')

class FAQForm(FlaskForm):
    question = StringField('Question', validators=[DataRequired()])
    answer = TextAreaField('Answer', validators=[DataRequired()])
    category = StringField('Category', validators=[Optional()])
    is_published = BooleanField('Publish', default=True)
    submit = SubmitField('Save FAQ')

# Routes
@admin.route('/')
@login_required
@admin_required
def index():
    # Dashboard statistics
    stats = {
        'total_users': User.query.count(),
        'total_events': Event.query.count(),
        'upcoming_events': Event.query.filter(Event.date > datetime.utcnow()).count(),
        'total_registrations': IndividualRegistration.query.count() + GroupRegistration.query.count(),
        'total_teams': Team.query.count(),
        'unresolved_queries': ContactQuery.query.filter_by(is_resolved=False).count()
    }
    
    # Recent activities
    recent_registrations = IndividualRegistration.query.order_by(IndividualRegistration.registered_at.desc()).limit(5).all()
    recent_announcements = Announcement.query.order_by(Announcement.created_at.desc()).limit(5).all()
    
    return render_template('admin/index.html', 
                           stats=stats,
                           recent_registrations=recent_registrations,
                           recent_announcements=recent_announcements)

# Events Management
@admin.route('/events')
@login_required
@admin_required
def events_list():
    events = Event.query.order_by(Event.date.desc()).all()
    return render_template('admin/events/index.html', events=events)

@admin.route('/events/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_event():
    form = EventForm()
    
    if form.validate_on_submit():
        event = Event(
            name=form.name.data,
            description=form.description.data,
            category=form.category.data,
            venue=form.venue.data,
            date=form.date.data,
            registration_deadline=form.registration_deadline.data,
            max_participants=form.max_participants.data,
            is_team_event=form.is_team_event.data,
            min_team_size=form.min_team_size.data if form.is_team_event.data else 1,
            max_team_size=form.max_team_size.data if form.is_team_event.data else 1
        )
        db.session.add(event)
        db.session.commit()
        
        flash(f'Event "{event.name}" has been created!')
        return redirect(url_for('admin.events_list'))
    
    return render_template('admin/events/create.html', form=form)

@admin.route('/events/<int:event_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_event(event_id):
    event = Event.query.get_or_404(event_id)
    form = EventForm(obj=event)
    
    if form.validate_on_submit():
        form.populate_obj(event)
        db.session.commit()
        
        flash(f'Event "{event.name}" has been updated!')
        return redirect(url_for('admin.events_list'))
    
    return render_template('admin/events/edit.html', form=form, event=event)

@admin.route('/events/<int:event_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    
    # Check if there are any registrations
    has_registrations = IndividualRegistration.query.filter_by(event_id=event_id).first() or \
                       GroupRegistration.query.filter_by(event_id=event_id).first()
    
    if has_registrations:
        flash('Cannot delete event with existing registrations.')
        return redirect(url_for('admin.events_list'))
    
    db.session.delete(event)
    db.session.commit()
    
    flash(f'Event "{event.name}" has been deleted!')
    return redirect(url_for('admin.events_list'))

@admin.route('/events/<int:event_id>/participants')
@login_required
@admin_required
def event_participants(event_id):
    event = Event.query.get_or_404(event_id)
    
    # Individual registrations
    individual_registrations = IndividualRegistration.query.filter_by(event_id=event_id).all()
    individual_participants = []
    
    for reg in individual_registrations:
        user = User.query.get(reg.user_id)
        if user:
            participant = {
                'user': user,
                'status': reg.status,
                'registered_at': reg.registered_at
            }
            individual_participants.append(participant)
    
    # Team registrations
    group_registrations = GroupRegistration.query.filter_by(event_id=event_id).all()
    team_participants = []
    
    for reg in group_registrations:
        team = Team.query.get(reg.team_id)
        if team:
            # Get team members
            team_members = []
            memberships = TeamMember.query.filter_by(team_id=team.id).all()
            
            for membership in memberships:
                user = User.query.get(membership.user_id)
                if user:
                    member = {
                        'user': user,
                        'role': membership.role
                    }
                    team_members.append(member)
            
            team_data = {
                'team': team,
                'status': reg.status,
                'registered_at': reg.registered_at,
                'members': team_members
            }
            team_participants.append(team_data)
    
    return render_template('admin/events/participants.html',
                           event=event,
                           individual_participants=individual_participants,
                           team_participants=team_participants)

@admin.route('/events/<int:event_id>/notify', methods=['GET', 'POST'])
@login_required
@admin_required
def notify_participants(event_id):
    event = Event.query.get_or_404(event_id)
    
    if request.method == 'POST':
        title = request.form.get('title')
        message = request.form.get('message')
        
        if title and message:
            # Get all participants
            individual_regs = IndividualRegistration.query.filter_by(event_id=event_id).all()
            group_regs = GroupRegistration.query.filter_by(event_id=event_id).all()
            
            # Set to store unique user IDs
            user_ids = set()
            
            # Add individual participants
            for reg in individual_regs:
                user_ids.add(reg.user_id)
            
            # Add team members
            for reg in group_regs:
                memberships = TeamMember.query.filter_by(team_id=reg.team_id).all()
                for membership in memberships:
                    user_ids.add(membership.user_id)
            
            # Create notifications
            for user_id in user_ids:
                notification = Notification(
                    user_id=user_id,
                    title=title,
                    message=message
                )
                db.session.add(notification)
            
            db.session.commit()
            flash(f'Notification sent to {len(user_ids)} participants!')
            return redirect(url_for('admin.event_participants', event_id=event_id))
        else:
            flash('Title and message are required.')
    
    return render_template('admin/events/notify.html', event=event)

# User Management
@admin.route('/users')
@login_required
@admin_required
def users_list():
    users = User.query.order_by(User.username).all()
    return render_template('admin/users/index.html', users=users)

@admin.route('/users/<int:user_id>')
@login_required
@admin_required
def user_details(user_id):
    user = User.query.get_or_404(user_id)
    
    # Get user's registrations
    individual_regs = IndividualRegistration.query.filter_by(user_id=user_id).all()
    individual_events = []
    
    for reg in individual_regs:
        event = Event.query.get(reg.event_id)
        if event:
            reg_data = {
                'event': event,
                'status': reg.status,
                'registered_at': reg.registered_at
            }
            individual_events.append(reg_data)
    
    # Get user's teams
    team_memberships = TeamMember.query.filter_by(user_id=user_id).all()
    teams = []
    
    for membership in team_memberships:
        team = Team.query.get(membership.team_id)
        if team:
            team_data = {
                'team': team,
                'role': membership.role,
                'joined_at': membership.joined_at
            }
            teams.append(team_data)
    
    return render_template('admin/users/details.html',
                           user=user,
                           individual_events=individual_events,
                           teams=teams)

@admin.route('/users/<int:user_id>/toggle-admin', methods=['POST'])
@login_required
@admin_required
def toggle_admin(user_id):
    user = User.query.get_or_404(user_id)
    
    # Prevent self-demotion
    if user.id == current_user.id:
        flash('You cannot change your own admin status.')
        return redirect(url_for('admin.users_list'))
    
    user.is_admin = not user.is_admin
    db.session.commit()
    
    action = 'granted' if user.is_admin else 'revoked'
    flash(f'Admin privileges {action} for {user.username}!')
    return redirect(url_for('admin.users_list'))

# Announcements
@admin.route('/announcements')
@login_required
@admin_required
def announcements_list():
    announcements = Announcement.query.order_by(Announcement.created_at.desc()).all()
    return render_template('admin/announcements/index.html', announcements=announcements)

@admin.route('/announcements/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_announcement():
    form = AnnouncementForm()
    
    if form.validate_on_submit():
        announcement = Announcement(
            title=form.title.data,
            content=form.content.data,
            author_id=current_user.id,
            is_pinned=form.is_pinned.data
        )
        db.session.add(announcement)
        db.session.commit()
        
        flash('Announcement has been posted!')
        return redirect(url_for('admin.announcements_list'))
    
    return render_template('admin/announcements/create.html', form=form)

@admin.route('/announcements/<int:announcement_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_announcement(announcement_id):
    announcement = Announcement.query.get_or_404(announcement_id)
    form = AnnouncementForm(obj=announcement)
    
    if form.validate_on_submit():
        form.populate_obj(announcement)
        announcement.updated_at = datetime.utcnow()
        db.session.commit()
        
        flash('Announcement has been updated!')
        return redirect(url_for('admin.announcements_list'))
    
    return render_template('admin/announcements/edit.html', form=form, announcement=announcement)

@admin.route('/announcements/<int:announcement_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_announcement(announcement_id):
    announcement = Announcement.query.get_or_404(announcement_id)
    db.session.delete(announcement)
    db.session.commit()
    
    flash('Announcement has been deleted!')
    return redirect(url_for('admin.announcements_list'))

# FAQ Management
@admin.route('/faqs')
@login_required
@admin_required
def faqs_list():
    faqs = FAQ.query.order_by(FAQ.category, FAQ.id).all()
    return render_template('admin/faqs/index.html', faqs=faqs)

@admin.route('/faqs/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_faq():
    form = FAQForm()
    
    if form.validate_on_submit():
        faq = FAQ(
            question=form.question.data,
            answer=form.answer.data,
            category=form.category.data,
            is_published=form.is_published.data
        )
        db.session.add(faq)
        db.session.commit()
        
        flash('FAQ has been created!')
        return redirect(url_for('admin.faqs_list'))
    
    return render_template('admin/faqs/create.html', form=form)

@admin.route('/faqs/<int:faq_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_faq(faq_id):
    faq = FAQ.query.get_or_404(faq_id)
    form = FAQForm(obj=faq)
    
    if form.validate_on_submit():
        form.populate_obj(faq)
        faq.updated_at = datetime.utcnow()
        db.session.commit()
        
        flash('FAQ has been updated!')
        return redirect(url_for('admin.faqs_list'))
    
    return render_template('admin/faqs/edit.html', form=form, faq=faq)

@admin.route('/faqs/<int:faq_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_faq(faq_id):
    faq = FAQ.query.get_or_404(faq_id)
    db.session.delete(faq)
    db.session.commit()
    
    flash('FAQ has been deleted!')
    return redirect(url_for('admin.faqs_list'))

# Contact Queries
@admin.route('/contact-queries')
@login_required
@admin_required
def contact_queries():
    queries = ContactQuery.query.order_by(ContactQuery.created_at.desc()).all()
    return render_template('admin/contact_queries.html', queries=queries)

@admin.route('/contact-queries/<int:query_id>/toggle-resolved', methods=['POST'])
@login_required
@admin_required
def toggle_query_resolved(query_id):
    query = ContactQuery.query.get_or_404(query_id)
    query.is_resolved = not query.is_resolved
    
    if query.is_resolved:
        query.resolved_at = datetime.utcnow()
    else:
        query.resolved_at = None
    
    db.session.commit()
    
    status = 'resolved' if query.is_resolved else 'pending'
    flash(f'Query marked as {status}!')
    return redirect(url_for('admin.contact_queries'))
