from django.http import HttpResponse, JsonResponse
import json 

from djmongoauth.models import User
from djmongoauth.DjMongoAuthError import DjMongoAuthError

def register(request):
    if request.method != "POST":
        return HttpResponse(status=405)    # incorrect request method
    req_body = json.loads(request.body.decode("UTF-8"))
    user = User()
    user.username = req_body["username"]
    user.email = req_body["email"]
    user.password = req_body["password"]
    try:
        user.register()
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
    return HttpResponse(status=201)

def login(request):
    if request.method != "POST":
        return HttpResponse(status=405)
    try:
        req_body = json.loads(request.body.decode("UTF-8"))
        x_auth_token = User.login(req_body["username"], req_body["password"])
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"token": x_auth_token})

def logout(request):
    try:
        User.logout(request)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
    return HttpResponse(status=204)

def send_verify_email(request):
    pass 

def handle_email_verification(requrst):
    pass 

def send_recovery_email(request):
    pass 

def handle_password_recovery(request):
    pass 


