from datetime import datetime, timedelta
import calendar
import secrets
import json

from django.conf import settings
from djongo import models
from djongo.sql2mongo import SQLDecodeError
from django.contrib.auth.hashers import make_password, check_password
from bson.objectid import ObjectId

from .DjMongoAuthError import DjMongoAuthError
from .common.EmailFactory import EmailFactory
from .common.EmailTypes import EmailTypes
from .common.EmailUtils import send_email

class TemporaryAuthenticator(models.Model):
    _id = models.ObjectIdField()
    user_id = models.CharField(max_length=128)
    expires_at = models.DateTimeField()
    authenticator = models.CharField(max_length=128, default=None)

    def generate_authenticator(self):
        self.authenticator = secrets.token_urlsafe(64)

    # TODO use custom django setting value
    def set_expires_at(self):
        self.expires_at = datetime.now() + timedelta(hours=1)

    def has_expired(self)->bool:
        expires_at_ntz = self.expires_at.replace(tzinfo=None)
        return expires_at_ntz < datetime.now()

class Session(models.Model):
    _id = models.ObjectIdField()
    session_key = models.CharField(max_length=255, unique=True)
    user_id = models.CharField(max_length=128)
    expires_at = models.DateTimeField()
    x_auth_token = models.CharField(max_length=1024, unique=True)

    def has_expired(self)->bool:
        # both datetime.now() and self.expires_at are in UTC, so removing tz awareness from self.expires_at
        expires_at_ntz = self.expires_at.replace(tzinfo=None)
        return expires_at_ntz < datetime.now()
    
    def set_expires_at(self):
        self.expires_at = datetime.now() + timedelta(hours=settings.SESSION_EXPIRE_IN_HOUR) # expires in a week
    
    def generate_x_auth_token(self, username:str):
        assert self.session_key
        assert self.user_id
        assert self.expires_at
        self.x_auth_token = "exp={}&user_id={}&username={}&session_key={}".format(
            calendar.timegm(self.expires_at.utctimetuple()),
            self.user_id,
            username,
            self.session_key
        )

    def generate_session_key(self):
        self.session_key = secrets.token_urlsafe(128)
    
    @staticmethod
    def parse_x_auth_token(x_auth_token:str)->tuple:
        tokens = x_auth_token.split("&")
        if len(tokens) < 3:
            raise DjMongoAuthError("Failed to parse x_auth_token: {}".format(x_auth_token))
        return (
            tokens[0].split("=")[1],
            tokens[1].split("=")[1],
            tokens[2].split("=")[1],
            tokens[3].split("=")[1]
        )

class User(models.Model):
    _id = models.ObjectIdField()
    username = models.CharField(max_length=128, unique=True)
    email = models.EmailField(max_length=128, unique=True)
    password = models.CharField(max_length=128)
    email_verified = models.BooleanField(default=False)
    email_verified_at = models.DateTimeField(default=None)

    def register(self):
        try:
            self.password = make_password(self.password)
            self.save()
        except SQLDecodeError as e:
            raise DjMongoAuthError("Username or email has already been registered")

    @staticmethod
    def login(username, password)->str:
        try:
            user = User.objects.get(username=username)
        except Exception as e:
            raise DjMongoAuthError(str(e))
        if not check_password(password, user.password):
            raise DjMongoAuthError("Password is incorrect for user {}".format(username))
        try:
            existing_sessions = Session.objects.filter(user_id=str(user._id))
            for s in existing_sessions:
                if not s.has_expired():
                    return s.x_auth_token
        except Exception as e:
            raise DjMongoAuthError(str(e))
        new_session = Session()
        new_session.user_id = str(user._id)
        new_session.set_expires_at()
        new_session.generate_session_key()
        new_session.generate_x_auth_token(username=username)
        new_session.save()
        return new_session.x_auth_token

    @staticmethod
    def logout(request):
        # don't fail silently here (unlike default django logout() call)
        x_auth_token = request.META.get("HTTP_AUTHORIZATION")
        if not x_auth_token:
            raise DjMongoAuthError("No token found in request header!")
        exp, user_id, _, session_key = Session.parse_x_auth_token(x_auth_token)
        if calendar.timegm(datetime.now().utctimetuple()) > int(exp):
            raise DjMongoAuthError("Unable to log out since token has already expired")
        has_valid_session = False 
        existing_sessions = Session.objects.filter(user_id=user_id)
        if len(existing_sessions):
            for s in existing_sessions:
                if not s.has_expired() and s.session_key == session_key:
                    has_valid_session = True 
                    break
        if not has_valid_session:
            raise DjMongoAuthError("Session key not found!")
        # delete all sessions
        existing_sessions.delete()

    @staticmethod
    def send_email(request, type:EmailTypes):
        user_id = Session.parse_x_auth_token(request.META["HTTP_AUTHORIZATION"])[1]
        user = None 
        try:
            user = User.objects.get(_id=ObjectId(user_id))
        except Exception:
            raise DjMongoAuthError("User not found!")
        temp_auth = TemporaryAuthenticator()
        temp_auth.user_id = user_id
        temp_auth.generate_authenticator()
        temp_auth.set_expires_at()
        temp_auth.save()
        try:
            mail_to_be_sent = None 
            if type == EmailTypes.VERIFY:
                mail_to_be_sent = EmailFactory.generate_email(type=EmailTypes.VERIFY, temp_auth=temp_auth, user=user)
            elif type == EmailTypes.RESET:
                mail_to_be_sent = EmailFactory.generate_email(type=EmailTypes.RESET, temp_auth=temp_auth, user=user)
            assert mail_to_be_sent
            send_email(mail_to_be_sent)
        except Exception as e:
            if type == EmailTypes.VERIFY:
                raise DjMongoAuthError("Failed to send verification email: {}".format(str(e)))
            elif type == EmailTypes.RESET:
                raise DjMongoAuthError("Failed to send password reset email: {}".format(str(e)))

    @staticmethod
    def handle_email_request(request, type:EmailTypes):
        try:
            authenticator = request.GET.get("a", None)
            assert authenticator
            temp_auth = TemporaryAuthenticator.objects.get(authenticator=authenticator)
            if temp_auth.has_expired():
                raise DjMongoAuthError("Invalid session!")
            user = User.objects.get(_id=ObjectId(temp_auth.user_id))
            if type == EmailTypes.VERIFY:
                user.email_verified = True 
                user.email_verified_at = datetime.now()
                user.save()
            elif type == EmailTypes.RESET:
                req_body = json.loads(request.body.decode("UTF-8"))
                user.password = make_password(req_body["new_password"])
                user.save()
                # clear all existing sessions
                Session.objects.filter(user_id=str(user._id)).delete()
            temp_auth.delete()
        except Exception as e:
            raise DjMongoAuthError("Cannot process email verification request: {}".format(str(e))) 




    