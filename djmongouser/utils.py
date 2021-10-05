from models import User, Session, TemporaryAuthenticator
from DjMongoUserError import DjMongoUserError

def login(request, user:User)->str:
    if request.method != "POST":
        raise DjMongoUserError("Login request must be a POST request!")
    return user.login()

def logout(request):
    # don't fail silently here (unlike default django logout() call)
    pass 

def register(user:User):
    pass 

def send_verify_email(user:User):
    pass 

def handle_email_verificiation_request(request):
    pass 

def send_password_recovery_email(user:User):
    pass 

def handle_password_recovery_request(request):
    pass 





