#!/usr/bin/python
from flask_wtf import FlaskForm, csrf
from wtforms import StringField, TextAreaField, PasswordField, BooleanField, SubmitField, HiddenField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length
from app.models import User

class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Please use a different username.')

class PostForm(FlaskForm):
    post = TextAreaField('Say something', validators=[
        DataRequired(), Length(min=1, max=2000)])
    submit = SubmitField('Submit')

class ReplaySearchForm(FlaskForm):
    # query  = TextAreaField('Search', validators=[DataRequired(), Length(min=1, max=2000)])
    query  = StringField('Search', id="s-query", render_kw={"placeholder": "Search Replays"})
    p1char = HiddenField("P1",     id="s-p1-char", default=-1)
    p2char = HiddenField("P2",     id="s-p2-char", default=-1)
    stage  = HiddenField("Stage",  id="s-stage",   default=-1)
    sort   = HiddenField("Sort",   id="s-sort",    default="played")
    submit = SubmitField('Search', id="s-submit")
