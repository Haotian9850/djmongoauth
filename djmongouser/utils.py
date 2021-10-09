import json 

from django.contrib.auth.hashers import make_password
from models import User, Session, TemporaryAuthenticator
from DjMongoUserError import DjMongoUserError

def login(request)->str:
    if request.method != "POST":
        raise DjMongoUserError("Login request must be a POST request!")
    req_body = json.loads(request.body.decode("UTF-8"))
    try:
        username = req_body["username"]
        password = req_body["password"]
    except Exception as e:
        raise DjMongoUserError("Cannot parse request body: {}".format(str(e)))
    return User.login(username, password)

def logout(request):
    if request.method != "PUT":
        raise DjMongoUserError("Logout request must be a PUT request!")
    User.logout(request)
    
def register(request):
    if request.method != "POST":
        raise DjMongoUserError("Register request must be a POST request!")
    # parse request body
    new_user = User()
    req_body = json.loads(request.body.decode("UTF-8"))
    try:
        new_user.username = req_body["username"]
        new_user.email = req_body["email"]
        new_user.password = make_password(req_body["password"])
    except Exception as e:
        raise DjMongoUserError("Cannot parse request body: {}".format(str(e)))
    new_user.register()


def send_verification_email(request):
    pass 

def handle_email_verificiation_request(request):
    pass 

def send_password_reset_email(request):
    pass 

def handle_password_reset_request(request):
    pass

def send_password_recovery_email(request):
    pass 

def handle_password_recovery_request(request):
    pass 


