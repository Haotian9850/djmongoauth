from datetime import datetime, timedelta
import calendar
import secrets
import json

from djongo import models
from djongo.sql2mongo import SQLDecodeError
from ..DjMongoUserError import DjMongoUserError
from django.contrib.auth.hashers import make_password, check_password
from bson.objectid import ObjectId

from ..common.EmailFactory import EmailFactory
from ..common.EmailTypes import EmailTypes
from ..common.EmailUtils import send_email

class TemporaryAuthenticator():
    pass 

class Session():
    pass 

class User():
    pass