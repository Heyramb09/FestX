# discussion.py - Discussion blueprint
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length
from .models import Announcement, DiscussionTopic, DiscussionReply, User
from . import db
from datetime import datetime

discussion = Blueprint('discussion', __name__)

# Forms
class TopicForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(1, 100)])
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Post Topic')

class ReplyForm(FlaskForm):
    content = TextAreaField('Reply', validators=[DataRequired()])
    submit = SubmitField('Post Reply')

# Routes
@discussion.route('/discussion')
def index():
    topics = DiscussionTopic.query.order_by(DiscussionTopic.created_at.desc()).all()
    return render_template('discussion/index.html', topics=topics)

@discussion.route('/discussion/announcements')
def announcements():
    announcements_list = Announcement.query.order_by(Announcement.created_at.desc()).all()
    return render_template('discussion/announcements.html', announcements=announcements_list)

@discussion.route('/discussion/create', methods=['GET', 'POST'])
@login_required
def create_topic():
    form = TopicForm()
    
    if form.validate_on_submit():
        topic = DiscussionTopic(
            title=form.title.data,
            content=form.content.data,
            author_id=current_user.id
        )
        db.session.add(topic)
        db.session.commit()
        
        flash('Your topic has been posted!')
        return redirect(url_for('discussion.topic', topic_id=topic.id))
    
    return render_template('discussion/create_topic.html', form=form)

@discussion.route('/discussion/<int:topic_id>', methods=['GET', 'POST'])
def topic(topic_id):
    topic = DiscussionTopic.query.get_or_404(topic_id)
    author = User.query.get(topic.author_id)
    replies = DiscussionReply.query.filter_by(topic_id=topic_id).order_by(DiscussionReply.created_at).all()
    
    # Process replies and fetch authors
    replies_with_authors = []
    for reply in replies:
        reply_author = User.query.get(reply.author_id)
        replies_with_authors.append({
            'reply': reply,
            'author': reply_author
        })
    
    form = ReplyForm()
    
    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash('You must be logged in to reply.')
            return redirect(url_for('auth.login', next=request.path))
        
        reply = DiscussionReply(
            topic_id=topic_id,
            content=form.content.data,
            author_id=current_user.id
        )
        db.session.add(reply)
        db.session.commit()
        
        flash('Your reply has been posted!')
        return redirect(url_for('discussion.topic', topic_id=topic_id))
    
    return render_template('discussion/topic.html', 
                           topic=topic, 
                           author=author, 
                           replies=replies_with_authors, 
                           form=form)

@discussion.route('/discussion/<int:topic_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_topic(topic_id):
    topic = DiscussionTopic.query.get_or_404(topic_id)
    
    # Check if user is the author or an admin
    if topic.author_id != current_user.id and not current_user.is_admin:
        flash('You can only edit your own topics.')
        return redirect(url_for('discussion.topic', topic_id=topic_id))
    
    form = TopicForm(obj=topic)
    
    if form.validate_on_submit():
        topic.title = form.title.data
        topic.content = form.content.data
        topic.updated_at = datetime.utcnow()
        db.session.commit()
        
        flash('Topic has been updated!')
        return redirect(url_for('discussion.topic', topic_id=topic_id))
    
    return render_template('discussion/edit_topic.html', form=form, topic=topic)

@discussion.route('/discussion/reply/<int:reply_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_reply(reply_id):
    reply = DiscussionReply.query.get_or_404(reply_id)
    
    # Check if user is the author or an admin
    if reply.author_id != current_user.id and not current_user.is_admin:
        flash('You can only edit your own replies.')
        return redirect(url_for('discussion.topic', topic_id=reply.topic_id))
    
    form = ReplyForm(obj=reply)
    
    if form.validate_on_submit():
        reply.content = form.content.data
        reply.updated_at = datetime.utcnow()
        db.session.commit()
        
        flash('Reply has been updated!')
        return redirect(url_for('discussion.topic', topic_id=reply.topic_id))
    
    return render_template('discussion/edit_reply.html', form=form, reply=reply)

@discussion.route('/discussion/<int:topic_id>/delete', methods=['POST'])
@login_required
def delete_topic(topic_id):
    topic = DiscussionTopic.query.get_or_404(topic_id)
    
    # Check if user is the author or an admin
    if topic.author_id != current_user.id and not current_user.is_admin:
        flash('You can only delete your own topics.')
        return redirect(url_for('discussion.topic', topic_id=topic_id))
    
    # Delete all replies
    DiscussionReply.query.filter_by(topic_id=topic_id).delete()
    
    db.session.delete(topic)
    db.session.commit()
    
    flash('Topic has been deleted!')
    return redirect(url_for('discussion.index'))

@discussion.route('/discussion/reply/<int:reply_id>/delete', methods=['POST'])
@login_required
def delete_reply(reply_id):
    reply = DiscussionReply.query.get_or_404(reply_id)
    
    # Check if user is the author or an admin
    if reply.author_id != current_user.id and not current_user.is_admin:
        flash('You can only delete your own replies.')
        return redirect(url_for('discussion.topic', topic_id=reply.topic_id))
    
    topic_id = reply.topic_id
    db.session.delete(reply)
    db.session.commit()
    
    flash('Reply has been deleted!')
    return redirect(url_for('discussion.topic', topic_id=topic_id))

@discussion.route('/discussion/my-topics')
@login_required
def my_topics():
    topics = DiscussionTopic.query.filter_by(author_id=current_user.id).order_by(DiscussionTopic.created_at.desc()).all()
    return render_template('discussion/my_topics.html', topics=topics)
