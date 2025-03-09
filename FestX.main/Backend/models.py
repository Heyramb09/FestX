# models.py - Database models
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from . import db

# User model
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(120), unique=True, index=True)
    phone = db.Column(db.String(20))
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    individual_registrations = db.relationship('IndividualRegistration', backref='participant', lazy='dynamic')
    team_members = db.relationship('TeamMember', backref='user', lazy='dynamic')
    announcements = db.relationship('Announcement', backref='author', lazy='dynamic')
    notifications = db.relationship('Notification', backref='recipient', lazy='dynamic')
    certificates = db.relationship('Certificate', backref='user', lazy='dynamic')
    results = db.relationship('Result', backref='user', lazy='dynamic')
    quiz_attempts = db.relationship('QuizAttempt', backref='user', lazy='dynamic')
    user_answers = db.relationship('UserAnswer', backref='user', lazy='dynamic')
    
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

# Event model
class Event(db.Model):
    __tablename__ = 'events'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50))
    venue = db.Column(db.String(100))
    date = db.Column(db.DateTime)
    registration_deadline = db.Column(db.DateTime)
    max_participants = db.Column(db.Integer)
    is_team_event = db.Column(db.Boolean, default=False)
    min_team_size = db.Column(db.Integer, default=1)
    max_team_size = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    individual_registrations = db.relationship('IndividualRegistration', backref='event', lazy='dynamic')
    group_registrations = db.relationship('GroupRegistration', backref='event', lazy='dynamic')
    quizzes = db.relationship('Quiz', backref='event', lazy='dynamic')
    results = db.relationship('Result', backref='event', lazy='dynamic')
    
    def __repr__(self):
        return f'<Event {self.name}>'

# Team model
class Team(db.Model):
    __tablename__ = 'team_table'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    leader_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    members = db.relationship('TeamMember', backref='team', lazy='dynamic')
    group_registrations = db.relationship('GroupRegistration', backref='team', lazy='dynamic')
    
    @property
    def leader(self):
        return User.query.get(self.leader_id)
    
    def __repr__(self):
        return f'<Team {self.name}>'

# TeamMember model
class TeamMember(db.Model):
    __tablename__ = 'team_member_table'
    
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey('team_table.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    role = db.Column(db.String(50), default='Member')
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<TeamMember {self.user_id} in Team {self.team_id}>'

# IndividualRegistration model
class IndividualRegistration(db.Model):
    __tablename__ = 'individual_registration_table'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'))
    status = db.Column(db.String(20), default='Registered')  # Registered, Confirmed, Cancelled
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<IndividualRegistration {self.id}>'

# GroupRegistration model
class GroupRegistration(db.Model):
    __tablename__ = 'group_registration_table'
    
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey('team_table.id'))
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'))
    status = db.Column(db.String(20), default='Registered')  # Registered, Confirmed, Cancelled
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<GroupRegistration {self.id}>'

# Quiz models
class Quiz(db.Model):
    __tablename__ = 'quizzes_table'
    
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'))
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    duration_minutes = db.Column(db.Integer)
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
    
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes_table.id'))
    question_text = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.String(20), default='MCQ')  # MCQ, TrueFalse, ShortAnswer
    points = db.Column(db.Integer, default=1)
    
    # Relationships
    options = db.relationship('QuizOption', backref='question', lazy='dynamic')
    user_answers = db.relationship('UserAnswer', backref='question', lazy='dynamic')
    
    def __repr__(self):
        return f'<QuizQuestion {self.id}>'

class QuizOption(db.Model):
    __tablename__ = 'quiz_option_table'
    
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('quiz_question_table.id'))
    option_text = db.Column(db.Text, nullable=False)
    is_correct = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<QuizOption {self.id}>'

class QuizAttempt(db.Model):
    __tablename__ = 'quiz_attempt_table'
    
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes_table.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    finished_at = db.Column(db.DateTime)
    score = db.Column(db.Integer)
    
    # Relationships
    answers = db.relationship('UserAnswer', backref='attempt', lazy='dynamic')
    
    def __repr__(self):
        return f'<QuizAttempt {self.id}>'

class UserAnswer(db.Model):
    __tablename__ = 'user_answer_table'
    
    id = db.Column(db.Integer, primary_key=True)
    attempt_id = db.Column(db.Integer, db.ForeignKey('quiz_attempt_table.id'))
    question_id = db.Column(db.Integer, db.ForeignKey('quiz_question_table.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    selected_option_id = db.Column(db.Integer, db.ForeignKey('quiz_option_table.id'), nullable=True)
    text_answer = db.Column(db.Text, nullable=True)
    is_correct = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<UserAnswer {self.id}>'

# Announcement model
class Announcement(db.Model):
    __tablename__ = 'announcement_table'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    is_pinned = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Announcement {self.title}>'

# Notification model
class Notification(db.Model):
    __tablename__ = 'notification_table'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    title = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Notification {self.id}>'

# Certificate model
class Certificate(db.Model):
    __tablename__ = 'certificate_table'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'))
    certificate_type = db.Column(db.String(50))  # Participation, Winner, Runner-up
    issue_date = db.Column(db.DateTime, default=datetime.utcnow)
    certificate_url = db.Column(db.String(255))
    
    def __repr__(self):
        return f'<Certificate {self.id}>'

# Result model
class Result(db.Model):
    __tablename__ = 'result_table'
    
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    team_id = db.Column(db.Integer, db.ForeignKey('team_table.id'), nullable=True)
    position = db.Column(db.Integer)  # 1 for winner, 2 for runner-up, etc.
    score = db.Column(db.Float, nullable=True)
    remarks = db.Column(db.Text, nullable=True)
    announced_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Result {self.id}>'

# Discussion models
class DiscussionTopic(db.Model):
    __tablename__ = 'discussion_topics'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    replies = db.relationship('DiscussionReply', backref='topic', lazy='dynamic')
    
    def __repr__(self):
        return f'<DiscussionTopic {self.title}>'

class DiscussionReply(db.Model):
    __tablename__ = 'discussion_replies'
    
    id = db.Column(db.Integer, primary_key=True)
    topic_id = db.Column(db.Integer, db.ForeignKey('discussion_topics.id'))
    content = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @property
    def author(self):
        return User.query.get(self.author_id)
    
    def __repr__(self):
        return f'<DiscussionReply {self.id}>'

# FAQ model
class FAQ(db.Model):
    __tablename__ = 'faqs'
    
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(255), nullable=False)
    answer = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=True)
    is_published = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<FAQ {self.id}>'

# Contact query model
class ContactQuery(db.Model):
    __tablename__ = 'contact_queries'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_resolved = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime, nullable=True)
    
    def __repr__(self):
        return f'<ContactQuery {self.id}>'
