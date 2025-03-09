# app/models.py
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login_manager

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(120), unique=True, index=True)
    phone_number = db.Column(db.String(15))
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    individual_registrations = db.relationship('IndividualRegistration', backref='participant', lazy='dynamic')
    team_memberships = db.relationship('TeamMember', backref='user', lazy='dynamic')
    teams_owned = db.relationship('Team', backref='team_leader', lazy='dynamic')
    quiz_attempts = db.relationship('QuizAttempt', backref='user', lazy='dynamic')
    user_answers = db.relationship('UserAnswer', backref='user', lazy='dynamic')
    notifications = db.relationship('Notification', backref='user', lazy='dynamic')
    certificates = db.relationship('Certificate', backref='user', lazy='dynamic')
    
    def __init__(self, username, email, phone_number, password, is_admin=False):
        self.username = username
        self.email = email
        self.phone_number = phone_number
        self.password_hash = generate_password_hash(password)
        self.is_admin = is_admin
    
    def get_id(self):
        return str(self.user_id)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Event(db.Model):
    __tablename__ = 'events'
    
    event_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50))
    event_date = db.Column(db.DateTime)
    registration_deadline = db.Column(db.DateTime)
    venue = db.Column(db.String(100))
    max_participants = db.Column(db.Integer)
    team_event = db.Column(db.Boolean, default=False)
    team_size = db.Column(db.Integer) # If team_event is True, specify team size
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    individual_registrations = db.relationship('IndividualRegistration', backref='event', lazy='dynamic')
    group_registrations = db.relationship('GroupRegistration', backref='event', lazy='dynamic')
    quizzes = db.relationship('Quiz', backref='event', lazy='dynamic')
    results = db.relationship('Result', backref='event', lazy='dynamic')
    
    def __repr__(self):
        return f'<Event {self.title}>'

class Team(db.Model):
    __tablename__ = 'team_table'
    
    team_id = db.Column(db.Integer, primary_key=True)
    team_name = db.Column(db.String(100), nullable=False)
    team_leader_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    members = db.relationship('TeamMember', backref='team', lazy='dynamic')
    group_registrations = db.relationship('GroupRegistration', backref='team', lazy='dynamic')
    
    def __repr__(self):
        return f'<Team {self.team_name}>'

class TeamMember(db.Model):
    __tablename__ = 'team_member_table'
    
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey('team_table.team_id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<TeamMember {self.id}>'

class IndividualRegistration(db.Model):
    __tablename__ = 'individual_registration_table'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    event_id = db.Column(db.Integer, db.ForeignKey('events.event_id'))
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<IndividualRegistration {self.id}>'

class GroupRegistration(db.Model):
    __tablename__ = 'group_registration_table'
    
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey('team_table.team_id'))
    event_id = db.Column(db.Integer, db.ForeignKey('events.event_id'))
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<GroupRegistration {self.id}>'

class Quiz(db.Model):
    __tablename__ = 'quizzes_table'
    
    quiz_id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.event_id'))
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    questions = db.relationship('QuizQuestion', backref='quiz', lazy='dynamic')
    attempts = db.relationship('QuizAttempt', backref='quiz', lazy='dynamic')
    
    def __repr__(self):
        return f'<Quiz {self.title}>'

class QuizQuestion(db.Model):
    __tablename__ = 'quiz_question_table'
    
    question_id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes_table.quiz_id'))
    question_text = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.String(20))  # MCQ, True/False, etc.
    points = db.Column(db.Integer, default=1)
    
    # Relationships
    options = db.relationship('QuizOption', backref='question', lazy='dynamic')
    user_answers = db.relationship('UserAnswer', backref='question', lazy='dynamic')
    
    def __repr__(self):
        return f'<QuizQuestion {self.question_id}>'

class QuizOption(db.Model):
    __tablename__ = 'quiz_option_table'
    
    option_id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('quiz_question_table.question_id'))
    option_text = db.Column(db.Text, nullable=False)
    is_correct = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<QuizOption {self.option_id}>'

class QuizAttempt(db.Model):
    __tablename__ = 'quiz_attempt_table'
    
    attempt_id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes_table.quiz_id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime)
    score = db.Column(db.Integer)
    
    # Relationships
    answers = db.relationship('UserAnswer', backref='attempt', lazy='dynamic')
    
    def __repr__(self):
        return f'<QuizAttempt {self.attempt_id}>'

class UserAnswer(db.Model):
    __tablename__ = 'user_answer_table'
    
    answer_id = db.Column(db.Integer, primary_key=True)
    attempt_id = db.Column(db.Integer, db.ForeignKey('quiz_attempt_table.attempt_id'))
    question_id = db.Column(db.Integer, db.ForeignKey('quiz_question_table.question_id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    answer_text = db.Column(db.Text)
    selected_option_id = db.Column(db.Integer, db.ForeignKey('quiz_option_table.option_id'), nullable=True)
    is_correct = db.Column(db.Boolean)
    
    def __repr__(self):
        return f'<UserAnswer {self.answer_id}>'

class Announcement(db.Model):
    __tablename__ = 'announcement_table'
    
    announcement_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    posted_by = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with User (admin who posted)
    admin = db.relationship('User', foreign_keys=[posted_by])
    
    def __repr__(self):
        return f'<Announcement {self.title}>'

class Notification(db.Model):
    __tablename__ = 'notification_table'
    
    notification_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Notification {self.notification_id}>'

class Certificate(db.Model):
    __tablename__ = 'certificate_table'
    
    certificate_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    event_id = db.Column(db.Integer, db.ForeignKey('events.event_id'))
    certificate_type = db.Column(db.String(50))  # Participation, Winner, etc.
    issue_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with Event
    event = db.relationship('Event', foreign_keys=[event_id])
    
    def __repr__(self):
        return f'<Certificate {self.certificate_id}>'

class Result(db.Model):
    __tablename__ = 'result_table'
    
    result_id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.event_id'))
    participant_type = db.Column(db.String(20))  # Individual or Team
    participant_id = db.Column(db.Integer)  # user_id or team_id
    position = db.Column(db.Integer)
    score = db.Column(db.Float)
    remarks = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Result {self.result_id}>'

# Discussion models
class DiscussionPost(db.Model):
    __tablename__ = 'discussion_posts'
    
    post_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='posts')
    replies = db.relationship('DiscussionReply', backref='post', lazy='dynamic')
    
    def __repr__(self):
        return f'<DiscussionPost {self.title}>'

class DiscussionReply(db.Model):
    __tablename__ = 'discussion_replies'
    
    reply_id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('discussion_posts.post_id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    user = db.relationship('User', backref='replies')
    
    def __repr__(self):
        return f'<DiscussionReply {self.reply_id}>'
