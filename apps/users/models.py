from django.db import models
import bcrypt
import re

r = "(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
def isValidEmail(email):
    if len(email) > 7:
        if re.match(r, email) != None:
            return True

class UserManager(models.Manager):
    def basic_validator(self, ReqSession, ReqPost):
        errors = {}
        if ReqPost['first_name']:
            ReqSession['first_name'] = ReqPost['first_name']
            if len(ReqSession['first_name']) < 2:
                errors['first_name_too_short'] = "First name must be 2 or more characters!"
        else:
            errors['first_name_blank'] = "First name must not be blank!"
        if ReqPost['last_name']:
            ReqSession['last_name'] = ReqPost['last_name']
            if len(ReqSession['last_name']) < 2:
                errors['last_name_too_short'] = "Last name must be 2 or more characters!"
        else:
            errors['last_name_blank'] = "Last name must not be blank!"
        if ReqPost['email']:
            ReqSession['email'] = ReqPost['email']
            if not isValidEmail(ReqSession['email']):
                errors['email_invalid'] = "Email must be valid!"
            elif len(User.objects.filter(email=ReqSession['email'])) > 0:
                errors['email_already_registered'] = "An account with that email already exists!"
        else:
            errors['email_blank'] = "Email must not be blank!"
        if ReqPost['password']:
            if len(ReqPost['password']) < 8:
                errors['password_short'] = "Password must contain at least 8 characters!"
            elif ReqPost['password'].isalpha():
                errors['password_all_letters'] = "Password must contain at least one non-letter character!"
            elif ReqPost['password'] == ReqPost['password'].lower():
                errors['password_all_lowercase'] = "Password must contain at least one uppercase letter!"
            else:
                hash1 = bcrypt.hashpw(ReqPost['password'].encode(), bcrypt.gensalt())
                if (ReqPost['password_confirm']):
                    if not bcrypt.checkpw(ReqPost['password_confirm'].encode(), hash1):
                        errors['password_mismatch'] = "Password and password confirmation must match!"
                else:
                    errors['password_confirm_blank'] = "Password confirmation must not be blank!"
        else:
            errors['password_blank'] = "Password must not be blank!"
        return errors
    def register_new_user(self, ReqSession, ReqPost):
        try:
            hash1 = bcrypt.hashpw(ReqPost['password'].encode(), bcrypt.gensalt())
            u = User(first_name = ReqSession['first_name'], last_name = ReqSession['last_name'], email=ReqSession['email'], pwhash = hash1)
            u.save()
            print ("No errors!")
            ReqSession.clear()
            ReqSession['id'] = u.id
            return True
        except:
            print ("Something went wrong. Please try registering again.")
            return False
    def validate_login(self, ReqSession, ReqPost):
        try:
            ReqSession['e_email'] = ReqPost['e_email']
            if len(User.objects.filter(email = ReqSession['e_email'])) > 0:
                user = User.objects.get(email = ReqSession['e_email'])
                if ReqPost['e_password']:
                    if bcrypt.checkpw(ReqPost['e_password'].encode(), user.pwhash.encode()):
                        ReqSession.clear()
                        ReqSession['id'] = user.id
                        return user
                return False
            else:
                return False
        except:
            print("Something went wrong. Please try logging in again.")
            return False

class User(models.Model):
    first_name = models.CharField(max_length = 255)
    last_name = models.CharField(max_length = 255)
    email = models.CharField(max_length = 255)
    pwhash = models.CharField(max_length = 255)
    objects = UserManager()
    