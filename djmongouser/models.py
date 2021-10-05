from datetime import datetime, timedelta
import calendar
import secrets

from djongo import models
from DjMongoUserError import DjMongoUserError
from django.contrib.auth.hashers import make_password, check_password

class User(models.Model):
    _id = models.ObjectIdField()
    username = models.CharField(max_length=128, unique=True)
    email = models.EmailField(max_length=128, unique=True)
    password = models.CharField(max_length=128)
    email_verified = models.BooleanField(default=False)
    email_verified_at = models.DateTimeField(default=None)

    def login(self)->str:
        try:
            user = self.objects.get(username=self.username)
        except Exception as e:
            raise DjMongoUserError(str(e))
        if not check_password(self.password, user.password):
            raise DjMongoUserError("Password is incorrect for user {}".format(self.username))
        try:
            existing_sessions = Session.objects.filter(user_id=str(self._id))
            for s in existing_sessions:
                if not s.has_expired():
                    return s.x_auth_token
        except Exception as e:
            raise DjMongoUserError(str(e))
        new_session = Session()
        new_session.user_id = str(user._id)
        new_session.set_expires_at()
        new_session.generate_session_key()
        new_session.generate_x_auth_token()
        new_session.save()
        return new_session.x_auth_token


class TemporaryAuthenticator(models.Model):
    _id = models.ObjectIdField()
    user_id = models.CharField(max_length=128)
    expires_at = models.DateTimeField()
    authenticator = models.CharField(max_length=128, default=None)

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
        self.expires_at = datetime.now() + timedelta(hours=168) # expires in a week
    
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


    