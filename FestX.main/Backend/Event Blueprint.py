# events.py - Events blueprint
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, SubmitField, SelectField
from wtforms.validators import DataRequired, NumberRange, ValidationError
from .models import Event, Team, TeamMember, IndividualRegistration, GroupRegistration
from . import db
from datetime import datetime

events = Blueprint('events', __name__)

# Forms
class TeamCreationForm(FlaskForm):
    name = StringField('Team Name', validators=[DataRequired()])
    submit = SubmitField('Create Team')
    
    def validate_name(self, field):
        if Team.query.filter_by(name=field.data).first():
            raise ValidationError('Team name already exists.')

# Routes
@events.route('/events')
def index():
    # Get all event categories
    categories = db.session.query(Event.category).distinct().all()
    categories = [category[0] for category in categories if category[0]]
    
    # Filter events by category if provided
    category = request.args.get('category', None)
    if category:
        events_list = Event.query.filter_by(category=category).order_by(Event.date).all()
    else:
        events_list = Event.query.order_by(Event.date).all()
    
    return render_template('events/index.html', events=events_list, categories=categories, selected_category=category)

@events.route('/events/<int:event_id>')
def event_details(event_id):
    event = Event.query.get_or_404(event_id)
    
    # Check if user is registered for this event
    is_registered = False
    registered_team = None
    
    if current_user.is_authenticated:
        # Check individual registration
        individual_reg = IndividualRegistration.query.filter_by(user_id=current_user.id, event_id=event_id).first()
        if individual_reg:
            is_registered = True
        
        # Check team registration
        if event.is_team_event:
            # Get all teams where user is a member
            user_teams = TeamMember.query.filter_by(user_id=current_user.id).all()
            for team_member in user_teams:
                group_reg = GroupRegistration.query.filter_by(team_id=team_member.team_id, event_id=event_id).first()
                if group_reg:
                    is_registered = True
                    registered_team = team_member.team
                    break
    
    return render_template('events/event_details.html', 
                           event=event,
                           is_registered=is_registered,
                           registered_team=registered_team)

@events.route('/events/<int:event_id>/register', methods=['GET', 'POST'])
@login_required
def register_event(event_id):
    event = Event.query.get_or_404(event_id)
    
    # Check if registration is still open
    if datetime.utcnow() > event.registration_deadline:
        flash('Registration for this event has closed.')
        return redirect(url_for('events.event_details', event_id=event_id))
    
    # Check if already registered
    individual_reg = IndividualRegistration.query.filter_by(user_id=current_user.id, event_id=event_id).first()
    if individual_reg:
        flash('You are already registered for this event.')
        return redirect(url_for('events.event_details', event_id=event_id))
    
    if event.is_team_event:
        # Team event registration
        # Get user's teams
        user_teams = []
        team_memberships = TeamMember.query.filter_by(user_id=current_user.id).all()
        for membership in team_memberships:
            team = Team.query.get(membership.team_id)
            if team:
                # Check if team size meets requirements
                member_count = TeamMember.query.filter_by(team_id=team.id).count()
                if member_count >= event.min_team_size and member_count <= event.max_team_size:
                    # Check if team is already registered
                    existing_reg = GroupRegistration.query.filter_by(team_id=team.id, event_id=event_id).first()
                    if not existing_reg:
                        user_teams.append(team)
        
        if request.method == 'POST':
            team_id = request.form.get('team_id')
            if team_id:
                team = Team.query.get(team_id)
                if team:
                    # Register the team
                    group_reg = GroupRegistration(
                        team_id=team.id,
                        event_id=event.id
                    )
                    db.session.add(group_reg)
                    db.session.commit()
                    flash(f'Team {team.name} has been registered for {event.name}!')
                    return redirect(url_for('events.event_details', event_id=event_id))
            else:
                flash('Please select a valid team.')
        
        return render_template('events/register_team.html', event=event, teams=user_teams)
    else:
        # Individual event registration
        if request.method == 'POST':
            # Register the user
            registration = IndividualRegistration(
                user_id=current_user.id,
                event_id=event.id
            )
            db.session.add(registration)
            db.session.commit()
            flash(f'You have successfully registered for {event.name}!')
            return redirect(url_for('events.event_details', event_id=event_id))
        
        return render_template('events/register_individual.html', event=event)

@events.route('/teams')
@login_required
def my_teams():
    # Get teams where the user is a member
    team_memberships = TeamMember.query.filter_by(user_id=current_user.id).all()
    teams = []
    
    for membership in team_memberships:
        team = Team.query.get(membership.team_id)
        if team:
            member_count = TeamMember.query.filter_by(team_id=team.id).count()
            team_data = {
                'team': team,
                'role': membership.role,
                'member_count': member_count
            }
            teams.append(team_data)
    
    return render_template('events/my_teams.html', teams=teams)

@events.route('/teams/create', methods=['GET', 'POST'])
@login_required
def create_team():
    form = TeamCreationForm()
    
    if form.validate_on_submit():
        team = Team(
            name=form.name.data,
            leader_id=current_user.id
        )
        db.session.add(team)
        db.session.flush()  # Get team ID before committing
        
        # Add the creator as a team member with Leader role
        team_member = TeamMember(
            team_id=team.id,
            user_id=current_user.id,
            role='Leader'
        )
        db.session.add(team_member)
        db.session.commit()
        
        flash(f'Team {team.name} has been created!')
        return redirect(url_for('events.my_teams'))
    
    return render_template('events/create_team.html', form=form)

@events.route('/teams/<int:team_id>')
@login_required
def team_details(team_id):
    team = Team.query.get_or_404(team_id)
    
    # Check if user is a member of this team
    is_member = TeamMember.query.filter_by(team# events.py - Events blueprint (continued)
@events.route('/teams/<int:team_id>')
@login_required
def team_details(team_id):
    team = Team.query.get_or_404(team_id)
    
    # Check if user is a member of this team
    is_member = TeamMember.query.filter_by(team_id=team_id, user_id=current_user.id).first()
    if not is_member and not current_user.is_admin:
        flash('You are not authorized to view this team.')
        return redirect(url_for('events.my_teams'))
    
    # Get all team members
    team_members = TeamMember.query.filter_by(team_id=team_id).all()
    members = []
    
    for member in team_members:
        user = User.query.get(member.user_id)
        if user:
            member_data = {
                'user': user,
                'role': member.role,
                'joined_at': member.joined_at
            }
            members.append(member_data)
    
    # Get team's registrations
    registrations = GroupRegistration.query.filter_by(team_id=team_id).all()
    events_registered = []
    
    for reg in registrations:
        event = Event.query.get(reg.event_id)
        if event:
            reg_data = {
                'event': event,
                'status': reg.status,
                'registered_at': reg.registered_at
            }
            events_registered.append(reg_data)
    
    return render_template('events/team_details.html', 
                           team=team, 
                           members=members, 
                           events_registered=events_registered,
                           is_leader=(team.leader_id == current_user.id))

@events.route('/teams/<int:team_id>/invite', methods=['GET', 'POST'])
@login_required
def invite_member(team_id):
    team = Team.query.get_or_404(team_id)
    
    # Check if user is team leader
    if team.leader_id != current_user.id and not current_user.is_admin:
        flash('Only team leaders can invite members.')
        return redirect(url_for('events.team_details', team_id=team_id))
    
    if request.method == 'POST':
        email = request.form.get('email')
        if email:
            # Find user by email
            user = User.query.filter_by(email=email).first()
            if user:
                # Check if user is already a member
                existing_member = TeamMember.query.filter_by(team_id=team_id, user_id=user.id).first()
                if existing_member:
                    flash(f'{user.username} is already a member of this team.')
                else:
                    # Add user to team
                    team_member = TeamMember(
                        team_id=team_id,
                        user_id=user.id
                    )
                    db.session.add(team_member)
                    db.session.commit()
                    flash(f'{user.username} has been added to the team!')
            else:
                flash(f'No user found with email {email}.')
        else:
            flash('Please enter a valid email address.')
    
    return render_template('events/invite_member.html', team=team)

@events.route('/registrations')
@login_required
def my_registrations():
    # Get individual registrations
    individual_regs = IndividualRegistration.query.filter_by(user_id=current_user.id).all()
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
    
    # Get team registrations
    team_memberships = TeamMember.query.filter_by(user_id=current_user.id).all()
    team_events = []
    
    for membership in team_memberships:
        team = Team.query.get(membership.team_id)
        if team:
            team_regs = GroupRegistration.query.filter_by(team_id=team.id).all()
            for reg in team_regs:
                event = Event.query.get(reg.event_id)
                if event:
                    reg_data = {
                        'event': event,
                        'team': team,
                        'status': reg.status,
                        'registered_at': reg.registered_at
                    }
                    team_events.append(reg_data)
    
    return render_template('events/my_registrations.html',
                           individual_events=individual_events,
                           team_events=team_events)

# Import for team_details route
from .models import User