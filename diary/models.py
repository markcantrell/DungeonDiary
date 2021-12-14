from django.db import models
from django.db.models.deletion import CASCADE, SET_NULL
from django.db.models.fields.related import ManyToManyField
from django.http import request 
import re
import bcrypt

class User_manager(models.Manager):
    def registration_validator(self, post_data):
        errors ={}
        if len(post_data['first_name']) == 0:
            errors['first_name'] = "Please enter a first name"
        if len(post_data['last_name']) == 0:
            errors['last_name'] = "Please enter a last name"
        if len(post_data['email']) == 0:
            errors['email'] = "Please enter a email"
        if len(post_data['password']) < 8:
            errors['password'] = "Please enter a password"
        if post_data['password'] != post_data['confirm_password']:
            errors['mismatch'] = "Passwords do not match"
        existingUsers = User.objects.filter(email = post_data['email'])
        if len(existingUsers) > 0:
            errors['unavail'] = "Email is already in use"
        EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
        if not EMAIL_REGEX.match(post_data['email']):
            errors['invalid_email'] = "Please enter a valid email address "
        return errors

    def login_validator(self, post_data):
        errors ={}
        existingUsers = User.objects.filter(email = post_data['email'])
        if len(post_data['email']) == 0:
            errors['email'] = "Please enter a email"
        elif len(existingUsers) < 1:
            errors['no_user'] = "Please enter a valid email and password"
        elif len(post_data['password']) < 8:
            errors['password'] = "Please enter a password"
        elif not bcrypt.checkpw(post_data['password'].encode(), existingUsers[0].password.encode()):
            errors['pw_mismatch'] = "please enter valid email and password"
        return errors

    def update_validator(self, post_data):
        errors ={}
        existingUsers = User.objects.filter(email = post_data['email'])
        if len(post_data['email']) == 0:
            errors['email'] = "Please enter a email"
        elif len(existingUsers) < 1:
            errors['no_user'] = "Please enter a valid email and password"
        if len(post_data['first_name']) == 0:
            errors['first_name'] = "Please enter a first name"
        if len(post_data['last_name']) == 0:
            errors['last_name'] = "Please enter a last name"
        if len(post_data['email']) == 0:
            errors['email'] = "Please enter a email"
        if len(post_data['new_password']) < 8:
            errors['password'] = "Please enter a password"
        if post_data['new_password'] != post_data['confirm_new_password']:
            errors['mismatch'] = "New passwords do not match"
        existingUsers = User.objects.filter(email = post_data['email'])
        if len(existingUsers) < 0:
            errors['unavail'] = "Email is already in use"
        EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
        if not EMAIL_REGEX.match(post_data['email']):
            errors['invalid_email'] = "Please enter a valid email address "
        return errors

class User(models.Model): 
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    password = models.CharField(max_length=15)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    objects = User_manager()

class Group_manager(models.Manager):
    def group_validator(self, post_data):
        errors = {}
        if len(post_data['group_name']) == 0:
            errors['group_name'] = "The group needs a name"
        return errors

class Group(models.Model):
    group_name = models.CharField(max_length=255)
    DM = models.ForeignKey(User, related_name="dungeon_master", null = True, blank = True, on_delete=SET_NULL)
    is_full = models.BooleanField(default = False)
    closed = models.BooleanField( default = False)
    max_members = models.IntegerField()
    members= ManyToManyField(User, related_name= "groups")
    creator = models.ForeignKey(User, related_name="created_groups", null = True, blank = True, on_delete=SET_NULL)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    objects = Group_manager()

class Session_manager(models.Manager):
    def schedule_validator(self, post_data): 
        errors = {}
        if len(post_data['date']) == 0:
            errors['date'] = "What day is the session?"
        if len(post_data['time']) == 0:
            errors['time'] = "When is the session?"
        if len(post_data['schedule_notes'])== 0:
            errors['notes'] = "Provide details for the session"
        current_group = Group.objects.get(id = post_data["group_id"])
        if len(current_group.sessions.all()) != 0: 
            if current_group.sessions.last().archived == False:
                errors['session'] = "Future session already scheduled"
        return errors

    def session_validator(self, post_data): 
        errors = {}
        if len(post_data['date']) == 0:
            errors['date'] = "What day is the session?"
        if len(post_data['time']) == 0:
            errors['time'] = "When is the session?"
        if len(post_data['session_notes'])== 0:
            errors['notes'] = "Session note is required"
        return errors


class Session(models.Model): 
    date = models.DateField()
    time = models.TimeField()
    schedule_notes = models.TextField()
    archived = models.BooleanField(default = False)
    session_notes = models.TextField(null = True, blank = True)
    npcs_met = models.TextField(null = True, blank = True)
    monsters = models.TextField(null = True, blank = True)
    treasure = models.TextField(null = True, blank = True)
    group = models.ForeignKey(Group, related_name="sessions", on_delete=CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    objects = Session_manager()
